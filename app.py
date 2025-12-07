import streamlit as st
import pandas as pd

st.set_page_config(page_title="Adaptive OS Scheduler", layout="wide")

st.title("Adaptive OS Scheduler - Task Input Module")

st.subheader("Enter Task Parameters")

default_data = {
    "Name": ["T1", "T2", "T3"],
    "Execution Time": [1, 2, 1],
    "Period": [4, 5, 8],
    "Deadline": [4, 5, 8],
}

task_df = st.data_editor(pd.DataFrame(default_data), num_rows="dynamic")

st.subheader("Validation Check")

valid = True
for _, row in task_df.iterrows():
    if row["Execution Time"] <= 0 or row["Period"] <= 0 or row["Deadline"] <= 0:
        valid = False
        st.error("All task parameters must be positive.")
    if row["Execution Time"] > row["Deadline"]:
        valid = False
        st.warning(f"Execution time > deadline for task {row['Name']} may cause deadline misses.")

if valid:
    st.success("Task input is valid.")
