"""
ingredient_tags.py
-------------------
Replaces the hardcoded flag assignment in build_dataset.py.

Every dish's is_vegetarian / is_vegan / contains_dairy / contains_gluten /
contains_egg / contains_nuts is DERIVED from what's actually in the recipe's
ingredient list, instead of being hardcoded to a default.

This is a rule-based classifier, not a magic fix for missing nutrition data.
It will not invent calories/fiber/sugar/sodium. It only fixes the flags,
which were previously just wrong defaults regardless of ingredients.

Extend these keyword sets as you find gaps -- they're intentionally simple
substring checks on the ingredient key (e.g. "raw_chicken", "mozzarella_cheese").
"""

MEAT_POULTRY = {
    "chicken", "pork", "beef", "mutton", "lamb", "goat", "buff", "duck",
    "turkey", "bacon", "ham", "sausage", "meat", "sekuwa", "sukuti",
}

SEAFOOD = {
    "fish", "shrimp", "prawn", "crab", "lobster", "salmon", "tuna",
    "anchov", "squid", "octopus", "clam", "oyster", "mussel",
}

DAIRY = {
    "milk", "butter", "cheese", "cream", "ghee", "paneer", "yogurt",
    "yoghurt", "curd", "dahi", "whey", "casein", "khoa", "mawa",
}

GLUTEN = {
    "flour", "wheat", "bread", "pasta", "noodle", "barley", "rye",
    "semolina", "dumpling_wrapper", "crust", "biscuit", "cracker",
    "pretzel", "soy_sauce",  # most commercial soy sauce contains wheat
}

EGG = {"egg", "eggs", "mayonnaise", "meringue"}

NUTS = {
    "almond", "walnut", "cashew", "peanut", "pecan", "pistachio",
    "hazelnut", "macadamia", "brazil_nut", "pine_nut",
}

VEGAN_EXCLUDING = MEAT_POULTRY | SEAFOOD | DAIRY | EGG | {"honey", "gelatin"}


def _any_keyword_match(ingredient_key: str, keyword_set: set) -> bool:
    key = ingredient_key.lower()
    return any(kw in key for kw in keyword_set)


def classify_recipe(ingredient_keys):
    """
    ingredient_keys: iterable of ingredient dict keys used in a recipe,
    e.g. ["raw_chicken", "flour", "mustard_oil"]

    Returns a dict of flags derived from actual composition.
    NOTE: contains_nuts / contains_gluten / contains_dairy / contains_egg
    are about ALLERGEN PRESENCE (True if any trace ingredient matches),
    which is the conservative/safe direction for an allergen flag.
    """
    has_meat = any(_any_keyword_match(k, MEAT_POULTRY) for k in ingredient_keys)
    has_seafood = any(_any_keyword_match(k, SEAFOOD) for k in ingredient_keys)
    has_dairy = any(_any_keyword_match(k, DAIRY) for k in ingredient_keys)
    has_gluten = any(_any_keyword_match(k, GLUTEN) for k in ingredient_keys)
    has_egg = any(_any_keyword_match(k, EGG) for k in ingredient_keys)
    has_nuts = any(_any_keyword_match(k, NUTS) for k in ingredient_keys)
    has_vegan_excluded = any(
        _any_keyword_match(k, VEGAN_EXCLUDING) for k in ingredient_keys
    )

    is_vegetarian = not (has_meat or has_seafood)
    is_vegan = is_vegetarian and not has_vegan_excluded

    return {
        "is_vegetarian": is_vegetarian,
        "is_vegan": is_vegan,
        "is_gluten_free": not has_gluten,
        "contains_dairy": has_dairy,
        "contains_gluten": has_gluten,
        "contains_egg": has_egg,
        "contains_nuts": has_nuts,
        # exposed for auditing / manual review, not written to the final CSV directly
        "_has_meat": has_meat,
        "_has_seafood": has_seafood,
    }


NEPALI_CATEGORY_PREFIXES = ("nepali_",)


def is_nepali_from_category(category: str) -> bool:
    """
    Replaces the hardcoded `is_nepali: True` in build_dataset.py.
    Only categories explicitly tagged nepali_* count as Nepali.
    A dish imported from a generic recipe source (American, Italian,
    Korean, etc.) should never default to True.
    """
    if not category:
        return False
    return category.lower().startswith(NEPALI_CATEGORY_PREFIXES)
