import requests

API_KEY = "mgl2rUjURL5V53XjcuWbKjMhVpdqbplfD5oCGP23"

def search_food(food_name):
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={food_name}&api_key={API_KEY}"
    response = requests.get(url)
    
    if response.status_code != 200:
        print("Error:", response.status_code)
        return
    
    data = response.json()
    
    # Show the top 3 matches
    for i, food in enumerate(data.get("foods", [])[:3]):
        print(f"{i+1}. {food['description']} (fdcId: {food['fdcId']})")

def get_food_details(fdc_id):
    url = f"https://api.nal.usda.gov/fdc/v1/food/{fdc_id}?api_key={API_KEY}"
    response = requests.get(url)
    
    if response.status_code != 200:
        print("Error:", response.status_code)
        return
    data = response.json()
    
    print("\nName:", data.get("description"))
    print("Nutrients:")
    for nutrient in data.get("foodNutrients", [])[:10]:
        nutrient_info = nutrient.get("nutrient", {})
        name = nutrient_info.get("name", "Unknown")
        value = nutrient.get("amount", "N/A")
        unit = nutrient_info.get("unitName", "")
        print(f" - {name}: {value} {unit}")


# Test
search_food("banana")  # Step 1: find product IDs
get_food_details(173944)  # Step 2: example FDC ID
