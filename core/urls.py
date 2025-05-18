from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Authentication URLs
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('verify-email/<uidb64>/<token>/', views.VerifyEmailView.as_view(), name='verify_email'),
    path('resend-verification/', views.resend_verification_email, name='resend_verification'),
    
    # User area
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    
    # Informative pages
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('privacy/', views.PrivacyView.as_view(), name='privacy'),
    path('terms/', views.TermsView.as_view(), name='terms'),
    
    # Features
    path('flights/', views.FlightsView.as_view(), name='flights'),
    path('hotels/', views.HotelsView.as_view(), name='hotels'),
    path('experiences/', views.ExperiencesView.as_view(), name='experiences'),
    path('security/', views.SecurityView.as_view(), name='security'),
    path('membership/', views.MembershipView.as_view(), name='membership'),
    
    # Admin routes
    path('admin-panel/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin-panel/users/', views.AdminUserListView.as_view(), name='admin_users_list'),
    path('admin-panel/users/create/', views.AdminUserCreateView.as_view(), name='admin_users_create'),
    path('admin-panel/users/<int:pk>/', views.AdminUserDetailView.as_view(), name='admin_user_detail'),
    path('admin-panel/users/<int:pk>/edit/', views.AdminUserUpdateView.as_view(), name='admin_users_edit'),
    path('admin-panel/flights/', views.AdminFlightsListView.as_view(), name='admin_flights_list'),
    path('admin-panel/flights/create/', views.AdminFlightFormView.as_view(), name='admin_flights_create'),
    path('admin-panel/hotels/', views.AdminHotelsListView.as_view(), name='admin_hotels_list'),
    path('admin-panel/hotels/create/', views.AdminHotelFormView.as_view(), name='admin_hotels_create'),
    path('admin-panel/payments/', views.AdminPaymentsListView.as_view(), name='admin_payments_list'),
    path('admin-panel/experiences/', views.AdminExperiencesListView.as_view(), name='admin_experiences_list'),
    
    # Home
    path('', views.home, name='home'),
]