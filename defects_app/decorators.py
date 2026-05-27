# defects_app/decorators.py
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from .permissions import has_permission


def permission_required(permission_code: str):
    """
    Декоратор для проверки права по коду.
    Использование:
    @permission_required("defects.create")
    def create_defect(...):
        ...
    """
    def outer(view_func):
        @login_required
        @wraps(view_func)
        def inner(request, *args, **kwargs):
            if not has_permission(request.user, permission_code):
                # Если хотите рендерить красивый 403-шаблон:
                # from .views import render_access_denied
                # return render_access_denied(request, "Недостаточно прав для выполнения действия.")
                return HttpResponseForbidden("Недостаточно прав.")
            return view_func(request, *args, **kwargs)
        return inner
    return outer


def department_required(section_key: str):
    """
    Декоратор для ограничения доступа к отделу.
    Требует функцию get_user_departments(user).
    """
    def outer(view_func):
        @login_required
        @wraps(view_func)
        def inner(request, *args, **kwargs):
            from .views import get_user_departments  # временно так, чтобы не было циклов на старте
            departments = get_user_departments(request.user)
            if section_key not in departments:
                return HttpResponseForbidden("Нет доступа к отделу.")
            return view_func(request, *args, **kwargs)
        return inner
    return outer


def station_session_required(view_func):
    @login_required
    @wraps(view_func)
    def inner(request, *args, **kwargs):
        from django.contrib.auth import logout
        from django.contrib import messages
        from django.shortcuts import redirect

        station_id = request.session.get("station_id")
        shift_id = request.session.get("shift_id")

        if not station_id or not shift_id:
            logout(request)
            messages.info(request, "Сессия истекла. Войдите снова.")
            return redirect("login")

        request.station_context = {
            "station_id": station_id,
            "shift_id": shift_id,
            "station_name": request.session.get("station_name"),
            "shift_name": request.session.get("shift_name"),
        }

        return view_func(request, *args, **kwargs)

    return inner