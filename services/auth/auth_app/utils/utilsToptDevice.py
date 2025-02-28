from django_otp.plugins.otp_totp.models import TOTPDevice
from rest_framework.response import Response
from rest_framework import status
import qrcode
import base64
from io import BytesIO


class CustomError(Exception):
    def __init__(self, message):
        super().__init__(message)


#argument must be the user serialized(username and password)
def genTOPTDevice(user):

    # Crear un dispositivo TOTP para el usuario
    totp_device = TOTPDevice.objects.create(user=user, confirmed=False)

    # Generar URL para Google Authenticator
    otp_url = totp_device.config_url

    # Generar QR code
    qr = qrcode.make(otp_url)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return qr_base64

def activateTOPTDevice(user, otp_token):
	# Buscar el dispositivo TOTP del usuario
	try:
		totp_device = TOTPDevice.objects.get(user=user, confirmed=False)
	except TOTPDevice.DoesNotExist:
		raise CustomError("2FA activated already")

	# Verificar OTP
	if totp_device.verify_token(otp_token):
		totp_device.confirmed = True  # Confirmamos que el dispositivo es válido
		totp_device.save()
		return True
	else:
		return False

def verifyTOPTDevice(user, otp_token):

	try:
		totp_device = TOTPDevice.objects.get(user=user, confirmed=True)
	except TOTPDevice.DoesNotExist:
		raise CustomError("this account dont have 2FA activated")

	if not totp_device.verify_token(otp_token):
		raise CustomError("OTP code wrong!!")
	else:
		return True


