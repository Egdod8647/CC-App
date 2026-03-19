import streamlit as st
import pandas as pd


# Load Data
ref_df = pd.read_csv('carbon_ref.csv')
grid_df = pd.read_csv('grid_intensity.csv')


st.set_page_config(page_title="Carbon Budgeter", page_icon="🌱")
st.title("🌱 Personal Carbon Budgeter")


# --- ONBOARDING QUIZ ---
if 'baseline' not in st.session_state:
    with st.form("quiz"):
        st.subheader("Calculate Your Daily Baseline")
        state = st.selectbox("Where do you live?", grid_df['State'].tolist())
        diet = st.selectbox("Dietary Habit", ["Vegan", "Vegetarian", "Average", "Meat-Heavy"])
        submit = st.form_submit_button("Set My Budget")
        if submit:
            # Simplified logic: Base (10k) + Diet + State factor
            diet_map = {"Vegan": 2000, "Vegetarian": 4000, "Average": 6000, "Meat-Heavy": 10000}
            st.session_state.baseline = 10000 + diet_map[diet]
            st.session_state.state = state
            st.session_state.spent = 0
            st.rerun()


# --- MAIN DASHBOARD ---
if 'baseline' in st.session_state:
    # Get regional intensity
    intensity = grid_df[grid_df['State'] == st.session_state.state]['Intensity'].values[0]
    
    st.metric("Daily Budget Remaining", f"{st.session_state.baseline - st.session_state.spent}g")
    
    st.subheader("Log Activity")
    for index, row in ref_df.iterrows():
        if st.button(f"Log {row['Activity']} ({row['Base_Cost']}g)"):
            st.session_state.spent += row['Base_Cost']
            st.info(f"💡 Swap Tip: {row['Swap_Suggestion']} saves {row['Swap_Savings']}g!")
            
    if st.button("Reset Day"):
        st.session_state.spent = 0
        st.rerun()