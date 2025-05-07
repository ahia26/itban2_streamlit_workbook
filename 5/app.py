import streamlit as st
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, text
import hashlib
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_USER = os.getenv("DB_USER", "root1")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "streamlit_demo")

# Create database connection
@st.cache_resource
def init_connection():
    try:
        connection_string = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        engine = create_engine(connection_string)
        return engine
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None

# Initialize database schema if needed
def initialize_database():
    engine = init_connection()
    if engine is None:
        return False
    
    # Create users table if it doesn't exist
    create_users_table = """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password_hash VARCHAR(64) NOT NULL,
        is_admin BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # Create products table if it doesn't exist
    create_products_table = """
    CREATE TABLE IF NOT EXISTS products (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        category VARCHAR(50),
        price DECIMAL(10, 2) NOT NULL,
        inventory INT DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    );
    """
    
    try:
        with engine.begin() as conn:
            # Create tables
            conn.execute(text(create_users_table))
            conn.execute(text(create_products_table))
            
            # Check if admin user exists
            result = conn.execute(text("SELECT COUNT(*) FROM users WHERE is_admin = TRUE"))
            admin_exists = result.scalar()
            
            # Add admin user if none exists
            if not admin_exists:
                admin_password_hash = hash_password("admin123")
                conn.execute(text(
                    "INSERT INTO users (username, password_hash, is_admin) VALUES ('admin', :password_hash, TRUE)"
                ), {"password_hash": admin_password_hash})
                
                # Add sample products
                sample_products = [
                    ("Laptop", "Electronics", 1299.99, 10),
                    ("Coffee Maker", "Appliances", 89.99, 15),
                    ("Desk Chair", "Furniture", 199.99, 5),
                    ("Smartphone", "Electronics", 899.99, 20),
                    ("Wireless Headphones", "Electronics", 149.99, 30)
                ]
                
                for product in sample_products:
                    conn.execute(text(
                        "INSERT INTO products (name, category, price, inventory) VALUES (:name, :category, :price, :inventory)"
                    ), {"name": product[0], "category": product[1], "price": product[2], "inventory": product[3]})
        
        return True
    except Exception as e:
        st.error(f"Database initialization error: {e}")
        return False

# Execute query with caching for read-only queries
@st.cache_data(ttl=60)
def run_query(query, params=None):
    engine = init_connection()
    if engine is None:
        return None
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query), params or {})
            return pd.DataFrame(result.fetchall(), columns=result.keys())
    except Exception as e:
        # If table doesn't exist, try to initialize database
        if "doesn't exist" in str(e):
            if initialize_database():
                # Try the query again after initialization
                with engine.connect() as conn:
                    result = conn.execute(text(query), params or {})
                    return pd.DataFrame(result.fetchall(), columns=result.keys())
            else:
                st.error(f"Query execution error: {e}")
                return None
        else:
            st.error(f"Query execution error: {e}")
            return None

# Execute query without caching for write operations
def execute_query(query, params=None):
    engine = init_connection()
    if engine is None:
        return False
    
    try:
        with engine.begin() as conn:
            conn.execute(text(query), params or {})
            return True
    except Exception as e:
        # If table doesn't exist, try to initialize database
        if "doesn't exist" in str(e):
            if initialize_database():
                # Try the query again after initialization
                with engine.begin() as conn:
                    conn.execute(text(query), params or {})
                    return True
            else:
                st.error(f"Query execution error: {e}")
                return False
        else:
            st.error(f"Query execution error: {e}")
            return False

# Hash password for secure storage
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Verify password
def verify_password(username, password):
    hashed_password = hash_password(password)
    query = "SELECT * FROM users WHERE username = :username AND password_hash = :password_hash"
    result = run_query(query, {"username": username, "password_hash": hashed_password})
    return not result.empty if result is not None else False

# User authentication system
def login_page():
    st.title("Login")
    #st.info("Default login: username = admin, password = admin123")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if verify_password(username, password):
            st.session_state.authenticated = True
            st.session_state.username = username
            st.rerun()
        else:
            st.error("Invalid username or password")

# Product management page
def product_management():
    st.title("Product Management")
    st.write(f"Welcome, {st.session_state.username}!")
    
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.rerun()
    
    st.header("Product Data")
    
    # Filter options
    st.subheader("Filter Products")
    col1, col2 = st.columns(2)
    
    # Default category to "All" in case query fails
    selected_category = "All"
    
    with col1:
        categories = run_query("SELECT DISTINCT category FROM products")
        if categories is not None and not categories.empty:
            category_list = ["All"] + categories["category"].tolist()
            selected_category = st.selectbox("Category", category_list)
    
    with col2:
        price_range = st.slider(
            "Price Range", 
            min_value=0.0, 
            max_value=2000.0, 
            value=(0.0, 2000.0),
            step=10.0
        )
    
    # Build query based on filters
    query = "SELECT * FROM products WHERE 1=1"
    params = {}
    
    if selected_category != "All":
        query += " AND category = :category"
        params["category"] = selected_category
    
    query += " AND price BETWEEN :min_price AND :max_price"
    params["min_price"] = price_range[0]
    params["max_price"] = price_range[1]
    
    # Display filtered products
    products = run_query(query, params)
    if products is not None:
        st.dataframe(products)
    else:
        st.info("No products found or unable to fetch products.")
    
    # Add new product form
    st.header("Add New Product")
    with st.form("new_product_form"):
        name = st.text_input("Product Name")
        category = st.text_input("Category")
        price = st.number_input("Price", min_value=0.01, step=0.01)
        inventory = st.number_input("Inventory", min_value=0, step=1)
        
        submit = st.form_submit_button("Add Product")
        
        if submit:
            if name and category and price > 0:
                insert_query = """
                INSERT INTO products (name, category, price, inventory) 
                VALUES (:name, :category, :price, :inventory)
                """
                if execute_query(insert_query, {
                    "name": name, 
                    "category": category, 
                    "price": price, 
                    "inventory": inventory
                }):
                    st.success("Product added successfully!")
                    # Clear cache to reflect new data
                    st.cache_data.clear()
                    st.rerun()
            else:
                st.error("Please fill all required fields")

# Main app
def main():
    st.set_page_config(page_title="Streamlit MySQL Integration", page_icon="🛒", layout="wide")
    
    # Initialize session state for authentication
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "username" not in st.session_state:
        st.session_state.username = None
    
    # Display appropriate page based on authentication status
    if not st.session_state.authenticated:
        login_page()
    else:
        product_management()

if __name__ == "__main__":
    main()