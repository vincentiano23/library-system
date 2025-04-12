from django.contrib import admin
from .models import Student, Visit 

class VisitInline(admin.TabularInline):
    model = Visit  
    extra = 0  
    fields = ('visit_time',) 
    readonly_fields = ('visit_time',) 

class StudentAdmin(admin.ModelAdmin):
    list_display = ('registration_number', 'full_name', 'email')  
    search_fields = ('registration_number', 'full_name', 'email') 
    list_filter = ('user__is_active',)  
    inlines = [VisitInline]  

    fieldsets = (
        (None, {
            'fields': ('registration_number', 'full_name', 'user', 'email') 
        }),
    )

admin.site.register(Student, StudentAdmin)
admin.site.register(Visit) 