from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from .meta import Base
import enum

class TransactionType(enum.Enum):
    income = "income"
    expense = "expense"

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Budget(Base):
    __tablename__ = 'budgets'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    amount = Column(Integer, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __acl__(self):
        """Return ACL for this budget."""
        return [
            (Allow, Authenticated, 'view'),
            (Allow, Authenticated, 'create'),
            (Allow, Authenticated, 'edit'),
            (Allow, Authenticated, 'delete'),
            (Allow, Authenticated, 'manage_budgets'),
            (Deny, Everyone, 'ALL_PERMISSIONS')
        ]

class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(100), nullable=False)
    type = Column(Enum(TransactionType))
    created_at = Column(DateTime, default=datetime.utcnow)

class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    budget_id = Column(Integer, ForeignKey('budgets.id'), nullable=False)
    type = Column(Enum(TransactionType))
    amount = Column(Integer, nullable=False)
    description = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

class Notification(Base):
    __tablename__ = 'notifications'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    message = Column(String(255), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)

# Define relationships after all models are defined
User.budgets = relationship("Budget", back_populates="user", lazy="dynamic")
User.transactions = relationship("Transaction", back_populates="user", lazy="dynamic")
User.categories = relationship("Category", back_populates="user", lazy="dynamic")
User.notifications = relationship("Notification", back_populates="user", lazy="dynamic")

Budget.user = relationship("User", back_populates="budgets")
Budget.category = relationship("Category", back_populates="budgets")
Budget.transactions = relationship("Transaction", back_populates="budget")

Category.user = relationship("User", back_populates="categories")
Category.transactions = relationship("Transaction", back_populates="category")
Category.budgets = relationship("Budget", back_populates="category")

Category.user = relationship("User", back_populates="categories")
Category.transactions = relationship("Transaction", back_populates="category")

Transaction.user = relationship("User", back_populates="transactions")
Transaction.category = relationship("Category", back_populates="transactions")
Transaction.budget = relationship("Budget", back_populates="transactions")

Notification.user = relationship("User", back_populates="notifications")
