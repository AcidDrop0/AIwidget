import os
import requests

API_KEY = os.environ.get("mgl2rUjURL5V53XjcuWbKjMhVpdqbplfD5oCGP23")  # Put your key in env var

BASE = "https://api.nal.usda.gov/fdc/v1"

def search_food(food_name):
    """Return a list of possible matches (with fdcId etc.)."""
    url = f"{BASE}/foods/search"
    params = {
        "api_key": API_KEY,
        "query": food_name,
        # optionally: "pageSize": 2, "dataType": ["Foundation","SR Legacy", ...]
    }
    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        return None
    return resp.json()

def get_food_details(fdc_id):
    """Get full nutrient details for a specific fdcId."""
    url = f"{BASE}/food/{fdc_id}"
    params = {
        "api_key": API_KEY
    }
    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        return None
    return resp.json()

def run():
    user_input = os.environ.get("ingredients", "")
    os.makedirs("output", exist_ok=True)

    if not user_input.strip():
        with open("output/result.txt", "w") as f:
            f.write("No ingredients provided.")
        return

    ingredients = [ing.strip() for ing in user_input.split(",") if ing.strip()]
    total = {
        "calories": 0.0,
        # you can track protein, carbs, fat etc
    }
    lines = []

    for ing in ingredients:
        # For simplicity, ignore quantity parsing first — just search by name
        resp = search_food(ing)
        if not resp or "foods" not in resp or len(resp["foods"]) == 0:
            lines.append(f"{ing} — not found in USDA database.")
            continue

        # pick the first result
        first = resp["foods"][0]
        fdcId = first.get("fdcId")

        details = get_food_details(fdcId)
        if not details:
            lines.append(f"{ing} — could not fetch details.")
            continue

        # Now extract nutrients. USDA returns a list "foodNutrients"
        nutrients = details.get("foodNutrients", [])
        # Example: find calories (nutrient number 208 is typically energy in kcal)
        cal = None
        for nut in nutrients:
            if nut.get("name", "").lower() in ("energy", "energy (kcal)"):
                cal = nut.get("amount")
        if cal is None:
            lines.append(f"{ing} — no calorie data.")
        else:
            total["calories"] += cal
            lines.append(f"{ing}: {cal} kcal")

    lines.append("\nTotal calories: {:.2f} kcal".format(total["calories"]))
    with open("output/result.txt", "w") as f:
        f.write("\n".join(lines))

if __name__ == "__main__":
    run()
