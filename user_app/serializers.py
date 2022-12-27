from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
  """ Serializador para el objeto Usuario """

  class Meta:
    model = get_user_model()
    fields = ("email", "password", "name")
    extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

  def create(self, validated_data):
    """ Crear nuevo usuario con clave encriptada y retornarlo """

    return get_user_model().objects.create_user(**validated_data)

  def update(self, instance, validated_data):
    """ Actualiza al usuario, configura el password correctamente y lo retorna """

    password = validated_data.pop("password", None)

    user = super().update(instance, validated_data)

    if password:
      user.set_password(password)
      user.save()
  
    return user

class AuthTokenSerializer(serializers.Serializer):
  """ Serializador para el objeto de autenticacion del usuario """

  email = serializers.CharField()
  password = serializers.CharField(
    style={"input_type":"password"},
    trim_whitespace=False
  )

  def validate(self, attrs):
    """ Validar y aunteticar usuario """

    email = attrs.get("email")
    password = attrs.get("password")

    user = authenticate(
      request=self.context.get("request"),
      username = email,
      password = password
    )

    if not user:
      msg = _("Unable to autheticate with provided credentials")
      raise serializers.ValidationError(msg, code="authorization")

    attrs["user"] = user
    return attrs