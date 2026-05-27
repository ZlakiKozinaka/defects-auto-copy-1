from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required

from defects_app.forms import CustomLoginForm, ManagerLoginForm
from defects_app.permissions import (
    has_permission,
    is_manager_user,
)

def custom_login_view(request):
    if request.user.is_authenticated:
        next_url = request.GET.get("next")
        if next_url:
            return redirect(next_url)
        return redirect("department_hub")

    if request.method == "POST":
        form = CustomLoginForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            shift = form.cleaned_data["shift"]
            department = form.cleaned_data["department"]

            # ВАЖНО: проверяем доступ к выбранному отделу ДО login()
            if not user_has_department_access(user, department):
                return render_access_denied(request, "Вы не имеете доступа к выбранному отделу. Проверьте, что выбрали правильный отдел.")


            # Только после проверки прав — логиним
            login(request, user)

            # Смена
            request.session["shift_id"] = shift.id
            request.session["shift_name"] = shift.nazvanie

            # Выбранный отдел
            request.session["department_key"] = department

            department_titles = {
                "otk": "ОТК",
                "aggregates": "Агрегаты",
                "logistics": "Логистика",
                "planning": "Планирование производства",
            }
            request.session["department_name"] = department_titles.get(department, department)

            # Очищаем station-контекст — станция теперь выбирается кнопкой в разделе
            request.session.pop("station_id", None)
            request.session.pop("station_name", None)

            next_url = request.GET.get("next")
            if next_url:
                return redirect(next_url)

            # Сразу в выбранный раздел
            return redirect("department_section", section=department)
    else:
        form = CustomLoginForm()

    return render(request, "registration/login.html", {"form": form})

def manager_login_view(request):
    if request.user.is_authenticated:
        if is_manager_user(request.user):
            return redirect("manager_dashboard")
        logout(request)

    if request.method == "POST":
        form = ManagerLoginForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()

            if not is_manager_user(user):
                messages.error(request, "Этот вход доступен только начальникам.")
                return render(request, "registration/manager_login.html", {"form": form})

            shift = form.cleaned_data["shift"]

            login(request, user)

            request.session["station_id"] = 999
            request.session["station_name"] = "Панель начальника"
            request.session["shift_id"] = shift.id
            request.session["shift_name"] = shift.nazvanie

            return redirect("manager_dashboard")
        else:
            messages.error(request, "Проверьте логин, пароль и смену.")
    else:
        form = ManagerLoginForm(request)

    return render(request, "registration/manager_login.html", {"form": form})

@login_required
def department_hub_view(request):
    departments = get_user_departments(request.user)

    if not departments:
        logout(request)
        messages.error(request, "Для вашей учетной записи не назначена ни одна роль.")
        return redirect("login")

    # если только одна принадлежность — сразу туда
    if len(departments) == 1:
        only_dep = list(departments)[0]
        return redirect("department_section", section=only_dep)

    return render(request, "defects_app/department_hub.html", {
        "departments": departments,
    })

@login_required
def department_section_view(request, section):
    if not user_has_department_access(request.user, section):
        return render_access_denied(request, "Вы не имеете доступа к этому отделу. Проверьте, что выбрали правильный отдел.")

    section_titles = {
        "otk": "ОТК",
        "aggregates": "Агрегаты",
        "logistics": "Логистика",
        "planning": "Планирование производства",
    }

    return render(request, "defects_app/department_section.html", {
        "section": section,
        "section_title": section_titles.get(section, section),
        "is_global_manager": is_manager_user(request.user),
    })

def get_user_departments(user):
    departments = set()

    if is_manager_user(user):
        departments.update(["otk", "aggregates", "logistics", "planning"])
        return departments

    if has_permission(user, "defects.create") or has_permission(user, "defects.edit"):
        departments.add("otk")

    if has_permission(user, "aggregates.fix") or has_permission(user, "aggregates.edit"):
        departments.add("aggregates")

    if has_permission(user, "cars.create_print"):
        departments.add("logistics")

    if has_permission(user, "reports.view"):
        departments.add("planning")

    return departments

def user_has_department_access(user, department_key):
    departments = get_user_departments(user)
    return department_key in departments

def render_access_denied(request, message=None):
    return render(request, "403.html", {
        "access_denied_message": message or "Проверьте, что выбран правильный отдел и роль пользователя.",
    }, status=403)

def csrf_failure_view(request, reason=""):
    return render(request, "defects_app/csrf_error.html", {
        "reason": reason,
    }, status=403)