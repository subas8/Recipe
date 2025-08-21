from django.core.management.base import BaseCommand
from core.models import Ingredient, Recipe, RecipeIngredient


class Command(BaseCommand):
    help = "Seed sample ingredients and recipes"

    def handle(self, *args, **options):
        ingredients = [
            ("egg", "dairy"),
            ("milk", "dairy"),
            ("flour", "baking"),
            ("sugar", "baking"),
            ("butter", "dairy"),
            ("salt", "spices"),
            ("tomato", "produce"),
            ("onion", "produce"),
            ("garlic", "produce"),
            ("pasta", "grains"),
            ("cheese", "dairy"),
            ("chicken", "meat"),
            ("rice", "grains"),
            ("beans", "canned"),
            ("olive oil", "oils"),
        ]

        name_to_obj = {}
        for name, cat in ingredients:
            obj, _ = Ingredient.objects.get_or_create(name=name, defaults={"category": cat})
            name_to_obj[name] = obj

        recipes = [
            ("Pancakes", "https://example.com/pancakes", ["egg", "milk", "flour", "sugar", "salt", "butter"]),
            ("Simple Pasta", "https://example.com/pasta", ["pasta", "tomato", "garlic", "olive oil", "salt"]),
            ("Grilled Cheese", "https://example.com/grilled-cheese", ["bread", "butter", "cheese"]),
            ("Chicken Rice Bowl", "https://example.com/chicken-rice", ["chicken", "rice", "onion", "olive oil", "salt"]),
            ("Tomato Omelette", "https://example.com/omelette", ["egg", "tomato", "onion", "salt", "olive oil"]),
        ]

        # ensure 'bread' exists if used
        if not Ingredient.objects.filter(name="bread").exists():
            name_to_obj["bread"], _ = Ingredient.objects.get_or_create(name="bread", defaults={"category": "bakery"})

        for title, url, ing_list in recipes:
            r, _ = Recipe.objects.get_or_create(title=title, defaults={"url": url})
            RecipeIngredient.objects.filter(recipe=r).delete()
            for ing in ing_list:
                i = name_to_obj.get(ing) or Ingredient.objects.get_or_create(name=ing)[0]
                RecipeIngredient.objects.get_or_create(recipe=r, ingredient=i)

        self.stdout.write(self.style.SUCCESS("Seed data loaded."))

