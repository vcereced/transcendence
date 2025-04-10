from django.utils.timezone import now
from .utilsToptDevice import CustomError  # Importa tu modelo personalizado
from auth_app.models import EmailOTPDevice, CustomUser
from django.core.files.storage import default_storage

def verifyEmailTOPTDevice(email, otp_token):

	device = EmailOTPDevice.objects.get(email=email, otp_token=otp_token)# if not error throw exception .DoesNotExist
	
	if device.valid_until < now():
		raise CustomError("otp email expired")
	else:
		return True

def verifyUser(email, password):

	user = CustomUser.objects.filter(email=email).first()  # Buscar el usuario directamente

	if user is None:
		return "wrong email"
	elif not user.check_password(password):
		return "password wrong"
	elif user.is_active == False:
		return "user pending to validate"
	else:
		return "ok"

def verifyPendingUser(email, username, password):

	user = CustomUser.objects.filter(email=email, username= username).first()  # Buscar el usuario directamente

	if user is None:
		return "wrong user"
	elif not user.check_password(password):
		return "password wrong"
	elif user.is_active == False:
		return 'ok'
	else:
		return 'error'
	
def removeOldImagen(user):

	defaultName = ["default.gif", "default1.gif", "default2.gif", "default3.gif", "default4.gif"]

	if user.profile_picture and user.profile_picture not in defaultName:
		old_path = user.profile_picture.replace("/media/", "")

		if default_storage.exists(old_path):
			default_storage.delete(old_path)