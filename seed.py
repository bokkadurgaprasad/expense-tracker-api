"""
Seed script to populate database with sample data
"""
from datetime import datetime, timedelta, UTC
from pymongo import MongoClient
from passlib.context import CryptContext
from bson import ObjectId
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash password with bcrypt 72 byte limit handling"""
    if len(password.encode('utf-8')) > 72:
        password = password[:72]
    return pwd_context.hash(password)

# MongoDB connection
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "personal_finance_tracker")

client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]

def clear_database():
    """Clear all collections"""
    print("Clearing database...")
    db.users.delete_many({})
    db.bank_accounts.delete_many({})
    db.credit_cards.delete_many({})
    db.emis.delete_many({})
    db.borrow_records.delete_many({})
    db.expected_cashflows.delete_many({})
    db.monthly_snapshots.delete_many({})
    print("✓ Database cleared")

def create_users():
    """Create sample users"""
    print("Creating users...")
    users = [
        {
            "_id": ObjectId(),
            "username": "dp_user",
            "password_hash": hash_password("Password123"),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "username": "test_user",
            "password_hash": hash_password("Test@123"),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    db.users.insert_many(users)
    print(f"✓ Created {len(users)} users")
    return users

def create_bank_accounts(users):
    """Create sample bank accounts"""
    print("Creating bank accounts...")
    accounts = []
    
    for user in users:
        user_accounts = [
            {
                "_id": ObjectId(),
                "user_id": user["_id"],
                "bank_name": "Chase Bank",
                "liquid_balance": 15000.00,
                "reserve_amount": 2000.00,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "_id": ObjectId(),
                "user_id": user["_id"],
                "bank_name": "Wells Fargo",
                "liquid_balance": 8000.00,
                "reserve_amount": 1000.00,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        accounts.extend(user_accounts)
    
    db.bank_accounts.insert_many(accounts)
    print(f"✓ Created {len(accounts)} bank accounts")
    return accounts

def create_credit_cards(users, accounts):
    """Create sample credit cards"""
    print("Creating credit cards...")
    cards = []
    
    # Group accounts by user
    user_accounts = {}
    for account in accounts:
        user_id = account["user_id"]
        if user_id not in user_accounts:
            user_accounts[user_id] = []
        user_accounts[user_id].append(account)
    
    for user in users:
        user_accs = user_accounts.get(user["_id"], [])
        if len(user_accs) >= 2:
            user_cards = [
                {
                    "_id": ObjectId(),
                    "user_id": user["_id"],
                    "card_name": "Chase Sapphire",
                    "bank_account_id": user_accs[0]["_id"],
                    "current_spend": 1200.00,
                    "billed_amount": 2500.00,
                    "emi_due": 500.00,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                },
                {
                    "_id": ObjectId(),
                    "user_id": user["_id"],
                    "card_name": "Amex Gold",
                    "bank_account_id": user_accs[1]["_id"],
                    "current_spend": 800.00,
                    "billed_amount": 1500.00,
                    "emi_due": 0.00,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcow()
                }
            ]
            cards.extend(user_cards)
    
    db.credit_cards.insert_many(cards)
    print(f"✓ Created {len(cards)} credit cards")
    return cards

def create_emis(users):
    """Create sample EMI records"""
    print("Creating EMI records...")
    emis = []
    
    for user in users:
        user_emis = [
            {
                "_id": ObjectId(),
                "user_id": user["_id"],
                "name": "Home Loan",
                "principal_amount": 500000.00,
                "interest_rate": 8.5,
                "monthly_emi_amount": 5000.00,
                "remaining_months": 120,
                "is_completed": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "_id": ObjectId(),
                "user_id": user["_id"],
                "name": "Car Loan",
                "principal_amount": 50000.00,
                "interest_rate": 7.0,
                "monthly_emi_amount": 1500.00,
                "remaining_months": 24,
                "is_completed": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        emis.extend(user_emis)
    
    db.emis.insert_many(emis)
    print(f"✓ Created {len(emis)} EMI records")
    return emis

def create_borrow_records(users):
    """Create sample borrow records"""
    print("Creating borrow records...")
    borrows = []
    
    for user in users:
        user_borrows = [
            {
                "_id": ObjectId(),
                "user_id": user["_id"],
                "party_name": "John Smith",
                "transaction_type": "borrowed_from",
                "remaining_amount": 5000.00,
                "due_date": datetime.utcnow() + timedelta(days=30),
                "status": "active",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "_id": ObjectId(),
                "user_id": user["_id"],
                "party_name": "Sarah Johnson",
                "transaction_type": "lent_to",
                "remaining_amount": 3000.00,
                "due_date": datetime.utcnow() + timedelta(days=45),
                "status": "active",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        borrows.extend(user_borrows)
    
    db.borrow_records.insert_many(borrows)
    print(f"✓ Created {len(borrows)} borrow records")
    return borrows

def create_expected_cashflows(users):
    """Create sample expected cashflows"""
    print("Creating expected cashflows...")
    cashflows = []
    
    for user in users:
        user_cashflows = [
            {
                "_id": ObjectId(),
                "user_id": user["_id"],
                "transaction_type": "income",
                "amount": 8000.00,
                "expected_date": datetime.utcnow() + timedelta(days=5),
                "status": "pending",
                "description": "Monthly Salary",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "_id": ObjectId(),
                "user_id": user["_id"],
                "transaction_type": "income",
                "amount": 2000.00,
                "expected_date": datetime.utcnow() + timedelta(days=15),
                "status": "pending",
                "description": "Freelance Project Payment",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "_id": ObjectId(),
                "user_id": user["_id"],
                "transaction_type": "expense",
                "amount": 1500.00,
                "expected_date": datetime.utcnow() + timedelta(days=10),
                "status": "pending",
                "description": "Rent Payment",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "_id": ObjectId(),
                "user_id": user["_id"],
                "transaction_type": "expense",
                "amount": 500.00,
                "expected_date": datetime.utcnow() + timedelta(days=20),
                "status": "pending",
                "description": "Utility Bills",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "_id": ObjectId(),
                "user_id": user["_id"],
                "transaction_type": "income",
                "amount": 1000.00,
                "expected_date": datetime.utcnow() - timedelta(days=5),
                "status": "missed",
                "description": "Bonus Payment (Missed)",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        cashflows.extend(user_cashflows)
    
    db.expected_cashflows.insert_many(cashflows)
    print(f"✓ Created {len(cashflows)} expected cashflows")
    return cashflows

def main():
    """Main seed function"""
    print("\n=== Personal Finance Tracker - Seed Script ===\n")
    
    try:
        # Clear existing data
        clear_database()
        
        # Create sample data
        users = create_users()
        accounts = create_bank_accounts(users)
        cards = create_credit_cards(users, accounts)
        emis = create_emis(users)
        borrows = create_borrow_records(users)
        cashflows = create_expected_cashflows(users)
        
        print("\n=== Seed Complete ===")
        print(f"Created:")
        print(f"  - {len(users)} users")
        print(f"  - {len(accounts)} bank accounts")
        print(f"  - {len(cards)} credit cards")
        print(f"  - {len(emis)} EMI records")
        print(f"  - {len(borrows)} borrow records")
        print(f"  - {len(cashflows)} expected cashflows")
        print("\nTest credentials:")
        print("  Username: dp_user / Password: Password123")
        print("  Username: test_user / Password: Test@123")
        
    except Exception as e:
        print(f"\n✗ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    main()
