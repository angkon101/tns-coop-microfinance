from .models import Notification
from apps.accounts.models import CustomUser

def notify_user(user, title, message, link='', notification_type='INFO'):
    """Create a single notification for a specific user."""
    if user and user.is_authenticated:
        return Notification.objects.create(
            user=user,
            title=title,
            message=message,
            link=link or '',
            notification_type=notification_type
        )
    return None

def notify_role(role, title, message, link='', notification_type='INFO'):
    """Create notifications for all active users with a given role."""
    users = CustomUser.objects.filter(role=role, is_active=True)
    notifications = [
        Notification(
            user=u,
            title=title,
            message=message,
            link=link or '',
            notification_type=notification_type
        )
        for u in users
    ]
    if notifications:
        Notification.objects.bulk_create(notifications)

def notify_staff_and_admins(title, message, link='', notification_type='INFO'):
    """Notify all Officers, Admins, and Superusers."""
    users = CustomUser.objects.filter(role__in=['ADMIN', 'OFFICER'], is_active=True)
    notifications = [
        Notification(
            user=u,
            title=title,
            message=message,
            link=link or '',
            notification_type=notification_type
        )
        for u in users
    ]
    if notifications:
        Notification.objects.bulk_create(notifications)
