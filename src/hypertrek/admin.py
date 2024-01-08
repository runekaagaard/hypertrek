from django.contrib import admin
from .models import TrekState

@admin.register(TrekState)
class TrekStateAdmin(admin.ModelAdmin):
    list_display = ('added', 'added_by', 'added_by', 'updated_by', 'uuid')
    readonly_fields = ('added', 'updated', 'added_by', 'updated_by', 'uuid', 'value')
    date_hierarchy = 'updated'
