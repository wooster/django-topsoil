from django.contrib import admin
from models import OAuthApplication
from oauth_provider.consts import ACCEPTED, REJECTED

class OAuthApplicationAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization_name', 'approval_status', 'read_permission', 'write_permission', 'delete_permission', 'login_permission']
    ordering = ['id']
    actions = ['approve_consumer', 'reject_consumer']
    
    def _new_approval_status(self, request, queryset, new_status):
        rows_updated = 0
        for row in queryset:
            rows_updated += 1
            row.consumer.status = new_status
            row.consumer.save()
        return rows_updated
    
    def approve_consumer(self, request, queryset):
        # !! Should also send a notification email.
        self._new_approval_status(request, queryset, ACCEPTED)
    approve_consumer.short_description = 'Approve Consumer'

    def reject_consumer(self, request, queryset):
        # !! Should also send a notification email.
        self._new_approval_status(request, queryset, REJECTED)
    reject_consumer.short_description = 'Reject Consumer'

admin.site.register(OAuthApplication, OAuthApplicationAdmin)
