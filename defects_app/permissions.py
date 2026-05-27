# defects_app/permissions.py
from django.contrib.auth.models import Group

# --- Группы (единый источник правды) ---
GROUP_GLOBAL_MANAGERS = "Начальники"

GROUP_OTK_WORKER = "Работник ОТК"
GROUP_OTK_MANAGER = "Начальник ОТК"

GROUP_AGG_WORKER = "Работник Агрегатов"
GROUP_AGG_MANAGER = "Начальник Агрегатов"

GROUP_LOG_WORKER = "Работник Логистики"
GROUP_LOG_MANAGER = "Начальник Логистики"

GROUP_PLANNING = "Отдел планирования производства"

# На будущее (склад/филиалы):
# GROUP_WAREHOUSE_WORKER = "Работник склада"
# GROUP_WAREHOUSE_MANAGER = "Начальник склада"


def user_in_group(user, group_name: str) -> bool:
    if not user.is_authenticated:
        return False
    return user.groups.filter(name=group_name).exists()


def is_global_manager(user) -> bool:
    return bool(user.is_authenticated and (user.is_superuser or user_in_group(user, GROUP_GLOBAL_MANAGERS)))


# --- Матрица прав ---
# Ключ = "permission_code", значение = группы, которым разрешено.
PERMISSIONS_MAP = {
    "defects.create": {GROUP_OTK_WORKER, GROUP_OTK_MANAGER, GROUP_GLOBAL_MANAGERS},
    "defects.edit": {GROUP_OTK_MANAGER, GROUP_GLOBAL_MANAGERS},
    "defects.delete": {GROUP_OTK_MANAGER, GROUP_GLOBAL_MANAGERS},

    "aggregates.fix": {GROUP_AGG_WORKER, GROUP_AGG_MANAGER, GROUP_GLOBAL_MANAGERS},
    "aggregates.edit": {GROUP_AGG_MANAGER, GROUP_GLOBAL_MANAGERS},

    "cars.create_print": {GROUP_LOG_WORKER, GROUP_LOG_MANAGER, GROUP_GLOBAL_MANAGERS},

    "reports.view": {
        GROUP_OTK_MANAGER,
        GROUP_AGG_MANAGER,
        GROUP_LOG_MANAGER,
        GROUP_PLANNING,
        GROUP_GLOBAL_MANAGERS,
    },

    # На будущее:
    # "warehouse.view": {GROUP_WAREHOUSE_WORKER, GROUP_WAREHOUSE_MANAGER, GROUP_GLOBAL_MANAGERS},
    # "warehouse.receive": {GROUP_WAREHOUSE_WORKER, GROUP_WAREHOUSE_MANAGER, GROUP_GLOBAL_MANAGERS},
    # "warehouse.issue": {GROUP_WAREHOUSE_MANAGER, GROUP_GLOBAL_MANAGERS},
}


def has_permission(user, permission_code: str) -> bool:
    """
    Единая проверка разрешения.
    """
    if not user.is_authenticated:
        return False

    # Суперпользователь всегда имеет доступ
    if user.is_superuser:
        return True

    allowed_groups = PERMISSIONS_MAP.get(permission_code)
    if not allowed_groups:
        # Если permission_code не описан — доступа нет
        return False

    return user.groups.filter(name__in=allowed_groups).exists()

def is_manager_user(user):
    return is_global_manager(user)


def can_create_defects(user):
    return has_permission(user, "defects.create")


def can_edit_delete_defects(user):
    return has_permission(user, "defects.edit")


def can_fix_aggregates(user):
    return has_permission(user, "aggregates.fix")


def can_edit_aggregates(user):
    return has_permission(user, "aggregates.edit")


def can_create_cars_and_print(user):
    return has_permission(user, "cars.create_print")


def can_view_reports_exports(user):
    return has_permission(user, "reports.view")