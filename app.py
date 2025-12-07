import streamlit as st
import pandas as pd

st.set_page_config(page_title="Adaptive OS Scheduler", layout="wide")

st.title("Adaptive OS Scheduler - RMS Scheduling Module")

# -------- Task Input --------
default_data = {
    "Name": ["T1", "T2", "T3"],
    "Execution Time": [1, 2, 1],
    "Period": [4, 5, 8],
    "Deadline": [4, 5, 8],
}

task_df = st.data_editor(pd.DataFrame(default_data), num_rows="dynamic")


# -------- RMS Scheduling Implementation --------
def simulate_rms(tasks, sim_time=20):
    state = {}

    # Initialize state for each task
    for _, row in tasks.iterrows():
        name = row["Name"]
        state[name] = {
            "C": row["Execution Time"],
            "T": row["Period"],
            "D": row["Deadline"],
            "remaining": 0,
            "next_release": 0,
            "abs_deadline": 0,
        }

    schedule = []

    for time in range(sim_time):
        # Release new jobs
        for name, s in state.items():
            if time >= s["next_release"]:
                s["remaining"] = s["C"]
                s["abs_deadline"] = time + s["D"]
                s["next_release"] += s["T"]

        # Ready tasks
        ready = [name for name, s in state.items() if s["remaining"] > 0]

        if not ready:
            schedule.append((time, "IDLE"))
        else:
            # RMS = smallest period → highest priority
            chosen = min(ready, key=lambda n: state[n]["T"])
            state[chosen]["remaining"] -= 1
            schedule.append((time, chosen))

    return schedule


# -------- UI Button --------
if st.button("Run RMS"):
    schedule = simulate_rms(task_df)
    st.success("RMS Simulation Completed!")
    st.write(schedule[:50])
