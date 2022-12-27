from rest_framework import viewsets, mixins, status
from rest_framework.authentication import   TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from rest_framework.decorators import action
from rest_framework.response import Response

from app_core.models import Tag, Ingredient, Recipe
from recipe_app import serializers



# Create your views here.

class BaseRecipeAttrViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
  """ ViewSet Base """

  authentication_classes = (TokenAuthentication, )
  permission_classes = (IsAuthenticated, )

  def get_queryset(self):
    """ Retornar objetos para el usuario autenticado """
    assigned_only = bool(
      int(self.request.query_params.get("assigned_only", 0))
    )
    queryset = self.queryset

    if assigned_only:
      queryset = queryset.filter(recipe__isnull= False)

    return queryset.filter(
      user=self.request.user
    ).order_by("-name").distinct()


  def perform_create(self, serializer):
    """ Crear nuevo tag """

    serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAttrViewSet):
  """ Manejar Tags en base de datos """

 
  queryset = Tag.objects.all()
  serializer_class = serializers.TagSerializer


class IngredientViewSet(BaseRecipeAttrViewSet):
  """ Manejar Ingredientes en base de datos """

  queryset = Ingredient.objects.all()
  serializer_class = serializers.IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
  """ Manejar las recetas en la base de datos """

  serializer_class = serializers.RecipeSerializer
  queryset = Recipe.objects.all()
  authentication_classes = (TokenAuthentication, )
  permission_classes = (IsAuthenticated, )

  def get_queryset(self):
    """ Retornar objetos para el usuario autenticado """
    
    return self.queryset.filter(user=self.request.user)

  def get_serializer_class(self):
    """ Retorna clases de serializador apropiado """

    if self.action == "retrieve":
      return serializers.RecipeDetailSerializer

    elif self.action == "upload_image":
      return serializers.RecipeImageSerializer
      
    return self.serializer_class

  def perform_create(self, serializer):
    """ Crear nuevo tag """

    serializer.save(user=self.request.user)

  @action(methods=["POST"], detail=True, url_path="upload-image")
  def upload_image(self, request, pk=None):
    """ Subir imagen a receta """

    recipe = self.get_object()
    serializer = self.get_serializer(recipe, data=request.data)

    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


  def _params_to_ints(self, qs):
    """ Convertir lista string IDs a lista de integers """

    return [int(str_id) for str_id in qs.split(",")]

  def get_queryset(self):
    """ Obtener recetas para el usuario autenticado"""

    tags = self.request.query_params.get("tags")
    ingredients = self.request.query_params.get("ingredients")
    queryset = self.queryset

    if tags:
      tag_ids = self._params_to_ints(tags)
      queryset = queryset.filter(tags__id__in=tag_ids)
  
    if ingredients:
      ingredient_ids = self._params_to_ints(ingredients)
      queryset = queryset.filter(ingredients__id__in=ingredient_ids)
  
    return queryset.filter(user=self.request.user)