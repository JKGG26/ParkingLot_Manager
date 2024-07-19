from django.urls import path
from .views import obtain_jwt_token, ProtectedView, AdminOnlyView, SocioOnlyView, RegisterSocio, Logout_user


urlpatterns = [
    path('api/login/', obtain_jwt_token, name='log-in'),
    path('api/protected/', ProtectedView.as_view(), name='protected'),
    path('api/admin-only/', AdminOnlyView.as_view(), name='admin-only'),
    path('api/socio-only/', SocioOnlyView.as_view(), name='socio-only'),
    path('api/register-socio/', RegisterSocio, name='register-socio'),
    path('api/logout/', Logout_user, name='log-out'),
]