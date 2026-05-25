from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.db import transaction, connection

from defects_app.models import (
    Greydy,
    Mesta,
    Modeli,
    Otvetstvennye,
    Smeny,
    Tipy,
    Oblasti,   # если модель у тебя называется не Oblasti, замени только это имя
)


GROUPS = [
    {"id": 1, "name": "Работники"},
    {"id": 2, "name": "Начальники"},
]

GREYDY = [
    {"id": 1, "nazvanie": "V1"},
    {"id": 2, "nazvanie": "V2"},
    {"id": 3, "nazvanie": "V3"},
]

MESTA = [
    {"id": 1, "nazvanie": "Бестеневая"},
    {"id": 2, "nazvanie": "OkLine"},
    {"id": 3, "nazvanie": "Телематика"},
    {"id": 4, "nazvanie": "Глонасс"},
    {"id": 5, "nazvanie": "Батарея"},
    {"id": 6, "nazvanie": "Передний двигатель"},
    {"id": 7, "nazvanie": "Задний двигатель"},
    {"id": 8, "nazvanie": "Станция 3 – Качество"},
    {"id": 9, "nazvanie": "Т20 – Качество"},
    {"id": 10, "nazvanie": "С06 – Качество"},
    {"id": 11, "nazvanie": "Доводка"},
    {"id": 12, "nazvanie": "Станция №1"},
]

MODELI = [
    {"id": 1, "nazvanie": "FREE"},
    {"id": 2, "nazvanie": "I-JOY new"},
    {"id": 3, "nazvanie": "I-Jet"},
    {"id": 4, "nazvanie": "I-SKY"},
    {"id": 5, "nazvanie": "I-SKY NEW"},
    {"id": 6, "nazvanie": "I-SPACE (пятиместный)"},
    {"id": 7, "nazvanie": "I-SPACE (семиместный)"},
    {"id": 8, "nazvanie": "I-SPACE (4X4)"},
    {"id": 9, "nazvanie": "I-SPACE CKD (пятиместный)"},
    {"id": 10, "nazvanie": "I-SPACE CKD (семиместный)"},
]

OTVETSTVENNYE = [
    {"id": 1, "nazvanie": "Отдел логистики", "aktiven": True},
    {"id": 2, "nazvanie": "Производство", "aktiven": True},
    {"id": 3, "nazvanie": "Инженерный отдел", "aktiven": True},
    {"id": 4, "nazvanie": "Технологический отдел", "aktiven": True},
    {"id": 5, "nazvanie": "Поставщики", "aktiven": True},
]

SMENY = [
    {"id": 1, "nazvanie": "A"},
]

TIPY = [
    {"id": 1, "nazvanie": "Скол"},
    {"id": 2, "nazvanie": "Царапина"},
    {"id": 3, "nazvanie": "Потертость"},
    {"id": 4, "nazvanie": "Повреждение"},
    {"id": 5, "nazvanie": "Вмятина"},
    {"id": 6, "nazvanie": "Отсутствие"},
    {"id": 7, "nazvanie": "Грязь и потёртости"},
    {"id": 8, "nazvanie": "Голограмма"},
    {"id": 9, "nazvanie": "Следы краски"},
    {"id": 10, "nazvanie": "Матовые пятна"},
    {"id": 11, "nazvanie": "Сорность"},
]

OBLASTI = [
    {"id": 1, "nazvanie": "Передний бампер"},
    {"id": 2, "nazvanie": "Задний бампер"},
    {"id": 3, "nazvanie": "Капот"},
    {"id": 4, "nazvanie": "Передняя правая дверь"},
    {"id": 5, "nazvanie": "Передняя левая дверь"},
    {"id": 6, "nazvanie": "Задняя правая дверь"},
    {"id": 7, "nazvanie": "Задняя левая дверь"},
    {"id": 8, "nazvanie": "Дверь багажного отделения"},
    {"id": 9, "nazvanie": "Переднее правое крыло"},
    {"id": 10, "nazvanie": "Переднее левое крыло"},
    {"id": 11, "nazvanie": "Заднее правое крыло"},
    {"id": 12, "nazvanie": "Заднее левое крыло"},
    {"id": 13, "nazvanie": "Передняя правая арка"},
    {"id": 14, "nazvanie": "Передняя левая арка"},
    {"id": 15, "nazvanie": "Задняя левая арка"},
    {"id": 16, "nazvanie": "Задняя правая арка"},
    {"id": 17, "nazvanie": "Наружное правое зеркало заднего вида"},
    {"id": 18, "nazvanie": "Наружное левое зеркало заднего вида"},
    {"id": 19, "nazvanie": "Передняя левая фара"},
    {"id": 20, "nazvanie": "Передняя правая фара"},
    {"id": 21, "nazvanie": "Задняя левая фара"},
    {"id": 22, "nazvanie": "Задняя правая фара"},
    {"id": 23, "nazvanie": "Центральная передняя фара"},
    {"id": 24, "nazvanie": "Центральная задняя фара"},
    {"id": 25, "nazvanie": "Переднее правое колесо"},
    {"id": 26, "nazvanie": "Переднее левое колесо"},
    {"id": 27, "nazvanie": "Заднее правое колесо"},
    {"id": 28, "nazvanie": "Заднее левое колесо"},
    {"id": 29, "nazvanie": "Левый порог"},
    {"id": 30, "nazvanie": "Правый порог"},
    {"id": 31, "nazvanie": "Лобовое стекло"},
    {"id": 32, "nazvanie": "Переднее правое стекло"},
    {"id": 33, "nazvanie": "Переднее левое стекло"},
    {"id": 34, "nazvanie": "Заднее правое стекло"},
    {"id": 35, "nazvanie": "Заднее левое стекло"},
    {"id": 36, "nazvanie": "Стекло двери багажника"},
    {"id": 37, "nazvanie": "Заднее левое стекло окна боковины"},
    {"id": 38, "nazvanie": "Заднее правое стекло окна боковины"},
    {"id": 39, "nazvanie": "Спойлер"},
    {"id": 40, "nazvanie": "Пластиковая накладка спойлера левая"},
    {"id": 41, "nazvanie": "Пластиковая накладка спойлера правая"},
    {"id": 42, "nazvanie": "Задняя правая противотуманная фара"},
    {"id": 43, "nazvanie": "Задняя левая противотуманная фара"},
    {"id": 44, "nazvanie": "Лучек зарядного разъема"},
    {"id": 45, "nazvanie": "Лучек бензобака"},
    {"id": 46, "nazvanie": "Пластиковая площадка под номерной знак спереди"},
    {"id": 47, "nazvanie": "Пластиковая площадка под номерной знак задняя"},
    {"id": 48, "nazvanie": "Передний левый поводок дворника"},
    {"id": 49, "nazvanie": "Передний правый поводок дворника"},
    {"id": 50, "nazvanie": "Поводок заднего дворника"},
    {"id": 51, "nazvanie": "Жабо"},
    {"id": 52, "nazvanie": "Переднее левое сиденье"},
    {"id": 53, "nazvanie": "Переднее правое сиденье"},
    {"id": 54, "nazvanie": "Заднее левое сиденье"},
    {"id": 55, "nazvanie": "Заднее центральное сиденье"},
    {"id": 56, "nazvanie": "Заднее правое сиденье"},
    {"id": 57, "nazvanie": "Центральная консоль"},
    {"id": 58, "nazvanie": "Панорамное стекло крыши"},
    {"id": 59, "nazvanie": "Панорамный люк крыши"},
    {"id": 60, "nazvanie": "Ремень безопасности передний левый"},
    {"id": 61, "nazvanie": "Ремень безопасности передний правый"},
    {"id": 62, "nazvanie": "Ремень безопасности задний левый"},
    {"id": 63, "nazvanie": "Ремень безопасности задний центральный"},
    {"id": 64, "nazvanie": "Ремень безопасности задний правый"},
    {"id": 65, "nazvanie": "Подголовник передний правый"},
    {"id": 66, "nazvanie": "Подголовник передний левый"},
    {"id": 67, "nazvanie": "Подголовник задний правый"},
    {"id": 68, "nazvanie": "Подголовник задний левый"},
    {"id": 69, "nazvanie": "Подголовник задний центральный"},
    {"id": 70, "nazvanie": "Дверная карта передняя левая"},
    {"id": 71, "nazvanie": "Дверная карта передняя правая"},
    {"id": 72, "nazvanie": "Дверная карта задняя левая"},
    {"id": 73, "nazvanie": "Дверная карта задняя правая"},
    {"id": 74, "nazvanie": "Дверная ручка задняя левая"},
    {"id": 75, "nazvanie": "Дверная ручка задняя правая"},
    {"id": 76, "nazvanie": "Дверная ручка передняя левая"},
    {"id": 77, "nazvanie": "Дверная ручка передняя правая"},
    {"id": 78, "nazvanie": "Педаль газа"},
    {"id": 79, "nazvanie": "Педаль тормоза"},
    {"id": 80, "nazvanie": "Селектор коробки передач"},
    {"id": 81, "nazvanie": "Боковая облицовка панели приборов левая"},
    {"id": 82, "nazvanie": "Боковая облицовка панели приборов правая"},
    {"id": 83, "nazvanie": "Нижняя облицовка панели приборов левая"},
    {"id": 84, "nazvanie": "Бардачок"},
    {"id": 85, "nazvanie": "Приборная панель"},
    {"id": 86, "nazvanie": "Зеркало заднего вида"},
    {"id": 87, "nazvanie": "Солнцезащитный козырек левый"},
    {"id": 88, "nazvanie": "Солнцезащитный козырек правый"},
    {"id": 89, "nazvanie": "Решетка радиатора"},
    {"id": 90, "nazvanie": "Потолочная ручка передняя левая"},
    {"id": 91, "nazvanie": "Потолочная ручка передняя правая"},
    {"id": 92, "nazvanie": "Потолочная ручка задняя левая"},
    {"id": 93, "nazvanie": "Потолочная ручка задняя правая"},
    {"id": 94, "nazvanie": "IP панель"},
    {"id": 95, "nazvanie": "Багажное отделение"},
    {"id": 96, "nazvanie": "Руль"},
    {"id": 97, "nazvanie": "Кузов"},
    {"id": 98, "nazvanie": "Салон"},
    {"id": 99, "nazvanie": "Площадка под VIN номер"},
]


class Command(BaseCommand):
    help = "Заполняет начальные справочники фиксированными ID"

    def reset_sequence(self, table_name, id_column="id"):
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT setval(
                    pg_get_serial_sequence('"{table_name}"', '{id_column}'),
                    COALESCE((SELECT MAX({id_column}) FROM "{table_name}"), 1),
                    true
                );
                """
            )

    def upsert_group(self, item):
        Group.objects.update_or_create(
            id=item["id"],
            defaults={"name": item["name"]}
        )

    def upsert_model(self, model_class, items):
        for item in items:
            defaults = item.copy()
            defaults.pop("id", None)

            model_class.objects.update_or_create(
                nazvanie=item["nazvanie"],
                defaults=defaults
            )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Заполнение справочников..."))

        for group in GROUPS:
            self.upsert_group(group)

        self.upsert_model(Greydy, GREYDY)
        self.upsert_model(Mesta, MESTA)
        self.upsert_model(Modeli, MODELI)
        self.upsert_model(Otvetstvennye, OTVETSTVENNYE)
        self.upsert_model(Smeny, SMENY)
        self.upsert_model(Tipy, TIPY)
        self.upsert_model(Oblasti, OBLASTI)

        self.reset_sequence("auth_group")
        self.reset_sequence("defects_app_greydy")
        self.reset_sequence("defects_app_mesta")
        self.reset_sequence("defects_app_modeli")
        self.reset_sequence("defects_app_otvetstvennye")
        self.reset_sequence("defects_app_smeny")
        self.reset_sequence("defects_app_tipy")
        self.reset_sequence("defects_app_oblasti")

        self.stdout.write(self.style.SUCCESS("Справочники успешно заполнены."))