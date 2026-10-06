from django.core.validators import ValidationError


def price_validation(value):  # validates price
    if value < 100000:  # if price is below 10k....
        raise ValidationError('قیمت زیر 100000 نیست')  # raises error
    return value


def discount_validation(value):  # validates discount field
    if value > 100:  # if value is bigger than 1000...
        raise ValidationError('تخفیف بیش تر از 100 نیست')  # raises error
    if value < 0:  # if it's less than zero
        raise ValidationError('تخفیف کمتر از 0 نیست')  # raises error

    return value