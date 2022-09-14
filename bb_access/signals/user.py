from datetime import timedelta
from django.dispatch import receiver
from django.db.models.signals import post_save
from ..media_sender import Sender, Content
from .. import models


@receiver(post_save, sender=models.User)
def user_post_save_receiver(sender, instance: models.User, created: bool = False, **kwargs):
    if not created:
        return

    if ... and not instance.has_usable_password():
        instance.request_otp(type=models.UserOTP.UserOTPType.PIN, length=12, validity=timedelta(hours=72))


@receiver(post_save, sender=models.UserOTP)
def user_otp_post_save_receiver(sender, instance: models.UserOTP, created: bool = False, **kwargs):
    if not created:
        return

    MessageSender = Sender.get_sender('SMS' if instance.user.phone and instance.type == models.UserOTP.UserOTPType.PIN else 'EMAIL')
    language = 'de'

    template = f'user_token_{language}.html'
    subject = f''
    destination = instance.user.email
    if instance.type == models.UserOTP.UserOTPType.PIN:
        if instance.user.phone:
            template = f'user_otp_pin_{language}.txt'
            subject = f''
            destination = instance.user.phone

        else:
            template = f'user_otp_pin_{language}.html'

    elif ... and not instance.user.has_usable_password():
        template = f'user_business_{language}.html'
        subject = f'Business Registration'

    message = MessageSender(Content(
        subject=subject,
        receiver=destination,
        template=template,
        language=language,
        values={
            'otp': instance,
            'user': instance.user,
        },
    ))
    message.send()
