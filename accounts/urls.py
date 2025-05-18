from django.urls import path
from rest_framework.routers import DefaultRouter
from django.views.generic import RedirectView
from . import views
from .views import user_profile

router = DefaultRouter()
router.register('users', views.UserViewSet)

urlpatterns = [
    path('profile/', user_profile, name='user-profile'),
    path('membership/', views.MembershipView.as_view(), name='membership-details'),
    path('register/', views.RegisterView.as_view(), name='register'),
    # Redirección para login web
    path('login/', RedirectView.as_view(pattern_name='core:login', permanent=True)),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('password/reset/', views.PasswordResetView.as_view(), name='password-reset'),
    path('password/reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
] + router.urls