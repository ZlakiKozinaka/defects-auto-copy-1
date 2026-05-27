from defects_app.views.defect_views import (
    home,
    create_defect,
    check_vin,
    edit_defect,
    delete_defect,
    okline_view,
    complete_bestenevaya,
    quality_view,
    vh1_view,
    dovodka_view,
    snp_orders_view,
)

from defects_app.views.logistics_views import (
    create_car_view,
    print_created_car_view,
    print_created_car_info_view,
    print_created_car_info_batch_view,
)

from defects_app.views.aggregate_views import (
    telematika_view,
    glonass_view,
    telematika_glonass_view,
    batareya_view,
    perednij_dvigatel_view,
    zadnij_dvigatel_view,
    agregaty_view,
)

from defects_app.views.auth_views import (
    custom_login_view,
    manager_login_view,
    department_hub_view,
    department_section_view,
    csrf_failure_view,
)

from defects_app.views.report_views import (
    manager_dashboard_view,
    manager_open_station_view,
    manager_open_vh1_station_view,
    print_sgp_report_view,
    upload_plan_vin_view,

    exports_view,
    export_defects_view,
    export_created_cars_view,

    reports_view,
    oee_report_view,
    oee_print_view,
    qrqc_dashboard_view,

    qrqc_oee_api_view,
    qrqc_dphu_api_view,
    qrqc_top_defects_api_view,
    qrqc_snp_api_view,

    top_defects_report_view,
    top_defects_api_view,
    dphu_report_view,
    qrqc_print_view,

    production_plans_view,
    bestenevaya_timer_api_view,
    export_qrqc_production_view,

    live_cars_view,
    logistics_live_cars_view,

    upload_old_snp_cars_view,
    export_snp_cars_view,
    export_full_cars_view,
    qrqc_direct_pass_api_view,
    defect_types_dashboard_view,
    defect_types_dashboard_api_view,
    export_defect_types_dashboard_view,
)

from defects_app.views.station_views import (
    open_station_for_department_view,
    open_vh1_station_for_department_view,
)

from defects_app.views.vin_views import (
    vin_prefixes_api_view,
    vin_model_api_view,
)

from defects_app.views.photo_views import (
    defect_photo_detail_view,
)