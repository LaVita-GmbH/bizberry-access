import logging

from django.core.management.base import BaseCommand, CommandParser

from bb_access.models.user import UserOTP
from bb_access.models import User


_logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Get OTP for User"

    def add_arguments(self, parser: CommandParser):
        parser.add_argument("user", type=str)
        parser.add_argument("--tenant", type=str, required=False)

    def handle(self, *args, **options):
        user: User
        try:
            user = User.objects.get(email=options["user"])

        except User.MultipleObjectsReturned:
            if options["tenant"]:
                user = User.objects.get(
                    email=options["user"], tenant_id=options["tenant"]
                )

            else:
                raise

        otp = user.request_otp(type=UserOTP.UserOTPType.PIN, is_internal=True)
        print(f"OTP: {otp._value}")
