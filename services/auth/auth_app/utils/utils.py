from django_otp.plugins.otp_totp.models import TOTPDevice
from rest_framework.response import Response
from rest_framework import status
import qrcode
import base64
from io import BytesIO

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
		return Response({"error": "No hay configuración de 2FA pendiente."}, status=status.HTTP_400_BAD_REQUEST)
	
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
		return Response({'error': 'No tiene activado 2FA esta cuenta.'}, status=status.HTTP_401_UNAUTHORIZED)

	if not totp_device.verify_token(otp_token):
		return Response({'error': 'Código OTP incorrecto.'}, status=status.HTTP_400_BAD_REQUEST)
	else:
		return True