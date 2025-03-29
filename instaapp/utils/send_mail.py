from django.core.mail import send_mail
from django.conf import settings

def send_welcome_email(profile):
        subject = "Welcome to InstaApp!"
        message = f"Hello {profile.username},\n\nYour account has been successfully created!"
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [profile.email]

        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
