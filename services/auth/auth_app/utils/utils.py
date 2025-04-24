from django.utils.timezone import now
from auth_app.models import EmailOTPDevice, CustomUser
from django.core.files.storage import default_storage

class CustomError(Exception):
    def __init__(self, message):
        super().__init__(message)

def verifyEmailTOPTDevice(email, otp_token):

	device = EmailOTPDevice.objects.get(email=email, otp_token=otp_token)
	
	if device.valid_until < now():
		raise CustomError("El mensaje OTP ha expirado")
	else:
		return True

def verifyUser(email, password):

	user = CustomUser.objects.filter(email=email).first()  # Buscar el usuario directamente

	if user is None:
		return "Email incorrecto"
	elif not user.check_password(password):
		return "Contraseña incorrecta"
	elif user.is_active == False:
		return "Usuario pendiente de verificación"
	else:
		return "ok"

def verifyPendingUser(email, username, password):

	user = CustomUser.objects.filter(email=email, username= username).first()  # Buscar el usuario directamente

	if user is None:
		return "Usuario incorrecto"
	elif not user.check_password(password):
		return "Contraseña incorrecta"
	elif user.is_active == False:
		return 'ok'
	else:
		return 'error'
	
def removeOldImagen(user):

	defaultName = ["default0.gif", "default1.gif", "default2.gif", "default3.gif", "default4.gif"]

	if user.profile_picture and user.profile_picture not in defaultName:
		old_path = user.profile_picture.replace("/media/", "")

		if default_storage.exists(old_path):
			default_storage.delete(old_path)