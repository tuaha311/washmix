from django.shortcuts import redirect, render

from notifications.models import Notification


def show_notifications(request, *args, **kwargs):
    if not request.user.is_superuser:
        return redirect("/admin")

    if request.method == "POST":
        notification_pk = request.POST.get("primary-key", "")
        if notification_pk:
            Notification.objects.get(pk=notification_pk).notification_read()

    notifications = Notification.objects.filter(is_read=False)
    read_notifications = Notification.objects.filter(is_read=True).order_by("-created")[:10]
    for notification in notifications:
        notification.message = notification.get_message_display()
    for read in read_notifications:
        read.message = read.get_message_display()
    return render(
        request,
        "notifications/notifications.html",
        {"notifications": notifications, "read_notifications": read_notifications},
    )
