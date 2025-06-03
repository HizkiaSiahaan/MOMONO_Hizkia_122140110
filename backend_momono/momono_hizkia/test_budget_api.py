import requests
import json
import time
import sys
import os

# Base URL for the API
BASE_URL = "http://localhost:6543"

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_separator():
    """Print a separator line."""
    print("=" * 50)

def test_budget_endpoints():
    clear_screen()
    print_separator()
    print("TESTING BUDGET ENDPOINTS")
    print_separator()
    
    # Test creating a budget
    print("\n1. Creating a new budget with category...")
    budget_data = {
        "name": "Test Budget",
        "description": "Budget for testing",
        "amount": 1000,
        "category": "Food"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/simple/budgets", json=budget_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                resp_json = response.json()
                print(f"JSON Response: {json.dumps(resp_json, indent=2)}")
                budget_id = resp_json.get("budget", {}).get("id")
                print(f"Created budget with ID: {budget_id}")
                print(f"Category: {resp_json.get('budget', {}).get('category')}")
            except Exception as e:
                print(f"Error parsing JSON: {str(e)}")
                return
        else:
            print(f"Failed to create budget: {response.text}")
            return
    except Exception as e:
        print(f"Request error: {str(e)}")
        return
    
    if budget_id:
        # Test getting all budgets
        print("\n2. Getting all budgets...")
        try:
            response = requests.get(f"{BASE_URL}/api/simple/budgets")
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    resp_json = response.json()
                    print(f"Total budgets: {len(resp_json.get('budgets', []))}")
                    print(f"JSON Response: {json.dumps(resp_json, indent=2)}")
                except Exception as e:
                    print(f"Error parsing JSON: {str(e)}")
        except Exception as e:
            print(f"Request error: {str(e)}")
        
        # Test getting a specific budget
        print(f"\n3. Getting budget with ID {budget_id}...")
        try:
            response = requests.get(f"{BASE_URL}/api/simple/budgets/{budget_id}")
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    resp_json = response.json()
                    print(f"JSON Response: {json.dumps(resp_json, indent=2)}")
                    print(f"Budget category: {resp_json.get('budget', {}).get('category')}")
                except Exception as e:
                    print(f"Error parsing JSON: {str(e)}")
        except Exception as e:
            print(f"Request error: {str(e)}")
        
        # Test updating a budget
        print(f"\n4. Updating budget with ID {budget_id}...")
        update_data = {
            "name": "Updated Test Budget",
            "description": "Updated description",
            "amount": 1500,
            "category": "Groceries"
        }
        
        try:
            response = requests.put(f"{BASE_URL}/api/simple/budgets/{budget_id}", json=update_data)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    resp_json = response.json()
                    print(f"JSON Response: {json.dumps(resp_json, indent=2)}")
                    print(f"Updated budget category: {resp_json.get('budget', {}).get('category')}")
                except Exception as e:
                    print(f"Error parsing JSON: {str(e)}")
        except Exception as e:
            print(f"Request error: {str(e)}")
        
        # Test deleting a budget
        print(f"\n5. Deleting budget with ID {budget_id}...")
        try:
            response = requests.delete(f"{BASE_URL}/api/simple/budgets/{budget_id}")
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    resp_json = response.json()
                    print(f"JSON Response: {json.dumps(resp_json, indent=2)}")
                except Exception as e:
                    print(f"Error parsing JSON: {str(e)}")
        except Exception as e:
            print(f"Request error: {str(e)}")
    
    print_separator()
    print("BUDGET API TESTS COMPLETED")
    print_separator()

if __name__ == "__main__":
    test_budget_endpoints()
