from django.core.mail import send_mail
from django.conf import settings

def send_verification_email(profile):
    verification_code = profile.generate_verification_code()
    subject = "Verify Your InstaApp Account"
    message = f"Hello {profile.user.username},\n\nYour verification code is: {verification_code}"
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [profile.user.email]

    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=recipient_list,
        fail_silently=False
    )
    return verification_code  