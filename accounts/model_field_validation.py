from django.core.exceptions import ValidationError


def otp_code_validation(value):
    if value < 10000:
        raise ValidationError("کد یکبار مصرف باید بیش تر از 10000 باشد")

    if value > 99999:
        raise ValidationError("کد یکبار مصرف باید کمتر از 99999 باشد")

    return value