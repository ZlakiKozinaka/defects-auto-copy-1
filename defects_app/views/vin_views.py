from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from defects_app.models import VinPrefix, PlanovyeVin

# внесение ВИН-номеров и их префиксов
@login_required
def vin_prefixes_api_view(request):
    prefixes = VinPrefix.objects.filter(
        is_active=True,
        show_in_select=True
    ).select_related("model").order_by("model__nazvanie", "prefix")

    data = []

    for item in prefixes:
        data.append({
            "model": item.model.nazvanie,
            "prefix": item.prefix,
        })

    return JsonResponse(data, safe=False)


@login_required
def vin_model_api_view(request):
    vin = request.GET.get("vin", "").strip().upper()

    if len(vin) != 17:
        return JsonResponse({
            "found": False,
            "model": None,
        })

    # Плановые VIN используем ТОЛЬКО для FREE,
    # потому что у FREE / FREE DKD / FREE MKD одинаковый префикс
    if vin.startswith("EDAVGC3B0TL"):
        plan_vin = PlanovyeVin.objects.filter(vin=vin).first()

        if plan_vin and plan_vin.model:
            return JsonResponse({
                "found": True,
                "source": "plan",
                "model": plan_vin.model.strip(),
            })

    # Все остальные модели определяем ТОЛЬКО по префиксу
    prefixes = VinPrefix.objects.filter(
        is_active=True,
        prefix__isnull=False
    ).select_related("model").order_by("-prefix")

    for item in prefixes:
        if vin.startswith(item.prefix):
            return JsonResponse({
                "found": True,
                "source": "prefix",
                "model": item.model.nazvanie,
            })

    return JsonResponse({
        "found": False,
        "model": None,
    })