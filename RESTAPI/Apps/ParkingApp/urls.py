from django.urls import path
from django.shortcuts import redirect
from .views import ProtectedView, AdminOnlyView, SocioOnlyView      # Test access endpoints
from .views import obtain_jwt_token, RegisterSocio, Logout_user     # User managing endpoints
from .views import create_parking_lot, list_parking_lots, get_parking_lot, delete_parking_lot, edit_parking_lot
from .views import set_socio_parking, delete_user_parking_relation
from .views import register_vehicle_entry, register_vehicle_exit, list_vehicles_entries, get_vehicles_entries
from .views import top_vehicles_entries, top_vehicles_entries_parking, first_time_vehicles_parking, incomes_last_days_parking, incomes_summary_parking
from .views import top_socios_vehicles_entries, top_3_socios_vehicles_entries_week, top_parking_lots_incomes
from .views import send_mail


urlpatterns = [
    path('api/login/', obtain_jwt_token, name='log-in'),
    path('api/protected/', ProtectedView.as_view(), name='protected'),
    path('api/admin-only/', AdminOnlyView.as_view(), name='admin-only'),
    path('api/socio-only/', SocioOnlyView.as_view(), name='socio-only'),
    path('api/register-socio/', RegisterSocio, name='register-socio'),
    path('api/logout/', Logout_user, name='log-out'),
    path('api/create-parking-lot/', create_parking_lot, name='create-parking-lot'),
    path('api/parking-lots/', list_parking_lots, name='parking-lots'),
    path('api/parking-lots/<int:id>', get_parking_lot, name='parking-lot'),
    path('api/delete-parking-lot/<int:id>', delete_parking_lot, name='delete-parking-lot'),
    path('api/edit-parking-lot/<int:id>', edit_parking_lot, name='edit-parking-lot'),
    path('api/set-socio-parking/', set_socio_parking, name='set-socio-parking'),
    path('api/delete-socio-parking/<int:id>', delete_user_parking_relation, name='delete-socio-parking'),
    path('api/register-vehicle-entry/', register_vehicle_entry, name='register-vehicle-entry'),
    path('api/register-vehicle-exit/', register_vehicle_exit, name='register-vehicle-exit'),
    path('api/vehicles-entries/', list_vehicles_entries, name='vehicles-entries'),
    path('api/vehicles-entries/<int:id>', get_vehicles_entries, name='vehicles-entries-parking'),
    path('api/top-<int:top>-vehicles-entries/', top_vehicles_entries, name='top_vehicles_entries'),
    path('api/top-<int:top>-vehicles-entries/<int:id>', top_vehicles_entries_parking, name='top_vehicles_entries_parking'),
    path('api/first-time-vehicles/<int:id>', first_time_vehicles_parking, name='first_time_vehicles_parking'),
    path('api/incomes-last-<int:days>-days-parking-lot/<int:id>', incomes_last_days_parking, name='incomes_last_days_parking'),
    path('api/incomes-parking-lot/<int:id>', incomes_summary_parking, name='incomes_summary_parking'),
    path('api/top-<int:top>-socios-vehicles-entries/last-<int:days>-days/', top_socios_vehicles_entries, name='top_socios_vehicles_entries'),
    path('api/top-socios-vehicles-entries/', top_3_socios_vehicles_entries_week, name='top_socios_3_vehicles_entries_week'),
    path('api/top-<int:top>-parking-lots-incomes/', top_parking_lots_incomes, name='top_parking_lots_incomes'),
    path('api/send-mail/', send_mail, name='send_mail'),
]