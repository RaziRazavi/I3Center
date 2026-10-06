import random
from kavenegar import *
from accounts.models import OtpCode


def send_sms(phone_number, code):
    try :
        api = KavenegarAPI('506358774350617153756651767A67334C472F376471586766684C416C67762F786453456176684E4456553D')
        params = {
            'sender' : '2000660110',
            'receptor' : phone_number,  # due to webservice's policy, it only works on my phone number - 09377775352
            'message' : 'کد ورود شما به سایت' + str(code),
        }
        response = api.sms_send(params)
        return response
    except APIException as e:
        print(e)
    except HTTPException as e:
        print(e)


def get_client_ip_address(request):
    ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
    if ip_address is not None:
        return ip_address

    return request.META.get('REMOTE_ADDR')


def create_unique_otp_code():
    while True:
        code  = random.randint(10000, 99999)
        if not OtpCode.objects.filter(code=code).exists():
            return code