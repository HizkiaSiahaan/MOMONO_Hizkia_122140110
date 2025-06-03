import requests
import json
import os

# Base URL for the API
BASE_URL = "http://localhost:6543"

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_separator():
    """Print a separator line."""
    print("=" * 50)

def test_categories_endpoints():
    clear_screen()
    print_separator()
    print("TESTING CATEGORIES ENDPOINTS")
    print_separator()
    
    # Test getting all categories
    print("\n1. Getting all categories...")
    try:
        response = requests.get(f"{BASE_URL}/api/categories")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                resp_json = response.json()
                print(f"Total categories: {len(resp_json.get('categories', []))}")
                print(f"JSON Response: {json.dumps(resp_json, indent=2)}")
            except Exception as e:
                print(f"Error parsing JSON: {str(e)}")
        else:
            print(f"Failed to get categories: {response.text}")
    except Exception as e:
        print(f"Request error: {str(e)}")
    
    # Test creating a new category
    print("\n2. Creating a new category...")
    category_data = {
        "name": "Test Category",
        "type": "expense"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/categories", json=category_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                resp_json = response.json()
                print(f"JSON Response: {json.dumps(resp_json, indent=2)}")
                print(f"Created category with ID: {resp_json.get('category', {}).get('id')}")
            except Exception as e:
                print(f"Error parsing JSON: {str(e)}")
        else:
            print(f"Failed to create category: {response.text}")
    except Exception as e:
        print(f"Request error: {str(e)}")
    
    print_separator()
    print("CATEGORIES API TESTS COMPLETED")
    print_separator()

if __name__ == "__main__":
    test_categories_endpoints()
