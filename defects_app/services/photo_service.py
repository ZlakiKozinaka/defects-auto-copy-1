# defects_app/services/photo_service.py

import uuid
from io import BytesIO

from PIL import Image, ImageOps
from django.core.files.base import ContentFile
from django.contrib import messages

from defects_app.models import (
    DefectPhoto,
    ContainerReceiptPhoto,
    ContainerCarPhoto,
)


MAX_PHOTO_SIZE = (1280, 1280)
WEBP_QUALITY = 70
WEBP_METHOD = 4


def save_defect_photos(defect, request):
    photos = request.FILES.getlist("photos")

    for uploaded_file in photos:
        try:
            image = Image.open(uploaded_file)
            image = ImageOps.exif_transpose(image)

            if image.mode != "RGB":
                image = image.convert("RGB")

            image.thumbnail(MAX_PHOTO_SIZE, Image.Resampling.LANCZOS)

            buffer = BytesIO()
            image.save(
                buffer,
                format="WEBP",
                quality=WEBP_QUALITY,
                method=WEBP_METHOD,
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


def save_container_receipt_photos(receipt, request):
    photos = request.FILES.getlist("photos")

    for uploaded_file in photos:
        try:
            image = Image.open(uploaded_file)
            image = ImageOps.exif_transpose(image)

            if image.mode != "RGB":
                image = image.convert("RGB")

            image.thumbnail(MAX_PHOTO_SIZE, Image.Resampling.LANCZOS)

            buffer = BytesIO()

            image.save(
                buffer,
                format="WEBP",
                quality=WEBP_QUALITY,
                method=WEBP_METHOD,
            )

            file_name = f"{uuid.uuid4().hex}.webp"

            photo = ContainerReceiptPhoto(
                receipt=receipt,
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
                f"Не удалось обработать фото контейнера: {uploaded_file.name}. Ошибка: {e}"
            )

def save_container_car_photos(container_car, request):
    photos = request.FILES.getlist("photos")
    existing_original_names = set(
        container_car.photos.exclude(original_name__isnull=True)
        .exclude(original_name="")
        .values_list("original_name", flat=True)
    )
    skipped_count = 0
   
    for uploaded_file in photos:
        if uploaded_file.name in existing_original_names:
            skipped_count += 1
            continue
        
        try:
            image = Image.open(uploaded_file)
            image = ImageOps.exif_transpose(image)

            if image.mode != "RGB":
                image = image.convert("RGB")

            image.thumbnail(MAX_PHOTO_SIZE, Image.Resampling.LANCZOS)

            buffer = BytesIO()

            image.save(
                buffer,
                format="WEBP",
                quality=WEBP_QUALITY,
                method=WEBP_METHOD,
            )

            file_name = f"{uuid.uuid4().hex}.webp"

            photo = ContainerCarPhoto(
                container_car=container_car,
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
            existing_original_names.add(uploaded_file.name)

        except Exception as e:
            messages.error(
                request,
                f"Не удалось обработать фото машины: {uploaded_file.name}. Ошибка: {e}"
            )

    if skipped_count:
        messages.info(
            request,
            f"Повторные фото машины пропущены: {skipped_count}."
        )