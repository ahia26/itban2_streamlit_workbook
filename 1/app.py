import streamlit as st

# Title
st.title("User Input App")

# Header
st.header("Enter Your Details")

# Text input field
name = st.text_input("What's your name?")

# Number input field (age)
age = st.number_input("Enter your age:", min_value=1, max_value=120, step=1)

# Dropdown (favorite color)
color = st.selectbox("Pick your favorite color:", ["Red", "Green", "Blue", "Yellow", "Other"])

# Checkbox (agreement)
agree = st.checkbox("I agree to the terms and conditions")

# Display output dynamically
if name and age and agree:
    st.write(f"Hello, {name}! You are {age} years old and love {color}. Thanks for agreeing!")
