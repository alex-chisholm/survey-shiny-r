import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from streamlit.runtime.scriptrunner import get_script_run_ctx

# Initialize session state if not already done
if 'current_question' not in st.session_state:
    st.session_state.current_question = 1
if 'responses' not in st.session_state:
    # Create fake data
    np.random.seed(123)
    n_responses = 50
    roles = ["Business Analyst", "Data Analyst", "Data Scientist", "Data Engineer"]
    st.session_state.responses = pd.DataFrame({
        "role": np.random.choice(roles, n_responses),
        "data_comfort": np.random.randint(1, 6, n_responses),
        "comm_comfort": np.random.randint(1, 6, n_responses)
    })
    st.session_state.roles = roles

# Navigation functions
def next_question():
    st.session_state.current_question += 1

def prev_question():
    st.session_state.current_question -= 1

def skip_to_results():
    st.session_state.current_question = -1

def submit_response():
    new_response = pd.DataFrame({
        "role": [st.session_state.role],
        "data_comfort": [st.session_state.data_comfort],
        "comm_comfort": [st.session_state.comm_comfort]
    })
    st.session_state.responses = pd.concat([st.session_state.responses, new_response], ignore_index=True)
    st.session_state.current_question = -1

# App layout
st.title("Data Professional Survey")

# Survey Section
if st.session_state.current_question > 0:
    with st.container():
        if st.session_state.current_question == 1:
            st.header("Question 1 of 3")
            st.radio(
                "Which role best describes you?",
                options=st.session_state.roles,
                key="role"
            )
            col1, col2 = st.columns([1, 4])
            with col1:
                st.button("Next", on_click=next_question)
            with col2:
                st.button("Skip to results", on_click=skip_to_results)

        elif st.session_state.current_question == 2:
            st.header("Question 2 of 3")
            st.slider(
                "How comfortable are you manipulating data?",
                min_value=1,
                max_value=5,
                value=3,
                key="data_comfort"
            )
            col1, col2, col3 = st.columns([1, 1, 4])
            with col1:
                st.button("Previous", on_click=prev_question)
            with col2:
                st.button("Next", on_click=next_question)
            with col3:
                st.button("Skip to results ", on_click=skip_to_results)

        elif st.session_state.current_question == 3:
            st.header("Question 3 of 3")
            st.slider(
                "How comfortable are you communicating data?",
                min_value=1,
                max_value=5,
                value=3,
                key="comm_comfort"
            )
            col1, col2, col3 = st.columns([1, 1, 4])
            with col1:
                st.button("Previous ", on_click=prev_question)
            with col2:
                st.button("Submit", on_click=submit_response)
            with col3:
                st.button("Skip to results  ", on_click=skip_to_results)

# Results Section
else:
    st.header("Survey Results")
    
    # Role filter
    role_filter = st.selectbox(
        "Filter by Role:",
        options=["All"] + list(st.session_state.responses["role"].unique())
    )
    
    # Filter data based on selection
    data = st.session_state.responses
    if role_filter != "All":
        data = data[data["role"] == role_filter]
    
    # Create two columns for the plots
    col1, col2 = st.columns(2)
    
    with col1:
        fig1, ax1 = plt.subplots(figsize=(8, 6))
        ax1.hist(data["data_comfort"], bins=np.arange(1, 7) - 0.5,
                rwidth=0.8, color="steelblue")
        ax1.set_title("Data Manipulation Comfort Level")
        ax1.set_xlabel("Comfort Level (1-5)")
        ax1.set_ylabel("Count")
        ax1.grid(True, alpha=0.3)
        st.pyplot(fig1)
    
    with col2:
        fig2, ax2 = plt.subplots(figsize=(8, 6))
        ax2.hist(data["comm_comfort"], bins=np.arange(1, 7) - 0.5,
                rwidth=0.8, color="forestgreen")
        ax2.set_title("Data Communication Comfort Level")
        ax2.set_xlabel("Comfort Level (1-5)")
        ax2.set_ylabel("Count")
        ax2.grid(True, alpha=0.3)
        st.pyplot(fig2)