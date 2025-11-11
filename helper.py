import requests

API_KEY = "mgl2rUjURL5V53XjcuWbKjMhVpdqbplfD5oCGP23"
BASE_URL = "https://api.nal.usda.gov/fdc/v1"

def search_food(food_name):
    """Поиск продуктов по названию"""
    url = f"{BASE_URL}/foods/search?query={food_name}&api_key={API_KEY}"
    response = requests.get(url)

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

    return foods[:5]


def get_food_details(fdc_id, selected_nutrients):
    """Получение деталей о продукте по FDC ID"""
    url = f"{BASE_URL}/food/{fdc_id}?api_key={API_KEY}"
    response = requests.get(url)

    if response.status_code != 200:
        print("❌ Error:", response.status_code)
        return

    data = response.json()
    print(f"\n📦 Product: {data.get('description', 'Unknown')}")
    print("📊 Selected Nutrients:")

    for nutrient in data.get("foodNutrients", []):
        name = nutrient.get("nutrient", {}).get("name", "").lower()
        value = nutrient.get("amount", "N/A")
        unit = nutrient.get("nutrient", {}).get("unitName", "")

        for key in selected_nutrients:
            if key.lower() in name:
                print(f" - {name.title()}: {value} {unit}")


def main():
    print("=== 🥦 USDA Food Nutrition Finder ===")
    food_name = input("Enter food name: ").strip()

    # Step 1: Поиск продуктов
    foods = search_food(food_name)
    if not foods:
        return

    choice = input("\nEnter number of the food to view details: ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(foods)):
        print("❌ Invalid choice.")
        return

    fdc_id = foods[int(choice) - 1]["fdcId"]

    # Step 2: Выбор нутриентов
    nutrient_options = [
        "Calories",
        "Protein",
        "Fat",
        "Carbohydrate",
        "Sugar",
        "Fiber",
        "Cholesterol",
        "Sodium",
        "Calcium",
        "Iron",
    ]

    print("\nSelect nutrients to show (e.g. 1,3,5):")
    for i, n in enumerate(nutrient_options, 1):
        print(f"{i}. {n}")

    selected = input("\nYour selection: ").strip()
    if not selected:
        print("⚠️ No nutrients selected, showing all.")
        selected_nutrients = nutrient_options
    else:
        indices = [int(i) for i in selected.split(",") if i.strip().isdigit()]
        selected_nutrients = [
            nutrient_options[i - 1] for i in indices if 1 <= i <= len(nutrient_options)
        ]

    # Step 3: Получаем информацию
    get_food_details(fdc_id, selected_nutrients)


if __name__ == "__main__":
    main()
