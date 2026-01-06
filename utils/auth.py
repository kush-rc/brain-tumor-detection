"""
Authentication and user management system
Uses CSV file for user storage
"""

import streamlit as st
import bcrypt
import pandas as pd
from pathlib import Path
from datetime import datetime

# User database file
DATA_DIR = Path("data")
USERS_FILE = DATA_DIR / "users.csv"

def hash_password(password):
    """
    Hash a password using bcrypt
    
    Args:
        password: Plain text password
    
    Returns:
        Hashed password string
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    """
    Verify a password against its hash
    
    Args:
        password: Plain text password
        hashed: Hashed password
    
    Returns:
        Boolean indicating match
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def init_users_db():
    """Initialize users CSV file with default admin"""
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        if not USERS_FILE.exists():
            # Create default admin user
            default_users = pd.DataFrame([{
                'username': 'admin',
                'password': hash_password('admin123'),
                'role': 'admin',
                'email': 'admin@braintumordetection.ai',
                'full_name': 'System Administrator',
                'created_at': datetime.now().isoformat(),
                'last_login': None
            }])
            
            default_users.to_csv(USERS_FILE, index=False)
        
        return True
    
    except Exception as e:
        st.error(f"Error initializing users: {e}")
        return False

def load_users():
    """
    Load users from CSV file
    
    Returns:
        Dictionary of users
    """
    try:
        init_users_db()
        
        df = pd.read_csv(USERS_FILE)
        
        # Convert to dictionary
        users = {}
        for _, row in df.iterrows():
            username = row['username']
            users[username] = {
                'password': row['password'],
                'role': row['role'],
                'email': row['email'],
                'full_name': row['full_name'],
                'created_at': row['created_at'],
                'last_login': row.get('last_login', None)
            }
        
        return users
    
    except Exception as e:
        st.error(f"Error loading users: {e}")
        return {}

def save_users(users):
    """
    Save users to CSV file
    
    Args:
        users: Dictionary of users
    """
    try:
        # Convert dictionary to DataFrame
        users_list = []
        for username, info in users.items():
            user_data = {'username': username}
            user_data.update(info)
            users_list.append(user_data)
        
        df = pd.DataFrame(users_list)
        df.to_csv(USERS_FILE, index=False)
        
        return True
    
    except Exception as e:
        st.error(f"Error saving users: {e}")
        return False

def authenticate_user(username, password):
    """
    Authenticate a user
    
    Args:
        username: Username
        password: Password
    
    Returns:
        User dict if authenticated, None otherwise
    """
    users = load_users()
    
    if username in users:
        if verify_password(password, users[username]['password']):
            # Update last login
            users[username]['last_login'] = datetime.now().isoformat()
            save_users(users)
            return users[username]
    
    return None

def register_user(username, password, email, full_name, role="user"):
    """
    Register a new user
    
    Args:
        username: Username
        password: Password
        email: Email address
        full_name: Full name
        role: User role (admin/doctor/user)
    
    Returns:
        Boolean indicating success
    """
    try:
        users = load_users()
        
        if username in users:
            st.error("❌ Username already exists!")
            return False
        
        users[username] = {
            "password": hash_password(password),
            "role": role,
            "email": email,
            "full_name": full_name,
            "created_at": datetime.now().isoformat(),
            "last_login": None
        }
        
        save_users(users)
        return True
    
    except Exception as e:
        st.error(f"Error registering user: {e}")
        return False

# Rest of the functions remain the same (login_form, logout, require_login, get_current_user)
def login_form():
    """Display login form"""
    st.markdown("### 🔐 Login")
    
    login_tab, register_tab = st.tabs(["Login", "Register"])
    
    with login_tab:
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            submit = st.form_submit_button("🔓 Login", use_container_width=True)
            
            if submit:
                if username and password:
                    user = authenticate_user(username, password)
                    
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.user_role = user['role']
                        st.session_state.user_email = user['email']
                        st.session_state.user_full_name = user['full_name']
                        st.success(f"✅ Welcome back, {user['full_name']}!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
                else:
                    st.warning("⚠️ Please enter both username and password")
    
    with register_tab:
        with st.form("register_form"):
            new_username = st.text_input("Username*", placeholder="Choose a username")
            new_full_name = st.text_input("Full Name*", placeholder="Enter your full name")
            new_email = st.text_input("Email*", placeholder="your.email@example.com")
            new_password = st.text_input("Password*", type="password", placeholder="Choose a strong password")
            confirm_password = st.text_input("Confirm Password*", type="password", placeholder="Re-enter password")
            
            register_submit = st.form_submit_button("📝 Register", use_container_width=True)
            
            if register_submit:
                if not all([new_username, new_full_name, new_email, new_password, confirm_password]):
                    st.warning("⚠️ Please fill in all fields")
                elif new_password != confirm_password:
                    st.error("❌ Passwords do not match")
                elif len(new_password) < 6:
                    st.error("❌ Password must be at least 6 characters")
                else:
                    if register_user(new_username, new_password, new_email, new_full_name):
                        st.success("✅ Registration successful! Please login.")
                        st.balloons()
    
    st.info("""
    **Default Admin Credentials:**
    - Username: `admin`
    - Password: `admin123`
    
    ⚠️ Please change the default password after first login!
    """)

def logout():
    """Logout current user"""
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.user_role = None
    st.session_state.user_email = None
    st.session_state.user_full_name = None
    st.rerun()

def require_login(allowed_roles=None):
    """
    Require login for a page
    
    Args:
        allowed_roles: List of allowed roles (None = all logged in users)
    
    Returns:
        Boolean indicating if user has access
    """
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        st.warning("🔒 Please login to access this page")
        login_form()
        return False
    
    if allowed_roles and st.session_state.user_role not in allowed_roles:
        st.error("🚫 You don't have permission to access this page")
        return False
    
    return True

def get_current_user():
    """
    Get current logged in user info
    
    Returns:
        Dict with user info or None
    """
    if st.session_state.get('logged_in'):
        return {
            'username': st.session_state.username,
            'role': st.session_state.user_role,
            'email': st.session_state.user_email,
            'full_name': st.session_state.user_full_name
        }
    return None
