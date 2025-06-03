import requests
import json
import time
import sys
import os

# Base URL for the API
BASE_URL = "http://localhost:6543"

def test_budget_endpoints():
    print("\n=== Testing Budget Endpoints ===")
    
    # Test creating a budget
    print("\nCreating a new budget...")
    budget_data = {
        "name": "Test Budget",
        "description": "Budget for testing",
        "amount": 1000,
        "category": "Food"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/simple/budgets", json=budget_data)
        print(f"Status Code: {response.status_code}")
        print(f"Raw Response: {response.text}")
        
        if response.status_code == 200:
            try:
                resp_json = response.json()
                print(f"JSON Response: {resp_json}")
                budget_id = resp_json.get("budget", {}).get("id")
            except Exception as e:
                print(f"Error parsing JSON: {str(e)}")
                return
        else:
            print("Failed to create budget")
            return
    except Exception as e:
        print(f"Request error: {str(e)}")
        return
    
    if budget_id:
        
        # Test getting all budgets
        print("\nGetting all budgets...")
        try:
            response = requests.get(f"{BASE_URL}/api/simple/budgets")
            print(f"Status Code: {response.status_code}")
            print(f"Raw Response: {response.text}")
            if response.status_code == 200:
                try:
                    print(f"JSON Response: {response.json()}")
                except Exception as e:
                    print(f"Error parsing JSON: {str(e)}")
        except Exception as e:
            print(f"Request error: {str(e)}")
        
        # Test getting a specific budget
        print(f"\nGetting budget with ID {budget_id}...")
        try:
            response = requests.get(f"{BASE_URL}/api/simple/budgets/{budget_id}")
            print(f"Status Code: {response.status_code}")
            print(f"Raw Response: {response.text}")
            if response.status_code == 200:
                try:
                    print(f"JSON Response: {response.json()}")
                except Exception as e:
                    print(f"Error parsing JSON: {str(e)}")
        except Exception as e:
            print(f"Request error: {str(e)}")
        
        # Test updating a budget
        print(f"\nUpdating budget with ID {budget_id}...")
        update_data = {
            "name": "Updated Test Budget",
            "description": "Updated budget description",
            "amount": 1500
        }
        try:
            response = requests.put(f"{BASE_URL}/api/simple/budgets/{budget_id}", json=update_data)
            print(f"Status Code: {response.status_code}")
            print(f"Raw Response: {response.text}")
            if response.status_code == 200:
                try:
                    print(f"JSON Response: {response.json()}")
                except Exception as e:
                    print(f"Error parsing JSON: {str(e)}")
        except Exception as e:
            print(f"Request error: {str(e)}")
        
        # Test deleting a budget
        print(f"\nDeleting budget with ID {budget_id}...")
        try:
            response = requests.delete(f"{BASE_URL}/api/simple/budgets/{budget_id}")
            print(f"Status Code: {response.status_code}")
            print(f"Raw Response: {response.text}")
            if response.status_code == 200:
                try:
                    print(f"JSON Response: {response.json()}")
                except Exception as e:
                    print(f"Error parsing JSON: {str(e)}")
        except Exception as e:
            print(f"Request error: {str(e)}")
    
def test_transaction_endpoints():
    print("\n=== Testing Transaction Endpoints ===")
    
    # Test creating a transaction
    print("\nCreating a new transaction...")
    transaction_data = {
        "amount": 50.75,
        "description": "Test Transaction",
        "category": "Food",
        "type": "expense",
        "created_at": "2025-06-03"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/simple/transactions", json=transaction_data)
        print(f"Status Code: {response.status_code}")
        print(f"Raw Response: {response.text}")
        
        if response.status_code == 200:
            try:
                resp_json = response.json()
                print(f"JSON Response: {resp_json}")
                transaction_id = resp_json.get("transaction", {}).get("id")
            except Exception as e:
                print(f"Error parsing JSON: {str(e)}")
                return
        else:
            print("Failed to create transaction")
            return
    except Exception as e:
        print(f"Request error: {str(e)}")
        return
    
    if transaction_id:
        # Test getting all transactions
        print("\nGetting all transactions...")
        try:
            response = requests.get(f"{BASE_URL}/api/simple/transactions")
            print(f"Status Code: {response.status_code}")
            print(f"Raw Response: {response.text}")
            if response.status_code == 200:
                try:
                    print(f"JSON Response: {response.json()}")
                except Exception as e:
                    print(f"Error parsing JSON: {str(e)}")
        except Exception as e:
            print(f"Request error: {str(e)}")
        
        # Test getting a specific transaction
        print(f"\nGetting transaction with ID {transaction_id}...")
        try:
            response = requests.get(f"{BASE_URL}/api/simple/transactions/{transaction_id}")
            print(f"Status Code: {response.status_code}")
            print(f"Raw Response: {response.text}")
            if response.status_code == 200:
                try:
                    print(f"JSON Response: {response.json()}")
                except Exception as e:
                    print(f"Error parsing JSON: {str(e)}")
        except Exception as e:
            print(f"Request error: {str(e)}")
        
        # Test updating a transaction
        print(f"\nUpdating transaction with ID {transaction_id}...")
        update_data = {
            "amount": 75.50,
            "description": "Updated Test Transaction",
            "category": "Groceries",
            "type": "expense",
            "created_at": "2025-06-03"
        }
        try:
            response = requests.put(f"{BASE_URL}/api/simple/transactions/{transaction_id}", json=update_data)
            print(f"Status Code: {response.status_code}")
            print(f"Raw Response: {response.text}")
            if response.status_code == 200:
                try:
                    print(f"JSON Response: {response.json()}")
                except Exception as e:
                    print(f"Error parsing JSON: {str(e)}")
        except Exception as e:
            print(f"Request error: {str(e)}")
        
        # Test deleting a transaction
        print(f"\nDeleting transaction with ID {transaction_id}...")
        try:
            response = requests.delete(f"{BASE_URL}/api/simple/transactions/{transaction_id}")
            print(f"Status Code: {response.status_code}")
            print(f"Raw Response: {response.text}")
            if response.status_code == 200:
                try:
                    print(f"JSON Response: {response.json()}")
                except Exception as e:
                    print(f"Error parsing JSON: {str(e)}")
        except Exception as e:
            print(f"Request error: {str(e)}")

if __name__ == "__main__":
    print("\n" + "="*50)
    print("STARTING API TESTS")
    print("="*50)
    
    print("\n" + "="*50)
    print("TESTING BUDGET ENDPOINTS")
    print("="*50)
    test_budget_endpoints()
    
    print("\n" + "="*50)
    print("TESTING TRANSACTION ENDPOINTS")
    print("="*50)
    test_transaction_endpoints()
    
    print("\n" + "="*50)
    print("API TESTS COMPLETED")
    print("="*50)
