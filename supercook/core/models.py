from django.db import models
from django.contrib.auth import get_user_model


class Ingredient(models.Model):
    name = models.CharField(max_length=120, unique=True)
    category = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    title = models.CharField(max_length=200)
    instructions = models.TextField(blank=True)
    url = models.URLField(blank=True)

    def __str__(self) -> str:
        return self.title


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="recipe_ingredients")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name="ingredient_recipes")
    quantity = models.CharField(max_length=120, blank=True)

    class Meta:
        unique_together = ("recipe", "ingredient")


User = get_user_model()


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "recipe")

# Create your models here.
