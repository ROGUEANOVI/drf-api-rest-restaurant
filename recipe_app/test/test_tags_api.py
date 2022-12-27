from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from app_core.models import Tag, Recipe

from recipe_app.serializers import TagSerializer

TAG_URL = reverse("recipe_app:tag-list")


class PublicTagsApiTests(TestCase):
  """ Probar los API tags disponibles publicamente """

  def setUp(self):
    self.client = APIClient()

  def test_login_required(self):
    """ Prueba que login sea requerido para obtener los tags """

    res = self.client.get(TAG_URL)
    self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
  """ Probar los API tags disponibles privados """

  def setUp(self):
    self.user = get_user_model().objects.create_user(
      "test@gmail.com",
      "password"
    )
    self.client = APIClient()
    self.client.force_authenticate(self.user)


  def test_retrieve_tags(self):
    """ Probar obtener tags """

    Tag.objects.create(user= self.user, name="Meat")
    Tag.objects.create(user= self.user, name="Banana")

    res = self.client.get(TAG_URL)

    tags = Tag.objects.all().order_by("-name")
    serializer = TagSerializer(tags, many=True)

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data, serializer.data)

  def test_tags_limited_to_user(self):
    """ Probar que los tags que retornamos sean del usuario """

    user2 = get_user_model().objects.create_user(
      "otrotest@gmail.com",
      "testpass"
    )

    Tag.objects.create(user=user2, name="Rasberry")
    tag = Tag.objects.create(user=self.user, name="confort Food")

    res = self.client.get(TAG_URL)

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(len(res.data), 1)
    self.assertEqual(res.data[0]["name"], tag.name)


  def test_create_tag_successful(self):
    """ Prueba creando nuevo tag """

    payload =  {"name": "Simple"}
    self.client.post(TAG_URL, payload)

    exists = Tag.objects.filter(
      user=self.user,
      name=payload["name"]
    ).exists()
    
    self.assertTrue(exists)
  
  def test_create_tag_invalid(self):
    """ Prueba creando nuevo tag con payload invalido """

    payload =  {"name": ""}
    res = self.client.post(TAG_URL, payload)

    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    
  def test_retrieve_tags_assigned_to_recipes(self):
    """ Prueba filtrando tags basados en recetas """

    tag1 = Tag.objects.create(user=self.user, name="Breakfast")
    tag2 = Tag.objects.create(user=self.user, name="Lunch")

    recipe = Recipe.objects.create(
      title= "Coriander eggs on toast",
      time_minutes = 10,
      price= 5.00,
      user= self.user,
    )

    recipe.tags.add(tag1)

    res = self.client.get(TAG_URL, {"assigned_only":1})

    serializer1 =  TagSerializer(tag1)
    serializer2 =  TagSerializer(tag2)

    self.assertIn(serializer1.data, res.data)
    self.assertNotIn(serializer2.data, res.data)

  def test_retrieve_tags_assigned_unique(self):
    """ Prueba filtro tags asignado por items unicos """

    tag = Tag.objects.create(user=self.user, name="Breakfast")
    
    recipe1 = Recipe.objects.create(
      title="Pancakes",
      time_minutes= 5,
      price= 3.00,
      user= self.user
    )
    recipe1.tags.add(tag)

    recipe2 = Recipe.objects.create(
      title="Porridge",
      time_minutes= 3,
      price= 2.00,
      user= self.user
    )
    recipe2.tags.add(tag)

    res = self.client.get(TAG_URL, {"assigned_only":1})

    self.assertEqual(len(res.data), 1)