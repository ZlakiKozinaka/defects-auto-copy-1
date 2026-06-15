from django import forms

from defects_app.models import WmsLot, WmsPalletType, WmsStorageCell
from defects_app.services.wms_storage import get_position_choices_for_pallet_type


class WmsLotUploadForm(forms.Form):
    source_file = forms.FileField(
        label="Excel-файл лота",
        widget=forms.FileInput(attrs={
            "class": "form-control",
            "accept": ".xlsx,.xlsm,.xltx,.xltm",
        })
    )
    lot_number = forms.CharField(
        label="Номер лота",
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            "class": "form-control form-control-lg",
            "placeholder": "Например: D/MY19-25003-08",
            "autocomplete": "off",
        })
    )
    comment = forms.CharField(
        label="Комментарий",
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3})
    )

    def clean_source_file(self):
        source_file = self.cleaned_data["source_file"]
        allowed = (".xlsx", ".xlsm", ".xltx", ".xltm")
        if not source_file.name.lower().endswith(allowed):
            raise forms.ValidationError("Загрузите Excel-файл в формате .xlsx/.xlsm.")
        return source_file

    def clean_lot_number(self):
        return self.cleaned_data.get("lot_number", "").strip()


class WmsLotScanForm(forms.Form):
    lot_number = forms.CharField(
        label="Скан лота / номер лота",
        max_length=100,
        widget=forms.TextInput(attrs={
            "class": "form-control form-control-lg",
            "placeholder": "Отсканируйте QR-код лота",
            "autocomplete": "off",
            "autofocus": True,
        })
    )

    def clean_lot_number(self):
        return self.cleaned_data["lot_number"].strip()


class WmsContainerSearchForm(forms.Form):
    container_number = forms.CharField(
        label="Номер контейнера",
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            "class": "form-control form-control-lg",
            "placeholder": "Отсканируйте или введите контейнер",
            "autocomplete": "off",
        })
    )

    def clean_container_number(self):
        return self.cleaned_data.get("container_number", "").strip().upper()


class WmsContainerPlacementForm(forms.Form):
    pallet_type = forms.ModelChoiceField(
        label="Тип поддона",
        queryset=WmsPalletType.objects.filter(is_active=True).order_by("name"),
        empty_label="Выберите тип поддона",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    cell = forms.ModelChoiceField(
        label="Ячейка",
        queryset=WmsStorageCell.objects.filter(
            is_active=True,
            line__is_active=True,
            line__warehouse__is_active=True,
            line__warehouse__site__is_active=True,
        )
        .select_related("line", "line__warehouse")
        .order_by("line__sort_order", "line__code", "column_number", "level_number"),
        empty_label="Выберите ячейку",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    position = forms.ChoiceField(
        label="Позиция",
        choices=(),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    pallet_number = forms.CharField(
        label="Номер поддона",
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Необязательно"}),
    )
    comment = forms.CharField(
        label="Комментарий",
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pallet_type = None
        cell = None

        data = self.data if self.is_bound else None
        if data:
            pallet_type_id = data.get("pallet_type")
            cell_id = data.get("cell")
            if pallet_type_id:
                pallet_type = WmsPalletType.objects.filter(id=pallet_type_id, is_active=True).first()
            if cell_id:
                cell = WmsStorageCell.objects.filter(id=cell_id).select_related("line").first()

        if pallet_type and cell:
            self.fields["position"].choices = get_position_choices_for_pallet_type(cell, pallet_type)
        elif pallet_type:
            self.fields["position"].choices = get_position_choices_for_pallet_type(None, pallet_type)
        else:
            self.fields["position"].choices = [
                ("1-2", "Евро: Лево [1-2]"),
                ("3-4", "Евро: Центр [3-4]"),
                ("5-6", "Евро: Право [5-6]"),
                ("1-3", "Нестандартный: Левая половина [1-3]"),
                ("4-6", "Нестандартный: Правая половина [4-6]"),
            ]

    def clean_position(self):
        value = self.cleaned_data["position"]
        try:
            start, end = value.split("-")
            return int(start), int(end)
        except (ValueError, AttributeError):
            raise forms.ValidationError("Выберите корректную позицию.")
        
class WmsCaseSuggestedPlacementForm(forms.Form):
    pallet_type = forms.ModelChoiceField(
        label="Тип поддона",
        queryset=WmsPalletType.objects.filter(is_active=True).order_by("name"),
        empty_label=None,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    selected_place = forms.CharField(
        widget=forms.HiddenInput()
    )

    pallet_number = forms.CharField(
        label="Номер поддона",
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Необязательно"})
    )

    comment = forms.CharField(
        label="Комментарий",
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2})
    )

    def clean_selected_place(self):
        value = self.cleaned_data["selected_place"]

        try:
            cell_id, position_from, position_to = value.split("|")
            return int(cell_id), int(position_from), int(position_to)
        except (ValueError, AttributeError):
            raise forms.ValidationError("Некорректное выбранное место.")
        
import re
from django import forms


class WmsStorageLineCreateForm(forms.Form):
    line_code = forms.CharField(
        label="Буква стеллажа",
        max_length=1,
        help_text="Только английская буква: A, B, C..."
    )

    columns_count = forms.IntegerField(
        label="Количество столбцов",
        min_value=1,
        max_value=100,
    )

    levels_count = forms.IntegerField(
        label="Количество этажей",
        min_value=1,
        max_value=20,
    )

    capacity_units = forms.IntegerField(
        label="Вместимость одной ячейки, units",
        min_value=1,
        max_value=20,
        initial=6,
    )

    def clean_line_code(self):
        value = self.cleaned_data["line_code"].strip().upper()

        if not re.fullmatch(r"[A-Z]", value):
            raise forms.ValidationError("Можно использовать только одну английскую букву: A, B, C...")

        return value
    

class WmsCaseManualPlacementForm(forms.Form):
    pallet_type = forms.ModelChoiceField(
        label="Тип поддона",
        queryset=WmsPalletType.objects.filter(is_active=True).order_by("name"),
        empty_label=None,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    cell_address = forms.CharField(
        label="Штрихкод / адрес ячейки",
        max_length=50,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Отсканируйте ячейку, например A1;1",
            "autocomplete": "off",
        })
    )

    pallet_number = forms.CharField(
        label="Номер поддона",
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Необязательно",
        })
    )

    comment = forms.CharField(
        label="Комментарий",
        required=False,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 2,
        })
    )

    def clean_cell_address(self):
        return self.cleaned_data["cell_address"].strip().upper()