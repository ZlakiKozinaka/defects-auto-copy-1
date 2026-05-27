# defects_app/services/photo_service.py

import uuid
from io import BytesIO

from PIL import Image, ImageOps
from django.core.files.base import ContentFile
from django.contrib import messages

from defects_app.models import DefectPhoto


def save_defect_photos(defect, request):
    photos = request.FILES.getlist("photos")

    for uploaded_file in photos:
        try:
            image = Image.open(uploaded_file)
            image = ImageOps.exif_transpose(image)

            if image.mode != "RGB":
                image = image.convert("RGB")

            image.thumbnail((1280, 1280), Image.Resampling.LANCZOS)

            buffer = BytesIO()
            image.save(
                buffer,
                format="WEBP",
                quality=70,
                method=6,
            )

            file_name = f"{uuid.uuid4().hex}.webp"

            photo = DefectPhoto(
                defect=defect,
                avto=defect.avto,
                original_name=uploaded_file.name,
                uploaded_by=request.user.username,
            )

            photo.image.save(
                file_name,
                ContentFile(buffer.getvalue()),
                save=True,
            )

            photo.file_size = photo.image.size
            photo.save(update_fields=["file_size"])

        except Exception as e:
            messages.error(
                request,
                f"Не удалось обработать фото: {uploaded_file.name}. Ошибка: {e}"
            )