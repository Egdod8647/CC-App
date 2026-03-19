import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. Page Config
st.set_page_config(page_title="Carbon Budgeter", page_icon="🌱")
st.title("🌱 Personal Carbon Budgeter")

# 2. Load Data and clean column names
try:
    ref_df = pd.read_csv('carbon_ref.csv')
    ref_df.columns = ref_df.columns.str.strip()
    
    grid_df = pd.read_csv('grid_intensity.csv')
    grid_df.columns = grid_df.columns.str.strip()
    
    # Initialize Google Sheets Connection
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Setup Error: {e}")
    st.stop()

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
        intensity = 340 
    
    # Header Metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Daily Budget Remaining", f"{st.session_state.baseline - st.session_state.spent}g")
    with col2:
        st.metric("Local Grid Intensity", f"{intensity}g/kWh")
    
    # Activity Logging
    st.subheader("Log Activity")
    # We display buttons in a grid to save space
    cols = st.columns(2)
    for index, row in ref_df.iterrows():
        act_name = row.iloc[1] 
        act_cost = row.iloc[2]
        # Use the modulus operator to alternate between column 1 and 2
        with cols[index % 2]:
            if st.button(f"Log {act_name} ({act_cost}g)"):
                st.session_state.spent += act_cost
                st.toast(f"Logged {act_name}!")
                st.rerun()

    # Tree Visualization
    st.divider()
    daily_tree_absorption = 57.5  # Grams a tree absorbs per day
    trees_equivalent = st.session_state.spent / daily_tree_absorption

    col_tree, col_info = st.columns([1, 4])
    with col_tree:
        st.title("🌳")
    with col_info:
        st.write(f"Your activity today required the full daily work of **{trees_equivalent:.1f} mature trees** to offset.")

    # Reset and Save Logic
    st.divider()
    st.subheader("🏁 End of Day")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Save Progress to Cloud", use_container_width=True):
            new_row = pd.DataFrame([{
                "Date": pd.Timestamp.now().strftime("%Y-%m-%d"),
                "State": st.session_state.state,
                "Spent": st.session_state.spent,
                "Baseline": st.session_state.baseline
            }])
            try:
                existing_data = conn.read(worksheet="Sheet1")
                updated_df = pd.concat([existing_data, new_row], ignore_index=True)
                conn.update(worksheet="Sheet1", data=updated_df)
                st.success("Data synced!")
            except Exception as e:
                st.error(f"Connection failed: {e}")
    
    with c2:
        if st.button("Reset Day", use_container_width=True):
            st.session_state.spent = 0
            st.rerun()
