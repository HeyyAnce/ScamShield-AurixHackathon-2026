/* Interface translations only. Never translate or replace user-entered text. */
window.ShieldI18n = (() => {
  const hi = {
    'Home':'होम', 'Safety Guide':'सुरक्षा गाइड', 'Help':'मदद', 'About':'हमारे बारे में',
    'Skip to content':'मुख्य सामग्री पर जाएँ', 'Main navigation':'मुख्य नेविगेशन',
    'Switch color theme':'रंग थीम बदलें', 'Give feedback ↗':'सुझाव दें ↗', '✎   Feedback':'✎   सुझाव',
    'Privacy':'गोपनीयता', 'Help & contact':'मदद और संपर्क', 'BUILT BY IDEAFORGE':'IDEAFORGE द्वारा बनाया गया',
    'A little pause. A safer decision.':'थोड़ा ठहरें। सुरक्षित फैसला लें।',
    'Before you trust it,':'भरोसा करने से पहले,', 'take a second.':'एक पल ठहरें।',
    'A message feels wrong? Let’s look closer.':'संदेश संदिग्ध लगता है? आइए जाँचें।',
    'Spot the warning signs and find a safer next step.':'खतरे के संकेत पहचानें और अगला कदम सोच-समझकर लें।',
    'English · Hindi · Hinglish':'अंग्रेज़ी · हिंदी · हिंग्लिश', 'Built for everyday India':'भारत के रोज़मर्रा के उपयोग के लिए',
    'Unknown sender · just now':'अनजान व्यक्ति · अभी', 'Your account will be blocked.':'आपका खाता बंद हो जाएगा।',
    'Update your KYC immediately.':'अपना KYC तुरंत अपडेट करें।',
    '↳ Urgency is a reason to pause.':'↳ जल्दबाज़ी कराएँ, तो ज़रूर ठहरें।',
    'ILLUSTRATIVE MESSAGE · NOT AN ANALYSIS':'सिर्फ उदाहरण · जाँच का नतीजा नहीं',
    'Message checker':'संदेश जाँच', 'YOUR SECOND OPINION':'आपकी मदद के लिए दूसरी राय', '01 / CHECK':'01 / जाँच',
    'What did you receive?':'आपको क्या संदेश मिला?', 'Input type':'इनपुट का प्रकार',
    'Paste a message':'संदेश पेस्ट करें', 'Upload screenshot':'स्क्रीनशॉट अपलोड करें', 'BETA':'बीटा',
    'Choose a screenshot':'स्क्रीनशॉट चुनें', 'Choose screenshot':'स्क्रीनशॉट चुनें',
    'PNG, JPEG or WebP · up to 5 MB':'PNG, JPEG या WebP · अधिकतम 5 MB', 'Selected screenshot':'चुना गया स्क्रीनशॉट',
    'Extract text':'टेक्स्ट निकालें',
    'The image is sent to Gemini for text extraction. Check the extracted text before analyzing.':'टेक्स्ट निकालने के लिए तस्वीर Gemini को भेजी जाती है। जाँच से पहले निकाला गया टेक्स्ट पढ़ लें।',
    'Read and correct the extracted text before checking.':'जाँचने से पहले निकाले गए टेक्स्ट को पढ़कर ठीक कर लें।',
    'Message text':'संदेश का टेक्स्ट',
    'Paste the SMS, WhatsApp message or email that made you pause…':'वह SMS, WhatsApp संदेश या ईमेल यहाँ पेस्ट करें जिस पर आपको शक है…',
    'Remove names, account details and personal information. Text is sent to Gemini when AI is available.':'नाम, खाते की जानकारी और निजी विवरण हटा दें। AI उपलब्ध होने पर टेक्स्ट Gemini को भेजा जाता है।',
    'Your privacy ↗':'आपकी गोपनीयता ↗', 'Check this message':'संदेश जाँचें',
    'Try example messages:':'उदाहरण संदेश आज़माएँ:', 'KYC alert':'KYC चेतावनी', 'Prize money':'इनाम का संदेश', 'Bank reminder':'बैंक का रिमाइंडर',
    'A helpful second opinion. Never a guarantee.':'मददगार दूसरी राय। कोई गारंटी नहीं।',
    'Already sent money or shared details?':'पैसे भेज दिए या जानकारी साझा कर दी?',
    'Act quickly. There are steps you can take now.':'जल्दी कार्रवाई करें। जानें कि अब क्या करना है।',
    'Find your next step ↗':'अगला कदम जानें ↗',
    'We look for warning signs in the message. We cannot verify the sender or guarantee that a message is safe.':'हम संदेश में खतरे के संकेत देखते हैं। हम भेजने वाले की पहचान या संदेश के सुरक्षित होने की गारंटी नहीं दे सकते।',
    'Get to know Scam Shield ↗':'Scam Shield के बारे में जानें ↗',
    'Make the next version better.':'अगला संस्करण बेहतर बनाने में मदद करें।',
    'Tell us what worked, what didn’t, or what felt missing. Please leave out private messages and personal details.':'बताएँ क्या अच्छा लगा, क्या नहीं चला और क्या कमी लगी। निजी संदेश या व्यक्तिगत जानकारी न लिखें।',
    'Close feedback':'सुझाव फ़ॉर्म बंद करें', 'What is this about?':'यह किस बारे में है?',
    'Design & ease of use':'डिज़ाइन और इस्तेमाल में आसानी', 'A result seems wrong':'नतीजा गलत लगता है',
    'Something is broken':'कुछ काम नहीं कर रहा', 'An idea':'एक सुझाव', 'Your feedback':'आपका सुझाव', 'I was trying to…':'मैं यह करने की कोशिश कर रहा था…',
    'This downloads a draft. Nothing is sent to the team.':'इससे ड्राफ़्ट डाउनलोड होगा। टीम को कुछ नहीं भेजा जाएगा।',
    'Download feedback draft':'सुझाव का ड्राफ़्ट डाउनलोड करें',
    'Draft downloaded. Share the file with the team when you are ready.':'ड्राफ़्ट डाउनलोड हो गया। तैयार होने पर फ़ाइल टीम के साथ साझा करें।',
    'Safety guide':'सुरक्षा गाइड', 'Small habits.':'छोटी आदतें।', 'Stronger protection.':'बेहतर सुरक्षा।',
    'You don’t need to be a tech expert. Start with a pause, a few checks, and the confidence to say no.':'टेक्नोलॉजी के विशेषज्ञ होने की ज़रूरत नहीं। थोड़ा ठहरें, कुछ बातें जाँचें और ज़रूरत पड़ने पर मना करें।',
    'Guide topics':'गाइड के विषय', 'Before you respond':'जवाब देने से पहले', 'Protect your details':'अपनी जानकारी सुरक्षित रखें',
    'Recognize the pressure':'दबाव पहचानें', 'If you already acted':'अगर आपने कार्रवाई कर दी है',
    '01 / PAUSE & VERIFY':'01 / ठहरें और पुष्टि करें', 'Take the conversation somewhere you trust.':'भरोसेमंद माध्यम से पुष्टि करें।',
    'Stop before clicking, paying or replying. A deadline in a message does not make it trustworthy.':'क्लिक करने, पैसे देने या जवाब देने से पहले रुकें। संदेश में समय-सीमा लिखी होने से वह भरोसेमंद नहीं हो जाता।',
    'Open your bank or service’s official app yourself. Don’t use the link or number in the suspicious message.':'बैंक या सेवा का आधिकारिक ऐप खुद खोलें। संदिग्ध संदेश का लिंक या नंबर इस्तेमाल न करें।',
    'If someone you know asks for money, call them on a number you already have.':'कोई जान-पहचान वाला पैसे माँगे, तो अपने पास पहले से मौजूद नंबर पर उसे कॉल करें।',
    '02 / KEEP CONTROL':'02 / नियंत्रण अपने पास रखें', 'Your codes are yours alone.':'आपके सुरक्षा कोड सिर्फ आपके हैं।',
    'Never share an OTP, password, card PIN, CVV or UPI PIN with someone who calls or messages you.':'कॉल या संदेश करने वाले किसी व्यक्ति से OTP, पासवर्ड, कार्ड PIN, CVV या UPI PIN साझा न करें।',
    'Don’t install an APK or a remote-access app because a stranger says it is required for a refund or support.':'किसी अनजान व्यक्ति के कहने पर रिफ़ंड या मदद के लिए APK या रिमोट-ऐक्सेस ऐप इंस्टॉल न करें।',
    'Use different passwords for important accounts and turn on two-step verification where available.':'ज़रूरी खातों के लिए अलग पासवर्ड रखें और जहाँ उपलब्ध हो, दो-चरण वाला सत्यापन चालू करें।',
    '03 / NOTICE THE TACTICS':'03 / चाल पहचानें', 'Pressure is part of the trick.':'दबाव बनाना भी धोखे की चाल है।',
    '“Pay now.” “Keep this secret.” “Your account will close.” “You won a prize, but first pay a fee.” These are reasons to stop and verify independently.':'“अभी पैसे दो।” “यह राज़ रखना।” “आपका खाता बंद होगा।” “इनाम जीता है, पहले शुल्क दो।” ऐसी बातें सुनकर रुकें और स्वतंत्र रूप से पुष्टि करें।',
    'A familiar logo, official-sounding name or polished message is not proof. Scam Shield can help you examine the wording; it cannot authenticate the sender.':'पहचाना हुआ लोगो, आधिकारिक लगने वाला नाम या अच्छा लिखा संदेश सबूत नहीं है। Scam Shield शब्दों की जाँच में मदद करता है; भेजने वाले की पहचान सत्यापित नहीं करता।',
    '04 / ACT QUICKLY':'04 / जल्दी कार्रवाई करें', 'Sent money? Contact your bank immediately.':'पैसे भेज दिए? तुरंत अपने बैंक से संपर्क करें।',
    'Use its official app, website or the number on your card. Ask about blocking affected payment access and reporting the transaction.':'आधिकारिक ऐप, वेबसाइट या कार्ड पर दिया नंबर इस्तेमाल करें। प्रभावित भुगतान सुविधा बंद करने और लेनदेन की शिकायत करने के बारे में पूछें।',
    'For financial cyber fraud in India, call':'भारत में आर्थिक साइबर धोखाधड़ी की शिकायत के लिए कॉल करें', 'or report at':'या यहाँ रिपोर्ट करें',
    'Save screenshots, transaction IDs, phone numbers and the timeline. Don’t delete evidence.':'स्क्रीनशॉट, लेनदेन ID, फ़ोन नंबर और घटनाओं का समय सुरक्षित रखें। सबूत न मिटाएँ।',
    'If you shared a password, change it from a trusted device and review active sessions.':'पासवर्ड साझा कर दिया है, तो भरोसेमंद डिवाइस से बदलें और सक्रिय लॉगिन जाँचें।',
    'Don’t pay anyone promising a guaranteed recovery. Reporting promptly may help, but recovery is not guaranteed.':'पैसे वापस दिलाने की गारंटी देने वालों को भुगतान न करें। तुरंत रिपोर्ट करने से मदद मिल सकती है, लेकिन पैसे वापस मिलने की गारंटी नहीं है।',
    'Official guidance:':'आधिकारिक मार्गदर्शन:', 'SBI cyber security':'SBI साइबर सुरक्षा', 'National Cyber Crime Reporting Portal':'राष्ट्रीय साइबर अपराध रिपोर्टिंग पोर्टल',
    'No silly questions.':'हर सवाल ज़रूरी है।', 'Just clearer answers.':'पाएँ आसान जवाब।',
    'Understand your result, get unstuck, or help us make this better.':'नतीजा समझें, परेशानी दूर करें या इसे बेहतर बनाने में मदद करें।',
    'Frequently asked questions':'अक्सर पूछे जाने वाले सवाल', 'Find an answer':'जवाब खोजें', 'Try “screenshot” or “safe”…':'“स्क्रीनशॉट” या “सुरक्षित” खोजें…',
    'Does “safe” mean I can trust the sender?':'क्या “सुरक्षित” का मतलब है कि भेजने वाले पर भरोसा कर सकता हूँ?',
    'No. It means the text did not show strong scam signals. Verify unexpected requests through an official channel before taking action.':'नहीं। इसका मतलब है कि टेक्स्ट में धोखे के मज़बूत संकेत नहीं मिले। कार्रवाई से पहले अनपेक्षित अनुरोध की आधिकारिक माध्यम से पुष्टि करें।',
    'Which languages can I check?':'मैं किन भाषाओं में जाँच सकता हूँ?',
    'Submit English, Hindi or Hinglish messages. Use the language switch for English or Hindi interface and AI explanations. Offline explanations may remain in English.':'अंग्रेज़ी, हिंदी या हिंग्लिश संदेश जाँचें। भाषा बटन से इंटरफ़ेस और AI की व्याख्या के लिए अंग्रेज़ी या हिंदी चुनें। ऑफ़लाइन व्याख्या अंग्रेज़ी में रह सकती है।',
    'Can I upload a screenshot?':'क्या मैं स्क्रीनशॉट अपलोड कर सकता हूँ?',
    'Yes. Choose a clear PNG, JPEG or WebP image up to 5 MB. Extraction is experimental: review and correct the text before checking it, especially Hindi text.':'हाँ। अधिकतम 5 MB की साफ़ PNG, JPEG या WebP तस्वीर चुनें। टेक्स्ट निकालने की सुविधा प्रयोगात्मक है: जाँच से पहले टेक्स्ट पढ़कर ठीक करें, खासकर हिंदी में।',
    'What if the AI is unavailable?':'AI उपलब्ध न हो तो क्या होगा?',
    'The checker can use warning-sign rules and available reference examples. The result tells you which checks were used. A fallback result has limitations too.':'जाँच के लिए खतरे के नियम और उपलब्ध उदाहरण इस्तेमाल हो सकते हैं। नतीजे में बताया जाएगा कि कौन-सी जाँच हुई। इस तरीके की भी सीमाएँ हैं।',
    'Why did the result get something wrong?':'नतीजे में गलती क्यों हुई?',
    'Language and context are complicated. Both AI and rules can make mistakes. Treat every result as a second opinion, and verify important decisions independently.':'भाषा और संदर्भ जटिल हो सकते हैं। AI और नियम दोनों गलती कर सकते हैं। नतीजे को दूसरी राय मानें और ज़रूरी निर्णय से पहले स्वतंत्र पुष्टि करें।',
    'Can you recover money or file a report for me?':'क्या आप पैसे वापस दिला सकते हैं या मेरी रिपोर्ट दर्ज कर सकते हैं?',
    'No. Scam Shield does not recover money or submit official complaints. See the Safety Guide for the next steps and official reporting channels.':'नहीं। Scam Shield पैसे वापस नहीं दिलाता और आधिकारिक शिकायत दर्ज नहीं करता। अगले कदम और शिकायत के आधिकारिक माध्यम सुरक्षा गाइड में देखें।',
    'No matching answer. Try a different word.':'जवाब नहीं मिला। कोई दूसरा शब्द खोजें।', 'A work in progress, together':'मिलकर बेहतर बनाएँ', 'Your experience matters.':'आपका अनुभव मायने रखता है।',
    'Something confusing? A result that missed the mark? Tell us what you expected and what happened.':'कुछ समझ नहीं आया या नतीजा गलत लगा? बताएँ कि आपको क्या उम्मीद थी और क्या हुआ।',
    'Write feedback':'सुझाव लिखें',
    'Download a feedback draft to share with the team. An online feedback inbox is not connected yet.':'टीम के साथ साझा करने के लिए सुझाव का ड्राफ़्ट डाउनलोड करें। ऑनलाइन सुझाव भेजने की सुविधा अभी जुड़ी नहीं है।',
    'Visit the project on GitHub ↗':'GitHub पर प्रोजेक्ट देखें ↗',
    'About Scam Shield':'Scam Shield के बारे में', 'Technology that helps':'ऐसी तकनीक जो मदद करे', 'you think twice.':'सोच-समझकर फैसला लेने में।',
    'Built by Team IDEAFORGE for people navigating everyday messages, urgent demands and uncertain links.':'रोज़ के संदेशों, जल्दबाज़ी वाले अनुरोधों और अनजान लिंक को समझने में मदद के लिए Team IDEAFORGE ने बनाया।',
    'A calmer moment':'थोड़ा सुकून', 'in a noisy inbox.':'संदेशों की भीड़ में।',
    'Scams often ask us to act before we think. Scam Shield creates space to pause: paste a message, see the warning signs and consider a safer next step.':'धोखेबाज़ अक्सर सोचने से पहले कार्रवाई करवाना चाहते हैं। Scam Shield ठहरने का मौका देता है: संदेश पेस्ट करें, खतरे के संकेत देखें और सुरक्षित अगला कदम सोचें।',
    'Our prototype combines AI analysis, warning-sign rules and reference examples. The reference collection includes synthetic messages; it is not a verified record of real incidents or proof of accuracy.':'हमारा प्रोटोटाइप AI विश्लेषण, खतरे के नियम और संदर्भ उदाहरण इस्तेमाल करता है। संग्रह में बनाए गए उदाहरण भी हैं; यह असली घटनाओं का सत्यापित रिकॉर्ड या सटीकता का प्रमाण नहीं है।',
    'We are a student hackathon team. This is an independent project, not a bank, police service or government-endorsed tool.':'हम छात्रों की हैकाथॉन टीम हैं। यह स्वतंत्र प्रोजेक्ट है, बैंक, पुलिस सेवा या सरकार द्वारा अनुमोदित उपकरण नहीं।',
    'Five people. One shared purpose.':'पाँच लोग। एक साझा मकसद।',
    'Privacy · prototype':'गोपनीयता · प्रोटोटाइप', 'Know what happens to your input.':'जानें आपकी जानकारी का क्या होता है।',
    'Messages and screenshots':'संदेश और स्क्रीनशॉट',
    'Checking sends your text to our Python backend. On the public site this runs on Streamlit Community Cloud. When AI is available, the message is sent to Google Gemini for analysis. Screenshot extraction sends the processed image to Gemini. Remove personal information before submitting. Third-party processing follows the provider’s policies.':'जाँच के लिए टेक्स्ट हमारे Python बैकएंड को भेजा जाता है। सार्वजनिक साइट पर यह Streamlit Community Cloud पर चलता है। AI उपलब्ध होने पर संदेश Google Gemini को भेजा जाता है। स्क्रीनशॉट की प्रोसेस की गई तस्वीर भी Gemini को भेजी जाती है। निजी जानकारी पहले हटा दें। तीसरे पक्ष की अपनी नीतियाँ लागू होती हैं।',
    'Browser preferences and feedback':'ब्राउज़र की पसंद और सुझाव',
    'Your theme and language preferences are saved in this browser. Message text is not saved to browser storage. Feedback is downloaded only when you choose to save it; it is not submitted to a team inbox.':'थीम और भाषा की पसंद इस ब्राउज़र में सहेजी जाती है। संदेश का टेक्स्ट ब्राउज़र स्टोरेज में नहीं सहेजा जाता। सुझाव सिर्फ आपके डाउनलोड करने पर फ़ाइल में सहेजा जाता है; टीम को नहीं भेजा जाता।',
    'Prototype limits':'प्रोटोटाइप की सीमाएँ',
    'This prototype keeps the latest request and result in your active server session. It does not intentionally save submissions to a database. Hosting and AI providers have their own retention policies. Do not submit confidential information. Feedback delivery is not connected yet.':'यह प्रोटोटाइप आपके सक्रिय सर्वर सत्र में आखिरी अनुरोध और नतीजा रखता है। जानकारी को डेटाबेस में जानबूझकर नहीं सहेजता। होस्टिंग और AI प्रदाताओं की जानकारी रखने की अपनी नीतियाँ हैं। गोपनीय जानकारी न भेजें। सुझाव भेजने की सुविधा अभी नहीं जुड़ी है।',
    'Paste a message first.':'पहले संदेश पेस्ट करें।', 'Checking the message. This may take a moment…':'संदेश की जाँच हो रही है। थोड़ा समय लग सकता है…',
    'Check stopped. Try again when you are ready.':'जाँच रुक गई। तैयार होने पर फिर कोशिश करें।', 'The check could not finish. Please try again.':'जाँच पूरी नहीं हुई। फिर कोशिश करें।',
    'Choose a PNG, JPEG or WebP image under 5 MB.':'5 MB से छोटी PNG, JPEG या WebP तस्वीर चुनें।', 'Reading the screenshot…':'स्क्रीनशॉट पढ़ा जा रहा है…',
    'Extraction stopped. Please try again.':'टेक्स्ट निकालना रुक गया। फिर कोशिश करें।',
    'Could not read this image. Try a clearer screenshot, or paste the message text.':'तस्वीर पढ़ी नहीं जा सकी। साफ़ स्क्रीनशॉट चुनें या संदेश का टेक्स्ट पेस्ट करें।',
    'Language changed. Check again for a result in this language.':'भाषा बदल गई। इस भाषा में नतीजा पाने के लिए दोबारा जाँचें।',
    '⛔ Scam':'⛔ धोखाधड़ी', '⚠ Likely scam':'⚠ धोखाधड़ी की आशंका', '✓ Safe':'✓ सुरक्षित', 'Check complete':'जाँच पूरी हुई',
    'Here’s what we found':'जाँच में यह मिला', 'Verify the message independently.':'संदेश की स्वतंत्र रूप से पुष्टि करें।',
    'Warning signs':'खतरे के संकेत', 'Your next steps':'अब क्या करें', 'How we checked':'हमने कैसे जाँचा',
    'AI analysis':'AI विश्लेषण', 'AI unavailable':'AI उपलब्ध नहीं', 'Warning-sign rules':'खतरे के नियम',
    'Reference examples could not be loaded. This result uses the remaining checks.':'संदर्भ उदाहरण लोड नहीं हुए। यह परिणाम बाकी उपलब्ध जाँचों पर आधारित है।',
    'Reference examples':'संदर्भ उदाहरण', 'Similar reference examples':'मिलते-जुलते संदर्भ उदाहरण',
    ' (Synthetic example)':' (बनाया गया उदाहरण)', 'A second opinion, not proof of who sent the message.':'यह दूसरी राय है, भेजने वाले की पहचान का प्रमाण नहीं।',
    'Clear and check another':'साफ़ करें और दूसरा संदेश जाँचें',
    'Offline explanations may remain in English.':'ऑफ़लाइन व्याख्या अंग्रेज़ी में रह सकती है।'
  };
  let language = 'en';
  try { language = localStorage.getItem('shield-language') === 'hi' ? 'hi' : 'en'; } catch {}
  const originals = new WeakMap();
  const attributes = new WeakMap();
  const t = text => language === 'hi' ? (hi[text] || text) : text;
  function apply() {
    document.documentElement.lang = language;
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    while (walker.nextNode()) {
      const node = walker.currentNode;
      if (node.parentElement.closest('script,style,textarea,#result,#status,#feedback-status,#upload-name,#count,#language-switch')) continue;
      if (!originals.has(node)) originals.set(node, node.nodeValue);
      const original = originals.get(node), key = original.trim();
      node.nodeValue = language === 'hi' && hi[key] ? original.replace(key, hi[key]) : original;
    }
    document.querySelectorAll('[placeholder],[aria-label],[alt]').forEach(el => {
      if (el.id === 'language-switch') return;
      if (!attributes.has(el)) attributes.set(el, Object.fromEntries(['placeholder','aria-label','alt'].filter(a=>el.hasAttribute(a)).map(a=>[a,el.getAttribute(a)])));
      Object.entries(attributes.get(el)).forEach(([attr,text])=>el.setAttribute(attr,t(text)));
    });
    const button = document.querySelector('#language-switch');
    button.textContent = language === 'en' ? 'हिंदी' : 'English';
    button.lang = language === 'en' ? 'hi' : 'en';
    button.setAttribute('aria-label',language === 'en' ? 'Switch language to Hindi' : 'भाषा अंग्रेज़ी करें');
  }
  function init() {
    apply();
    document.querySelector('#language-switch').onclick = () => {
      language = language === 'en' ? 'hi' : 'en';
      try { localStorage.setItem('shield-language',language); } catch {}
      apply();
      document.dispatchEvent(new Event('shield-language-change'));
    };
  }
  return { t, init, get language(){return language;} };
})();
