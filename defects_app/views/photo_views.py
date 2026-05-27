from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from defects_app.models import Defekty, StatusAvto
from defects_app.session_utils import manager_required_view

@login_required
def defect_photo_detail_view(request, defect_id):
    response = manager_required_view(request)
    if response:
        return response

    defect = get_object_or_404(
        Defekty.objects.select_related(
            "avto",
            "avto__model",
            "mesto",
            "tip",
            "oblast",
            "greyd",
            "otvetstvennyj",
            "smena",
        ).prefetch_related("photos"),
        id=defect_id
    )

    sgp_status = StatusAvto.objects.filter(
        avto=defect.avto,
        status="СГП"
    ).order_by("-data_statusa").first()

    return render(request, "defects_app/defect_photo_detail.html", {
        "defect": defect,
        "sgp_status": sgp_status,
    })