from typing import Optional
from django.utils import timezone
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from djfapi.schemas import Error
from djfapi.exceptions import ValidationError
from ..models import User, UserOTP


class UserOTPBackend(BaseBackend):
    def authenticate(self, request, password: Optional[str] = None, **kwargs) -> Optional[User]:
        otp: UserOTP
        try:
            user = User.objects.get(**kwargs)

        except (User.DoesNotExist):
            return None

        else:
            otps = user.otps.filter(expire_at__gte=timezone.now(), used_at__isnull=True)
            for otp in otps:
                if otp.type == UserOTP.UserOTPType.PIN and check_password(password, otp.value):
                    otp.used_at = timezone.now()
                    otp.save(update_fields=['used_at',])
                    return otp.user

                elif otp.type == UserOTP.UserOTPType.TOKEN and check_password(password, otp.value):
                    raise ValidationError(detail=Error(code='cannot_login_using_otp_type_token', detail={'id': otp.id}))

            return None
