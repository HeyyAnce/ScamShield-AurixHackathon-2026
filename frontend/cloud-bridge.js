/* Streamlit component transport. The standalone FastAPI frontend does not load this. */
(() => {
  if (window.parent === window) return;
  const pending = new Map();
  const nativeFetch = window.fetch.bind(window);
  const origin = document.referrer ? new URL(document.referrer).origin : location.origin;
  const send = (type, data) => window.parent.postMessage({isStreamlitMessage:true,type,...data}, origin);
  window.addEventListener('message', event => {
    if (event.source !== window.parent || event.origin !== origin || event.data?.type !== 'streamlit:render') return;
    const response = event.data.args?.response;
    if (!response || !pending.has(response.id)) return;
    const resolve = pending.get(response.id);
    pending.delete(response.id);
    resolve(new Response(JSON.stringify(response.body), {status:response.status,headers:{'Content-Type':'application/json'}}));
  });
  window.fetch = async (input, options = {}) => {
    if (typeof input !== 'string' || !['/api/analyze','/api/extract'].includes(input)) return nativeFetch(input, options);
    const id = crypto.randomUUID();
    let payload;
    if (input === '/api/extract') {
      payload = await new Promise((resolve,reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(String(reader.result).split(',')[1]);
        reader.onerror = reject;
        reader.readAsDataURL(options.body);
      });
    } else payload = JSON.parse(options.body);
    if (options.signal?.aborted) throw new DOMException('Aborted','AbortError');
    return new Promise((resolve,reject) => {
      const abort = () => { pending.delete(id); reject(new DOMException('Aborted','AbortError')); };
      options.signal?.addEventListener('abort',abort,{once:true});
      pending.set(id, response => {options.signal?.removeEventListener('abort',abort);resolve(response);});
      send('streamlit:setComponentValue',{value:{id,path:input,payload},dataType:'json'});
    });
  };
  let lastHeight = 0;
  function resize() {
    const height = Math.ceil(document.body.getBoundingClientRect().height) + 4;
    if (height !== lastHeight) {lastHeight=height;send('streamlit:setFrameHeight',{height});}
  }
  send('streamlit:componentReady',{apiVersion:1});
  new ResizeObserver(resize).observe(document.body);
  resize();
})();
