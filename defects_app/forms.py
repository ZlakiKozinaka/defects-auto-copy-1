from django import forms
import re
from .models import Avtomobili, Modeli, Smeny
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm
from .models import Mesta
from .models import Defekty, Tipy, Oblasti, Greydy, Otvetstvennye, Stancii, ContainerReceipt

VIN_PREFIXES = {
    "FREE": "EDAVGC3B0TL",      #stay   
    "I-JOY new": "EDAE5C1A0TN", #stay  
    "I-Jet": "EDAE6C1A0TN",     #stay     
    "I-SKY": "EDAE4C1A0SL",
    "I-SKY NEW": "EDAE3C2AETL",
    "I-SPACE (пятиместный)": "EDAE6C2A5TN",
    "I-SPACE (семиместный)": "EDAE6C2A7TN",
    "I-SPACE (4X4)": "EDAE6C2B5TN", 
    "I-SPACE CKD (пятиместный)": "EDAE6C2A5SN",
    "I-SPACE CKD (семиместный)": "EDAE6C2A7SN",
}

class CarSearchForm(forms.Form):
    vin = forms.CharField(
        label="VIN-номер",
        max_length=17,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Введите полный VIN"
        })
    )

    model = forms.ModelChoiceField(
        label="Модель",
        queryset=Modeli.objects.none(),
        required=False,
        empty_label="Выберите модель",
        widget=forms.Select(attrs={"class": "form-control"})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["model"].queryset = Modeli.objects.filter(
            vin_prefixes__show_in_select=True,
            vin_prefixes__is_active=True
        ).distinct().order_by("nazvanie")

    def clean_vin(self):
        vin = self.cleaned_data["vin"].strip().upper()

        if len(vin) != 17:
            raise forms.ValidationError("VIN должен содержать 17 символов.")

        return vin


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={
            "class": "form-control",
            "multiple": True,
            "accept": "image/jpeg,image/png,image/webp"
        }))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean

        if isinstance(data, (list, tuple)):
            return [single_file_clean(file, initial) for file in data]

        return single_file_clean(data, initial)

class DefectForm(forms.ModelForm):
    photos = MultipleFileField(
        label="Фото дефекта",
        required=False
    )

    oblast_search = forms.CharField(
        label="Поиск области",
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Начните вводить область..."
        })
    )

    class Meta:
        model = Defekty
        fields = [
            "tip",
            "oblast",
            "greyd",
            "otvetstvennyj",
            "kommentarij",
        ]

        widgets = {
            "tip": forms.Select(attrs={"class": "form-control"}),
            "oblast": forms.Select(attrs={"class": "form-control"}),
            "greyd": forms.Select(attrs={"class": "form-control"}),
            "otvetstvennyj": forms.Select(attrs={"class": "form-control"}),
            "kommentarij": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["tip"].empty_label = "Выберите тип"
        self.fields["oblast"].empty_label = "Выберите область"
        self.fields["greyd"].empty_label = "Выберите грейд"
        self.fields["otvetstvennyj"].empty_label = "Выберите ответственного"
        self.fields["otvetstvennyj"].required = True

    def clean(self):
        cleaned_data = super().clean()

        required_fields = [
            "tip",
            "oblast",
            "greyd",
            "otvetstvennyj",
        ]

        for field in required_fields:
            if not cleaned_data.get(field):
                raise forms.ValidationError("Заполните все обязательные поля!")

        return cleaned_data



DEPARTMENT_CHOICES = [
    ("otk", "ОТК"),
    ("aggregates", "Агрегаты"),
    ("logistics", "Логистика"),
    ("planning", "Планирование производства"),
]


class CustomLoginForm(AuthenticationForm):
    department = forms.ChoiceField(
        choices=DEPARTMENT_CHOICES,
        label="Принадлежность",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    shift = forms.ModelChoiceField(
        queryset=Smeny.objects.all(),
        label="Смена",
        empty_label="Выберите смену",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Единый стиль для всех полей (username, password, department, shift)
        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (existing + " form-control").strip()


class TelematikaForm(forms.Form):
    telematika = forms.CharField(
        label="Телематика",
        max_length=100,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Введите или отсканируйте номер телематики",
            "autocomplete": "off"
        })
    )

    def clean_telematika(self):
        telematika = (
            self.cleaned_data["telematika"]
            .replace("\n", "")
            .replace("\r", "")
            .strip()
        )

        telematika_digits = re.sub(r"\D", "", telematika)

        if len(telematika_digits) != 15:
            raise forms.ValidationError("Телематика должна состоять из 15 цифр.")

        return telematika_digits

class GlonassForm(forms.Form):
    glonass = forms.CharField(
        label="ГЛОНАСС",
        max_length=300,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 3,
            "placeholder": "Например: SN:275192538928; HF:208 (Voyah FREE); IMEI:861005074515666; ICCID:8970177000153017184;"
        })
    )
    def clean_glonass(self):
        value = self.cleaned_data["glonass"].strip()

        if "SN:" not in value.upper() or "IMEI:" not in value.upper() or "ICCID:" not in value.upper():
            raise forms.ValidationError("Строка ГЛОНАСС должна содержать SN, IMEI и ICCID.")

        sn_match = re.search(r"SN\s*:\s*([^;]+)", value, re.IGNORECASE)
        imei_match = re.search(r"IMEI\s*:\s*([^;]+)", value, re.IGNORECASE)
        iccid_match = re.search(r"ICCID\s*:\s*([^;]+)", value, re.IGNORECASE)

        if not sn_match or len(re.sub(r"\D", "", sn_match.group(1))) != 12:
            raise forms.ValidationError("Поле SN в ГЛОНАСС должно содержать 12 цифр.")

        if not imei_match or len(re.sub(r"\D", "", imei_match.group(1))) != 15:
            raise forms.ValidationError("Поле IMEI в ГЛОНАСС должно содержать 15 цифр.")

        if not iccid_match or len(re.sub(r"\D", "", iccid_match.group(1))) != 19:
            raise forms.ValidationError("Поле ICCID в ГЛОНАСС должно содержать 19 цифр.")

        return value


class DvsForm(forms.Form):
    dvs = forms.CharField(
        label="ДВС",
        max_length=100,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Отсканируйте или введите номер ДВС"
        })
    )


class BatareyaForm(forms.Form):
    batareya = forms.CharField(
        label="Батарея",
        max_length=100,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Отсканируйте или введите номер батареи"
        })
    )

class PerednijDvigatelForm(forms.Form):
    perednij_dvigatel = forms.CharField(
        label="Передний двигатель",
        max_length=100,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Отсканируйте или введите номер переднего двигателя"
        })
    )


class ZadnijDvigatelForm(forms.Form):
    zadnij_dvigatel = forms.CharField(
        label="Задний двигатель",
        max_length=100,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Отсканируйте или введите номер заднего двигателя"
        })
    )

class ManagerLoginForm(AuthenticationForm):
    shift = forms.ModelChoiceField(
        queryset=Smeny.objects.all(),
        label="Смена",
        empty_label="Выберите смену",
        widget=forms.Select(attrs={"class": "form-control"})
    )

    username = forms.CharField(
        label="Логин",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

class ContainerReceiptForm(forms.ModelForm):
    container_number = forms.CharField(
        label="Номер контейнера",
        max_length=50,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Введите номер контейнера",
            "autocomplete": "off",
        })
    )

    seals_text = forms.CharField(
        label="Номера пломб",
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Например: 123456, 789012",
            "autocomplete": "off",
        })
    )

    photos = MultipleFileField(
        label="Фото контейнера",
        required=False
    )

    class Meta:
        model = ContainerReceipt

        fields = [
            "vehicle_number",
            "components_name",
            "batch_number",
            "package_number",
            "package_marking",
        ]

        widgets = {
            "vehicle_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "А123БВ 777",
                "autocomplete": "off",
            }),
            "components_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Наименование комплектующих изделий",
            }),
            "batch_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Номер партии",
            }),
            "package_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Номер упаковки / количество мест",
            }),
            "package_marking": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Маркировка упаковочной тары",
            }),
        }

    def clean_vehicle_number(self):
        value = self.cleaned_data["vehicle_number"].strip().upper()
        pattern = r"^[АВЕКМНОРСТУХ]\d{3}[АВЕКМНОРСТУХ]{2}\s?\d{2,3}$"

        if not re.match(pattern, value):
            raise forms.ValidationError("Введите номер машины в формате А123БВ 777.")

        return value

    def clean_container_number(self):
        return self.cleaned_data["container_number"].strip().upper()