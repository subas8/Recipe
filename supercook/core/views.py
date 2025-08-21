from typing import List, Set, Dict
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import JsonResponse, HttpRequest
from django.shortcuts import render
from .models import Ingredient, Recipe, RecipeIngredient, Favorite


def home(request: HttpRequest):
    return render(request, 'home.html', {})


def _parse_ingredients_list(value: str) -> Set[str]:
    if not value:
        return set()
    names = [v.strip().lower() for v in value.split(',') if v.strip()]
    return set(names)


def search_recipes(request: HttpRequest):
    have = _parse_ingredients_list(request.GET.get('have', ''))
    one_away = request.GET.get('one_away', 'false').lower() in {'1', 'true', 'yes'}

    if not have:
        return JsonResponse({'recipes': [], 'one_away': []})

    ingredient_qs = Ingredient.objects.filter(name__in=list(have))
    ingredient_ids = list(ingredient_qs.values_list('id', flat=True))

    # Exact match: recipes where all required ingredients are a subset of have
    ri = RecipeIngredient.objects.values('recipe').annotate(total=Count('id'))
    ri_have = RecipeIngredient.objects.filter(ingredient_id__in=ingredient_ids).values('recipe').annotate(match=Count('id'))

    total_by_recipe: Dict[int, int] = {row['recipe']: row['total'] for row in ri}
    match_by_recipe: Dict[int, int] = {row['recipe']: row['match'] for row in ri_have}

    exact_recipe_ids: List[int] = [rid for rid, total in total_by_recipe.items() if match_by_recipe.get(rid, 0) == total and total > 0]

    recipes = list(Recipe.objects.filter(id__in=exact_recipe_ids).values('id', 'title', 'url'))

    result = {'recipes': recipes}

    if one_away:
        one_away_ids: List[int] = [rid for rid, total in total_by_recipe.items() if match_by_recipe.get(rid, 0) == total - 1 and total > 0]
        one_away_recipes = list(Recipe.objects.filter(id__in=one_away_ids).values('id', 'title', 'url'))
        result['one_away'] = one_away_recipes

    return JsonResponse(result)


def suggest_ingredients(request: HttpRequest):
    have = _parse_ingredients_list(request.GET.get('have', ''))
    if not have:
        return JsonResponse({'suggestions': []})

    have_ids = set(Ingredient.objects.filter(name__in=list(have)).values_list('id', flat=True))

    # For each missing ingredient, count how many additional recipes would become makeable
    suggestions: Dict[int, int] = {}
    recipe_requirements: Dict[int, Set[int]] = {}
    for req in RecipeIngredient.objects.values('recipe_id', 'ingredient_id'):
        rid = req['recipe_id']
        recipe_requirements.setdefault(rid, set()).add(req['ingredient_id'])

    for rid, reqs in recipe_requirements.items():
        matched_count = len(reqs & have_ids)
        missing = reqs - have_ids
        if missing and matched_count == len(reqs) - 1:
            # each missing ingredient here would unlock this recipe
            for mid in missing:
                suggestions[mid] = suggestions.get(mid, 0) + 1

    # Sort suggestions by unlock count desc
    sorted_pairs = sorted(suggestions.items(), key=lambda kv: kv[1], reverse=True)[:20]
    ingredients = Ingredient.objects.in_bulk([mid for mid, _ in sorted_pairs])
    payload = [
        {'id': mid, 'name': ingredients[mid].name, 'category': ingredients[mid].category, 'unlocks': cnt}
        for mid, cnt in sorted_pairs if mid in ingredients
    ]
    return JsonResponse({'suggestions': payload})


@login_required
def favorites(request: HttpRequest):
    if request.method == 'GET':
        favs = Favorite.objects.filter(user=request.user).select_related('recipe')
        data = [{'id': f.recipe.id, 'title': f.recipe.title, 'url': f.recipe.url} for f in favs]
        return JsonResponse({'favorites': data})
    if request.method == 'POST':
        recipe_id = request.POST.get('recipe_id')
        if not recipe_id:
            return JsonResponse({'error': 'recipe_id required'}, status=400)
        Favorite.objects.get_or_create(user=request.user, recipe_id=recipe_id)
        return JsonResponse({'ok': True})
    if request.method == 'DELETE':
        recipe_id = request.GET.get('recipe_id')
        Favorite.objects.filter(user=request.user, recipe_id=recipe_id).delete()
        return JsonResponse({'ok': True})
    return JsonResponse({'error': 'method not allowed'}, status=405)

# Create your views here.
