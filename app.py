import streamlit as st
import pandas as pd


# Load Data and clean column names immediately
try:
    ref_df = pd.read_csv('carbon_ref.csv')
    ref_df.columns = ref_df.columns.str.strip()
    
    grid_df = pd.read_csv('grid_intensity.csv')
    grid_df.columns = grid_df.columns.str.strip()
except Exception as e:
    st.error(f"Error loading CSV files: {e}")
    st.stop()


st.set_page_config(page_title="Carbon Budgeter", page_icon="🌱")
st.title("🌱 Personal Carbon Budgeter")


# --- ONBOARDING QUIZ ---
if 'baseline' not in st.session_state:
    with st.form("quiz"):
        st.subheader("Calculate Your Daily Baseline")
        state_options = grid_df.iloc[:, 0].tolist() 
        state = st.selectbox("Where do you live?", state_options)
        diet = st.selectbox("Dietary Habit", ["Vegan", "Vegetarian", "Average", "Meat-Heavy"])
        submit = st.form_submit_button("Set My Budget")
        
        if submit:
            diet_map = {"Vegan": 2000, "Vegetarian": 4000, "Average": 6000, "Meat-Heavy": 10000}
            st.session_state.baseline = 10000 + diet_map[diet]
            st.session_state.state = state
            st.session_state.spent = 0
            st.rerun()


# --- MAIN DASHBOARD ---
if 'baseline' in st.session_state:
    state_col = grid_df.columns[0]
    intensity_col = grid_df.columns[1]
    
    # Safely find the intensity
    try:
        intensity = grid_df[grid_df[state_col] == st.session_state.state][intensity_col].values[0]
    except IndexError:
        intensity = 340 # Default to US Average if lookup fails
    
    st.metric("Daily Budget Remaining", f"{st.session_state.baseline - st.session_state.spent}g")
    
    st.subheader("Log Activity")
    for index, row in ref_df.iterrows():
        act_name = row.iloc[1] 
        act_cost = row.iloc[2]
        if st.button(f"Log {act_name} ({act_cost}g)"):
            st.session_state.spent += act_cost
            st.toast(f"Logged {act_name}!")
            
    if st.button("Reset Day"):
        st.session_state.spent = 0
        st.rerun()