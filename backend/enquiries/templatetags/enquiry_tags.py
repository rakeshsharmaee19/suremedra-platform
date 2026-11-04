from django import template

from enquiries.models import Enquiry, Notification

register = template.Library()


@register.inclusion_tag("enquiries/dashboard_panel.html", takes_context=True)
def enquiry_panel(context):
    request = context["request"]
    user = request.user
    if not user.is_authenticated or not user.has_perm("enquiries.view_enquiry"):
        return {"show": False}
    unread = Notification.objects.filter(user=user, read_at__isnull=True).select_related("enquiry")
    return {
        "show": True,
        "new_count": Enquiry.objects.filter(status=Enquiry.Status.NEW).count(),
        "unread_count": unread.count(),
        "notifications": unread[:8],
    }
