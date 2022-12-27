from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

import uuid
import os

from django.conf import settings


def recipe_image_file_patch(instance, filename):
  """ Genera patxh para imagenes """
  ext = filename.split(".")[-1]
  filename = f"{uuid.uuid4()}.{ext}"

  return os.path.join("uploads/recipe/", filename)

# Create your models here.

class UserManager(BaseUserManager):

  def create_user(self, email, password=None, **extra_fields):
    """ Crea y guarda nuevos usuarios """

    if not email:
      raise ValueError("Users mst have an email")

    user = self.model(email=self.normalize_email(email), **extra_fields)
    user.set_password(password)
    user.save(using=self._db)

    return user

  def create_superuser(self, email, password):
    """ Crea y guarda un super usuario """

    user = self.create_user(email=email, password=password)
    user.is_staff = True
    user.is_superuser = True
    user.save(using=self._db)

    return user


class User(AbstractBaseUser, PermissionsMixin):
  """ Modelo personalizado de usuario para hacer login con email y no con username """
  
  email = models.EmailField(max_length=255, unique=True)
  name = models.CharField(max_length=225)
  is_active = models.BooleanField(default=True)
  is_staff = models.BooleanField(default=False)
  
  objects = UserManager()

  USERNAME_FIELD = "email"
  

class Tag(models.Model):
  """ Modelo del Tag para la receta """

  name = models.CharField(max_length=255)
  user = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE
  )

  def __str__(self):
    return self.name
    

class Ingredient(models.Model):
  """ Modelo del ingrediente para la receta """

  name = models.CharField(max_length=255)
  user = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE
  )

  def __str__(self):
    return self.name
    
class Recipe(models.Model):
  """ Receta objeto """

  name = models.CharField(max_length=255)
  user = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE
  )
  title = models.CharField(max_length=255)
  image = models.ImageField(null=True, upload_to=recipe_image_file_patch)
  time_minutes = models.IntegerField()
  price = models.DecimalField(max_digits=5, decimal_places=2)
  link = models.CharField(max_length=255, blank=True)
  ingredients = models.ManyToManyField("Ingredient")
  tags = models.ManyToManyField("Tag")

  def __str__(self):
    return self.title