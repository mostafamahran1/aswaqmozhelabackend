from io import BytesIO
from urllib.request import Request, urlopen

from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from PIL import Image, UnidentifiedImageError
from rest_framework.exceptions import APIException

MAX_SOURCE_BYTES = 10 * 1024 * 1024
MAX_STORED_BYTES = 250 * 1024
MAX_IMAGE_EDGE = 1000
CARD_EDGE = 640
CARD_QUALITY = 72
WEBP_QUALITIES = (80, 70)


class ImageRejected(APIException):
    status_code = 400
    default_code = 'image_rejected'

    def __init__(self, detail, code='image_rejected'):
        self.extra_code = code
        super().__init__(detail={'error': detail, 'code': code})


def _encode_webp(image, quality):
    buffer = BytesIO()
    image.save(buffer, format='WEBP', quality=quality, method=6)
    buffer.seek(0)
    return buffer


def optimize_upload(uploaded):
    """Store one light WebP. Reject anything that stays above 150 KB."""
    if uploaded is None or not isinstance(uploaded, UploadedFile):
        return uploaded
    if getattr(uploaded, '_aswaq_optimized', False):
        return uploaded

    size = getattr(uploaded, 'size', 0) or 0
    if size > MAX_SOURCE_BYTES:
        megabytes = size / (1024 * 1024)
        raise ImageRejected(
            f'الصورة حجمها {megabytes:.1f} ميجا. لازم تكون أصغر من 10 ميجا عشان نقدر نضغطها، ورفع المنتج اتوقف.',
            code='image_too_large',
        )
    if size == 0:
        raise ImageRejected('ملف الصورة فاضي، ورفع المنتج اتوقف.', code='image_empty')

    uploaded.seek(0)
    try:
        image = Image.open(uploaded)
        image.verify()
        uploaded.seek(0)
        image = Image.open(uploaded)
        image.load()
    except (UnidentifiedImageError, OSError, ValueError):
        raise ImageRejected(
            'الملف مش صورة صالحة. ارفع JPG أو PNG، ورفع المنتج اتوقف.',
            code='image_invalid',
        )

    if (
        size <= MAX_STORED_BYTES
        and (getattr(image, 'format', None) or '').upper() == 'WEBP'
        and max(image.size) <= MAX_IMAGE_EDGE
    ):
        uploaded.seek(0)
        uploaded._aswaq_optimized = True
        return uploaded

    has_alpha = image.mode in ('RGBA', 'LA') or (
        image.mode == 'P' and 'transparency' in image.info
    )
    if has_alpha and image.mode != 'RGBA':
        image = image.convert('RGBA')
    elif not has_alpha and image.mode != 'RGB':
        image = image.convert('RGB')
    image.thumbnail((MAX_IMAGE_EDGE, MAX_IMAGE_EDGE), Image.Resampling.LANCZOS)

    stored = None
    for quality in WEBP_QUALITIES:
        stored = _encode_webp(image, quality)
        if stored.getbuffer().nbytes <= MAX_STORED_BYTES:
            break

    stored_size = stored.getbuffer().nbytes
    if stored_size > MAX_STORED_BYTES:
        kilobytes = stored_size / 1024
        raise ImageRejected(
            f'الصورة بعد الضغط حجمها {kilobytes:.0f} كيلوبايت، والحد المسموح 250 كيلوبايت. رفع المنتج اتوقف.',
            code='image_too_large',
        )

    original_name = uploaded.name or 'upload.webp'
    stem = original_name.rsplit('.', 1)[0]
    optimized = InMemoryUploadedFile(
        stored,
        None,
        f'{stem}.webp',
        'image/webp',
        stored_size,
        None,
    )
    optimized._aswaq_optimized = True
    return optimized


def optimize_model_images(instance, field_names):
    for field_name in field_names:
        field_file = getattr(instance, field_name, None)
        if not field_file:
            continue
        current = getattr(field_file, '_file', None)
        if isinstance(current, UploadedFile):
            setattr(instance, field_name, optimize_upload(current))


def card_storage_name(storage_name):
    if not storage_name or storage_name.endswith('_card.webp'):
        return None
    stem = storage_name.rsplit('.', 1)[0]
    return f'{stem}_card.webp'


def _url_exists(url):
    request = Request(url, method='HEAD')
    try:
        with urlopen(request, timeout=15) as response:
            return 200 <= response.status < 300
    except Exception:
        return False


def write_card_image(field_file, force=False):
    """Small WebP used by product cards. A failure here must not block the product save."""
    try:
        return _write_card_image(field_file, force=force)
    except Exception:
        return None


def _write_card_image(field_file, force=False):
    if not field_file or not getattr(field_file, 'name', None):
        return None
    card_name = card_storage_name(field_file.name)
    if card_name is None:
        return None
    storage = field_file.storage
    card_url = storage.url(card_name)
    if not force and _url_exists(card_url):
        return card_name
    with urlopen(field_file.url, timeout=30) as response:
        data = response.read(12 * 1024 * 1024)
    image = Image.open(BytesIO(data))
    image.load()

    has_alpha = image.mode in ('RGBA', 'LA') or (
        image.mode == 'P' and 'transparency' in image.info
    )
    if has_alpha and image.mode != 'RGBA':
        image = image.convert('RGBA')
    elif not has_alpha and image.mode != 'RGB':
        image = image.convert('RGB')
    image.thumbnail((CARD_EDGE, CARD_EDGE), Image.Resampling.LANCZOS)
    stored = BytesIO()
    image.save(stored, format='WEBP', quality=CARD_QUALITY, method=4)
    storage.save(card_name, ContentFile(stored.getvalue()))
    return card_name
