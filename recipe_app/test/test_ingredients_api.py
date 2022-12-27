from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from app_core.models import Ingredient

from recipe_app.serializers import IngredientSerializer

INGREDIENT_URL = reverse("recipe_app:ingredient-list")

class PublicIngredientsApiTest(TestCase):
  """ Probar API ingredientes accesible publicamente """

  def setUp(self):
    self.client = APIClient()

  def test_login_required(self):
    """ Probar que login es necesario para acceder a este endpoint """
    res = self.client.get(INGREDIENT_URL)

    self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTest(TestCase):
  """ Probar API ingredientes accesible privado """
  
  def setUp(self):
    self.client = APIClient()
    self.user = get_user_model().objects.create_user(
      "test@gmail.com",
      "testpass"
    )
    self.client.force_authenticate(self.user)

  def test_retrieve_ingredient_list(self):
    """ Probar obtener listado de ingredientes """

    Ingredient.objects.create(user=self.user, name="milk")
    Ingredient.objects.create(user=self.user, name="cheese")

    res = self.client.get(INGREDIENT_URL)

    ingredients = Ingredient.objects.all().order_by("-name")
    serializer = IngredientSerializer(ingredients, many=True)

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data, serializer.data)

  def test_ingredients_limited_to_user(self):
    """ Probar retornar ingredientes solamente autenticados por el usuario """

    user2 = get_user_model().objects.create_user(
      "other@gmail.com",
      "testpass"
    )
    Ingredient.objects.create(user=user2, name="Vinegar") 
    ingredient = Ingredient.objects.create(user=self.user, name="tumeric")

    res = self.client.get(INGREDIENT_URL)

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(len(res.data), 1)
    self.assertEqual(res.data[0]["name"], ingredient.name)

  def test_create_ingredient_succesful(self):
    """ Probar crear nuevo ingrediente """

    payload = {"name": "Chocolate"}
    self.client.post(INGREDIENT_URL, payload)
    
    exists = Ingredient.objects.filter(user=self.user, name=payload["name"]).exists()
    
    self.assertTrue(exists)

  def test_create_ingredient_invalid(self):
    """ Probar crear un ingredinete vacio """

    payload = {"name": ""}
    res = self.client.post(INGREDIENT_URL, payload)

    self.assertEqual( res.status_code, status.HTTP_400_BAD_REQUEST)