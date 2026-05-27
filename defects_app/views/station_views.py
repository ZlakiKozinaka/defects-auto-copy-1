from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import Http404

from defects_app.models import Mesta
from defects_app.permissions import (
    is_manager_user,
    can_create_defects,
    can_fix_aggregates,
    can_create_cars_and_print,
)
from defects_app.views.auth_views import render_access_denied
from defects_app.views_helpers import (
    get_station_redirect_name,
    is_vh1_station,
    get_vh1_station,
)

@login_required
def open_station_for_department_view(request, station_id):
    station = Mesta.objects.filter(id=station_id).first()
    if not station:
        if station_id == 13:
            return redirect("open_vh1_station_for_department")
        raise Http404("No Mesta matches the given query.")

    user = request.user
    allowed = False

    # Глобальные начальники могут всё
    if is_manager_user(user):
        allowed = True
    else:
        # ОТК
        if station_id in [1, 2, 8, 9, 10, 11] and can_create_defects(user):
            allowed = True

        if can_create_defects(user) and is_vh1_station(station_id=station.id, station_name=station.nazvanie):
            allowed = True

        # Агрегаты
        if station_id in [3, 4, 5, 6, 7] and can_fix_aggregates(user):
            allowed = True

        # Логистика (станция создания машины)
        if station_id == 12 and can_create_cars_and_print(user):
            allowed = True

    if not allowed:
        return render_access_denied(request, "У вас нет доступа к выбранной станции для этого отдела.")

    # Смена уже должна быть выбрана на логине
    shift_id = request.session.get("shift_id")
    shift_name = request.session.get("shift_name")
    if not shift_id or not shift_name:
        logout(request)
        messages.error(request, "Смена не выбрана. Войдите заново.")
        return redirect("login")

    request.session["station_id"] = station.id
    request.session["station_name"] = station.nazvanie

    redirect_name = get_station_redirect_name(station.id)
    return redirect(redirect_name)


@login_required
def open_vh1_station_for_department_view(request):
    station = get_vh1_station()
    if not station:
        return render_access_denied(request, "Станция ВХ1 не найдена в справочнике мест.")

    user = request.user
    allowed = False
    if is_manager_user(user):
        allowed = True
    elif can_create_defects(user):
        allowed = True

    if not allowed:
        return render_access_denied(request, "У вас нет доступа к выбранной станции для этого отдела.")

    shift_id = request.session.get("shift_id")
    shift_name = request.session.get("shift_name")
    if not shift_id or not shift_name:
        logout(request)
        messages.error(request, "Смена не выбрана. Войдите заново.")
        return redirect("login")

    request.session["station_id"] = station.id
    request.session["station_name"] = station.nazvanie
    return redirect("vh1")