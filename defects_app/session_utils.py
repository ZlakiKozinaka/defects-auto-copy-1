from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.http import HttpResponseForbidden

from defects_app.permissions import is_manager_user

def require_station_session(request):
    station_id = request.session.get("station_id")
    shift_id = request.session.get("shift_id")

    if not request.user.is_authenticated:
        return None, redirect("login")

    if not station_id or not shift_id:
        logout(request)
        messages.info(request, "Сессия истекла. Войдите снова.")
        return None, redirect("login")

    return {
        "station_id": station_id,
        "shift_id": shift_id,
        "station_name": request.session.get("station_name"),
        "shift_name": request.session.get("shift_name"),
    }, None

def manager_required_view(request):
    if not request.user.is_authenticated:
        return redirect("login")

    if not is_manager_user(request.user):
        return HttpResponseForbidden("Доступ только для начальников.")

    return None