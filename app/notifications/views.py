from django.shortcuts import redirect, render

from notifications.models import Notification


def show_notifications(request, *args, **kwargs):
    if not request.user.is_superuser:
        return redirect("/admin")

    if request.method == "POST":
        notification_pk = request.POST.get("primary-key", "")
        Notification.objects.get(pk=notification_pk).notification_read()

    notifications = Notification.objects.filter(is_read=False)
    for notification in notifications:
        notification.message = notification.get_message_display()
    return render(request, "notifications/notifications.html", {"notifications": notifications})
