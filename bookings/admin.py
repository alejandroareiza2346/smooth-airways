from django.contrib import admin
from .models import Aircraft

@admin.register(Aircraft)
class AircraftAdmin(admin.ModelAdmin):
    list_display = ('name', 'model', 'capacity', 'status')
    list_filter = ('status',)
    search_fields = ('name', 'model')