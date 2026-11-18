from io import BytesIO

from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from PIL import Image, UnidentifiedImageError
from rest_framework.exceptions import APIException

MAX_IMAGE_BYTES = 10 * 1024 * 1024
MAX_IMAGE_EDGE = 1600
JPEG_QUALITY = 82


class ImageRejected(APIException):
    status_code = 400
    default_code = 'image_rejected'

    def __init__(self, detail, code='image_rejected'):
        self.extra_code = code
        super().__init__(detail={'error': detail, 'code': code})


def optimize_upload(uploaded):
    """Reject files over 10 MB, then store a resized copy for fast downloads."""
    if uploaded is None or not isinstance(uploaded, UploadedFile):
        return uploaded
    if getattr(uploaded, '_aswaq_optimized', False):
        return uploaded

    size = getattr(uploaded, 'size', 0) or 0
    if size > MAX_IMAGE_BYTES:
        megabytes = size / (1024 * 1024)
        raise ImageRejected(
            f'الصورة أكبر من 10 ميجا ({megabytes:.1f} ميجا). اختار صورة أصغر.',
            code='image_too_large',
        )
    if size == 0:
        raise ImageRejected('ملف الصورة فاضي.', code='image_empty')

    uploaded.seek(0)
    try:
        image = Image.open(uploaded)
        image.verify()
        uploaded.seek(0)
        image = Image.open(uploaded)
        image.load()
    except (UnidentifiedImageError, OSError, ValueError):
        raise ImageRejected(
            'الملف مش صورة صالحة. ارفع JPG أو PNG.',
            code='image_invalid',
        )

    has_alpha = image.mode in ('RGBA', 'LA') or (
        image.mode == 'P' and 'transparency' in image.info
    )
    image.thumbnail((MAX_IMAGE_EDGE, MAX_IMAGE_EDGE), Image.Resampling.LANCZOS)

    buffer = BytesIO()
    if has_alpha:
        image.save(buffer, format='PNG', optimize=True)
        content_type = 'image/png'
        extension = 'png'
    else:
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image.save(buffer, format='JPEG', quality=JPEG_QUALITY, optimize=True)
        content_type = 'image/jpeg'
        extension = 'jpg'

    buffer.seek(0)
    original_name = uploaded.name or f'upload.{extension}'
    stem = original_name.rsplit('.', 1)[0]
    optimized = InMemoryUploadedFile(
        buffer,
        None,
        f'{stem}.{extension}',
        content_type,
        buffer.getbuffer().nbytes,
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
