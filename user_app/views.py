from user_app.serializers import UserSerializer, AuthTokenSerializer
from rest_framework import generics, permissions, authentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

# Create your views here.
class CreateUserView(generics.CreateAPIView):
  """ Crea un nuevo usuario en el sistema """

  serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
  """ Crear un auth token para usuario """

  serializer_class = AuthTokenSerializer
  renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

class ManageUserView(generics.RetrieveUpdateAPIView):
  """ Manejar el usuario autenticado """

  serializer_class = UserSerializer
  authentication_classes = (authentication.TokenAuthentication,)
  permission_classes = (permissions.IsAuthenticated,)

  def get_object(self):
    """ Obtener y retornar el usuario autenticado """
    return self.request.user