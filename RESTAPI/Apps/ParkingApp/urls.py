from django.urls import path
from django.shortcuts import redirect
from .views import ProtectedView, AdminOnlyView, SocioOnlyView      # Test access endpoints
from .views import obtain_jwt_token, RegisterSocio, Logout_user     # User managing endpoints
from .views import create_parking_lot, list_parking_lots, get_parking_lot, delete_parking_lot, edit_parking_lot
from .views import set_socio_parking, delete_user_parking_relation
from .views import register_vehicle_entry, register_vehicle_exit, list_vehicles_entries, get_vehicles_entries
from .views import top_vehicles_entries


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
]