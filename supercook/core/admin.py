from django.contrib import admin
from .models import Ingredient, Recipe, RecipeIngredient, Favorite


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "category")
    search_fields = ("name", "category")


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("title", "url")
    search_fields = ("title",)
    inlines = [RecipeIngredientInline]


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe", "created_at")
    search_fields = ("user__username", "recipe__title")
