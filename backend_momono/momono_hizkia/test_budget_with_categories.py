import requests
import json
import os
import time

# Base URL for the API
BASE_URL = "http://localhost:6543"

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_separator():
    """Print a separator line."""
    print("=" * 50)

def test_budget_with_categories():
    clear_screen()
    print_separator()
    print("TESTING BUDGET WITH CATEGORIES")
    print_separator()
    
    # Step 1: Get all categories
    print("\n1. Getting all categories...")
    categories = []
    try:
        response = requests.get(f"{BASE_URL}/api/categories")
        if response.status_code == 200:
            resp_json = response.json()
            categories = resp_json.get('categories', [])
            print(f"Found {len(categories)} categories")
            if categories:
                print(f"First few categories: {categories[:3]}")
        else:
            print(f"Failed to get categories: {response.text}")
            return
    except Exception as e:
        print(f"Request error: {str(e)}")
        return
    
    if not categories:
        print("No categories found. Creating a test category...")
        category_data = {
            "name": "Test Category",
            "type": "expense"
        }
        try:
            response = requests.post(f"{BASE_URL}/api/categories", json=category_data)
            if response.status_code == 200:
                resp_json = response.json()
                categories = [resp_json.get('category')]
                print(f"Created category: {categories[0]}")
            else:
                print(f"Failed to create category: {response.text}")
                return
        except Exception as e:
            print(f"Request error: {str(e)}")
            return
    
    # Step 2: Create a budget with a category
    print("\n2. Creating a budget with a category...")
    selected_category = categories[0]['name']
    budget_data = {
        "name": "Test Budget with Category",
        "description": "Budget for testing with category",
        "amount": 1500,
        "category": selected_category
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/simple/budgets", json=budget_data)
        if response.status_code == 200:
            resp_json = response.json()
            budget = resp_json.get('budget')
            budget_id = budget.get('id')
            print(f"Created budget with ID: {budget_id}")
            print(f"Budget category: {budget.get('category')}")
            print(f"Full budget: {json.dumps(budget, indent=2)}")
        else:
            print(f"Failed to create budget: {response.text}")
            return
    except Exception as e:
        print(f"Request error: {str(e)}")
        return
    
    # Step 3: Get the budget to verify category is saved
    print(f"\n3. Getting budget with ID {budget_id} to verify category...")
    try:
        response = requests.get(f"{BASE_URL}/api/simple/budgets/{budget_id}")
        if response.status_code == 200:
            resp_json = response.json()
            budget = resp_json.get('budget')
            print(f"Retrieved budget category: {budget.get('category')}")
            if budget.get('category') == selected_category:
                print("✅ Category saved and retrieved successfully!")
            else:
                print("❌ Category mismatch!")
        else:
            print(f"Failed to get budget: {response.text}")
    except Exception as e:
        print(f"Request error: {str(e)}")
    
    # Step 4: Clean up - delete the test budget
    print(f"\n4. Cleaning up - deleting test budget...")
    try:
        response = requests.delete(f"{BASE_URL}/api/simple/budgets/{budget_id}")
        if response.status_code == 200:
            print("Test budget deleted successfully")
        else:
            print(f"Failed to delete budget: {response.text}")
    except Exception as e:
        print(f"Request error: {str(e)}")
    
    print_separator()
    print("TEST COMPLETED")
    print_separator()

if __name__ == "__main__":
    test_budget_with_categories()
