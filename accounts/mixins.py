from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect

class ClientRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_client()
    def handle_no_permission(self):
        return redirect('core:login')

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and (self.request.user.is_admin() or self.request.user.is_superadmin())
    def handle_no_permission(self):
        return redirect('core:login')

class SuperAdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_superadmin()
    def handle_no_permission(self):
        return redirect('core:login') 