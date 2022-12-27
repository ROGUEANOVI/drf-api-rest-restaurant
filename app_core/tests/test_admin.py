from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

class AdminSiteTest(TestCase):

  def setUp(self):

    self.client = Client()

    email = "testsuperuser@gmail.com"
    password = "testpass000"
    self.admin_user = get_user_model().objects.create_superuser(
      email=email,
      password=password
    )
    self.client.force_login(self.admin_user)

    email = "testuser@gmail.com"
    password = "testpass000"
    name = "Test user"
    self.user = get_user_model().objects.create_user(
      email=email,
      password=password,
      name=name
    )


  def test_users_listed(self):
    """ Testear que los usuarios han sido enlistados en la pagina de usuarios """

    url = reverse('admin:app_core_user_changelist')
    res = self.client.get(url)

    self.assertContains(res, self.user.name)
    self.assertContains(res, self.user.email)


  def test_user_change_page(self):
    """ Prueba que la pagina editada por el usuario funciona """

    # We have to include fieldssets to UserAdmin for this to work
    url = reverse('admin:app_core_user_change', args=[self.user.id])
    # /admin/core/user/1
    res = self.client.get(url)

    self.assertEqual(res.status_code, 200)


  def test_create_user_page(self):
    """ Testear que la pagina de crear usuario funciona """
    
    url = reverse('admin:app_core_user_add')
    response = self.client.get(url)

    self.assertEqual(response.status_code, 200)