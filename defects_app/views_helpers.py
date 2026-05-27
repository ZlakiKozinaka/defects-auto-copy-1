from defects_app.models import Mesta


def get_station_redirect_name(station_id):
    station_map = {
        1: "home",
        2: "okline",
        13: "vh1",
        3: "telematika_glonass",
        4: "telematika_glonass",
        5: "agregaty",
        6: "agregaty",
        7: "agregaty",
        11: "dovodka",
        12: "create_car",
    }

    if station_id in [8, 9, 10]:
        return "quality"

    return station_map.get(station_id, "home")


def is_vh1_station(station_id=None, station_name=None):
    if station_id == 13:
        return True

    if not station_name:
        return False

    normalized_name = str(station_name).strip().lower().replace("-", " ")
    normalized_name = " ".join(normalized_name.split())
    return normalized_name in {"вх 1", "вх1", "входной контроль 1"}


def get_vh1_station():
    stations = Mesta.objects.all()
    for station in stations:
        if is_vh1_station(station_id=station.id, station_name=station.nazvanie):
            return station
    return None