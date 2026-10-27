from io import BytesIO
from PIL import Image
import pytest
from src.image_reader import prepare_image, extract_text, ImageInputError, MAX_UPLOAD_BYTES

def make_test_image(format="PNG", size=(100, 100), color="white"):
    buf = BytesIO()
    im = Image.new("RGB", size, color=color)
    im.save(buf, format=format)
    return buf.getvalue()

def test_prepare_image_valid_png():
    png_bytes = make_test_image("PNG")
    prepared = prepare_image(png_bytes)
    assert isinstance(prepared, bytes)
    assert len(prepared) > 0
    # Output must be a valid PNG
    im = Image.open(BytesIO(prepared))
    assert im.format == "PNG"

def test_prepare_image_valid_jpeg():
    jpg_bytes = make_test_image("JPEG")
    prepared = prepare_image(jpg_bytes)
    im = Image.open(BytesIO(prepared))
    assert im.format == "PNG"

def test_prepare_image_invalid_bytes():
    with pytest.raises(ImageInputError) as exc:
        prepare_image(b"not an image data at all")
    assert str(exc.value) == "damaged"

def test_prepare_image_wrong_format():
    # GIF is not in allowed formats (PNG, JPEG, WEBP)
    gif_bytes = make_test_image("GIF")
    with pytest.raises(ImageInputError) as exc:
        prepare_image(gif_bytes)
    assert str(exc.value) == "wrong_format"

def test_prepare_image_oversized():
    oversized = b"0" * (MAX_UPLOAD_BYTES + 10)
    with pytest.raises(ImageInputError) as exc:
        prepare_image(oversized)
    assert str(exc.value) == "too_large"

def test_extract_text_no_key():
    png_bytes = make_test_image("PNG")
    with pytest.raises(ImageInputError) as exc:
        extract_text(png_bytes, api_key=None)
    assert str(exc.value) == "unavailable"
