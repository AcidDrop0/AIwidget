import os
import requests

API_KEY = os.environ.get("USDA_API_KEY", "mgl2rUjURL5V53XjcuWbKjMhVpdqbplfD5oCGP23")
BASE = "https://api.nal.usda.gov/fdc/v1"

# Какие нутриенты будем искать по имени
NUTRIENT_KEYWORDS = {
    "calories": ["energy", "energy (kcal)"],
    "protein": ["protein"],
    "fat": ["total lipid (fat)", "fat"],
    "carbs": ["carbohydrate", "carbohydrates"],
    "fiber": ["fiber", "total dietary fiber"],
    "sugar": ["sugars", "sugar"],
}

def search_food(food_name):
    url = f"{BASE}/foods/search"
    params = {"api_key": API_KEY, "query": food_name}
    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        return None
    return resp.json()

def get_food_details(fdc_id):
    url = f"{BASE}/food/{fdc_id}"
    params = {"api_key": API_KEY}
    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        return None
    return resp.json()

def run():
    # Входные данные от Abyss
    user_input = os.environ.get("ingredients", "")
    selected_nutrients = os.environ.get("nutrients", "calories,protein,fat,carbs").lower().split(",")

    os.makedirs("output", exist_ok=True)
    if not user_input.strip():
        with open("output/result.txt", "w") as f:
            f.write("No ingredients provided.")
        return

    ingredients = [ing.strip() for ing in user_input.split(",") if ing.strip()]
    total = {nut: 0.0 for nut in selected_nutrients}
    lines = []

    for ing in ingredients:
        resp = search_food(ing)
        if not resp or "foods" not in resp or not resp["foods"]:
            lines.append(f"{ing} — not found in USDA database.")
            continue

        first = resp["foods"][0]
        fdc_id = first.get("fdcId")
        details = get_food_details(fdc_id)
        if not details:
            lines.append(f"{ing} — could not fetch details.")
            continue

        nutrients = details.get("foodNutrients", [])
        nutrient_values = {}

        for nut in selected_nutrients:
            for n in nutrients:
                if n.get("name", "").lower() in NUTRIENT_KEYWORDS.get(nut, []):
                    nutrient_values[nut] = n.get("amount", 0.0)
                    total[nut] += n.get("amount", 0.0)
                    break

        # Форматируем строку с найденными нутриентами
        if nutrient_values:
            parts = [f"{k.capitalize()}: {v:.2f}" for k, v in nutrient_values.items()]
            lines.append(f"{ing}: " + ", ".join(parts))
        else:
            lines.append(f"{ing} — no matching nutrients found.")

    # Итог
    lines.append("\nTotal:")
    for k, v in total.items():
        lines.append(f"  {k.capitalize()}: {v:.2f}")

    with open("output/result.txt", "w") as f:
        f.write("\n".join(lines))

if __name__ == "__main__":
    run()
