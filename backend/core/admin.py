from django.contrib import admin, messages

from .models import EmailLog


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "kind", "to_email", "subject", "status", "attempts")
    list_filter = ("status", "kind")
    search_fields = ("to_email", "subject")
    readonly_fields = [f.name for f in EmailLog._meta.fields]
    actions = ["retry_failed"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.action(description="Retry sending selected emails")
    def retry_failed(self, request, queryset):
        from .tasks import deliver_email

        count = 0
        for log in queryset.exclude(status=EmailLog.Status.SENT):
            deliver_email.delay(log.pk)
            count += 1
        self.message_user(request, f"Queued {count} email(s) for sending.", messages.INFO)
