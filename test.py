import requests
import json

API_KEY = "mgl2rUjURL5V53XjcuWbKjMhVpdqbplfD5oCGP23"
BASE_URL = "https://api.nal.usda.gov/fdc/v1"

with open("config.json", "r") as f:
    config = json.load(f)

CONVERSIONS = config["conversions"]
UNIT_ALIASES = config["unit_aliases"]
NUTRIENT_OPTIONS = config["nutrients"]


def parse_input(user_input):
    """Extract quantity, unit, food name, and state from user input."""
    tokens = user_input.lower().split()
    quantity = 100.0
    unit = "g"
    state = "raw"
    food_name_parts = []

    for i, t in enumerate(tokens):
        if t.replace('.', '', 1).isdigit():
            quantity = float(t)
            if i + 1 < len(tokens):
                unit = tokens[i + 1].lower()
            food_name_parts = tokens[i + 2:]
            break
    else:
        food_name_parts = tokens

    if food_name_parts and food_name_parts[-1] in ("raw", "cooked", "boiled", "fried", "canned"):
        state = food_name_parts[-1]
        food_name_parts = food_name_parts[:-1]

    food_name = " ".join(food_name_parts).strip()
    return quantity, unit, food_name, state



def search_food(food_name, state="raw"):
    """Поиск продуктов по названию"""
    query = f"{food_name} {state}"
    url = f"{BASE_URL}/foods/search"

    params = {
        "api_key": API_KEY,
        "query": query,
        "dataType": ["Foundation", "SR Legacy","Survey (FNDDS)"],
        "pageSize": 5
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print("❌ Error:", response.status_code)
        return []

    data = response.json()
    foods = data.get("foods", [])
    if not foods:
        print("⚠️ No results found.")
        return []

    print("\n🔍 Top results:")
    for i, food in enumerate(foods[:5], 1):
        print(f"{i}. {food['description']} (fdcId: {food['fdcId']})")

    return foods[0]


def get_food_details(fdc_id):
    """Получение деталей о продукте по FDC ID"""
    url = f"{BASE_URL}/food/{fdc_id}?api_key={API_KEY}"
    response = requests.get(url)

    if response.status_code != 200:
        print("❌ Error:", response.status_code)
        return

    data = response.json()
    
    return data


def convert_to_base_unit(quantity, unit):
    
    """Convert given quantity and unit to grams or milliliters."""
    unit = unit.lower()
    unit = unit = UNIT_ALIASES.get(unit, unit)  # map plural to singular

    if unit == "ml":
        return quantity, "ml"

    if unit == 'g':
        return quantity, 'g'

    if unit in CONVERSIONS["weightGrams"]:
        grams = quantity * CONVERSIONS["weightGrams"][unit]
        return grams, "g"
    elif unit in CONVERSIONS["volumeML"]:
        ml = quantity * CONVERSIONS["volumeML"][unit]
        return ml, "ml"
    else:
        print(f"⚠️ Unknown unit '{unit}', assuming grams.")
        return quantity, "g"


def calculate_nutrients(details, quantity, unit):
    """Scale nutrients per user quantity based on 100 g or 100 ml base."""
    nutrients = details.get("foodNutrients", [])
    scaled = {}
    base = 100.0

    converted_value, base_unit = convert_to_base_unit(quantity, unit)

    for nutrient in nutrients:
        name = nutrient.get("nutrient", {}).get("name", "")
        amount = nutrient.get("amount", 0)
        if name:
            scaled[name] = round((amount / base) * converted_value, 2)

    return scaled, base_unit, converted_value


def main():
    print("=== 🥦 USDA Food Nutrition Finder ===")
    user_input = input("Enter food (e.g., '2 cups rice cooked'): ").strip()

    quantity, unit, food_name, state = parse_input(user_input)
    print(f"\nParsed input: {quantity} {unit} {food_name} ({state})")
    # Step 1: Поиск продуктов
    foods = search_food(food_name, state)
    if not foods:
        return

    fdc_id = foods["fdcId"]
    details = get_food_details(fdc_id)
    if not details:
        return

    scaled, base_unit, converted_value = calculate_nutrients(details, quantity, unit)

    print(f"\n📦 Product: {details.get('description')}")
    print(f"🧮 Amount: {quantity} {unit} ≈ {converted_value:.2f} {base_unit}")
    print("\n📊 Nutrients (scaled):")

    for key in NUTRIENT_OPTIONS:
        for name, val in scaled.items():
            if key.lower() in name.lower():
                print(f" - {name}: {val}")


if __name__ == "__main__":
    main()
