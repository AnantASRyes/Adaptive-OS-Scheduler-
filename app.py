import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -------------------- Page Configuration --------------------

st.set_page_config(
    page_title="Adaptive OS Scheduler for Real-Time Systems",
    layout="wide"
)

st.title("Adaptive OS Scheduler for Real-Time Systems")
st.write(
    "This application simulates Rate Monotonic Scheduling (RMS), "
    "Earliest Deadline First (EDF), and an Adaptive Scheduler using Python and Streamlit."
)

# -------------------- Helper Functions --------------------


def compute_utilization(tasks):
    """
    Compute total utilization of the task set as sum(C_i / T_i).
    """
    total = 0.0
    for t in tasks:
        C = float(t["Execution Time"])
        T = float(t["Period"])
        if T > 0:
            total += C / T
    return total


def simulate_scheduler(tasks, mode="Adaptive", sim_time=50, util_threshold=0.7):
    """
    Simulate real-time scheduling for the given task set.

    Parameters:
        tasks: list of dicts with keys:
            Name, Execution Time, Period, Deadline
        mode: "RMS", "EDF", or "Adaptive"
        sim_time: total time units to simulate
        util_threshold: threshold for adaptive switching

    Returns:
        schedule: list of (time, task_name)
        total_misses: dict of task_name -> missed deadlines count
        util_percent: simulated CPU utilization in %
        U: theoretical utilization sum ΣC_i / T_i
        used_algo: final algorithm used at the end of simulation
    """
    # Precompute utilization
    U = compute_utilization(tasks)

    # Decide base algorithm if Adaptive
    if mode == "Adaptive":
        if U <= util_threshold:
            current_algo = "RMS"
        else:
            current_algo = "EDF"
    else:
        current_algo = mode

    # Initialize runtime state for each task
    state = {}
    for t in tasks:
        name = t["Name"]
        C = int(t["Execution Time"])
        T = int(t["Period"])
        D = int(t["Deadline"])
        state[name] = {
            "C": C,
            "T": T,
            "D": D,
            "next_release": 0,
            "remaining": 0,
            "abs_deadline": 0,
            "misses": 0,
        }

    schedule = []
    total_idle = 0
    recent_misses = 0  # used for adaptive switching

    for time in range(sim_time):
        # Release jobs at the start of each time unit
        for name, s in state.items():
            if time >= s["next_release"]:
                # If previous job is not finished and deadline passed -> miss
                if s["remaining"] > 0 and time > s["abs_deadline"]:
                    s["misses"] += 1
                    recent_misses += 1
                # Release new job
                s["remaining"] = s["C"]
                s["abs_deadline"] = time + s["D"]
                s["next_release"] += s["T"]

        # Collect ready tasks
        ready = [name for name, s in state.items() if s["remaining"] > 0]

        # Adaptive switching based on recent misses
        if mode == "Adaptive":
            # If too many misses recently, switch to EDF
            if recent_misses >= 3:
                current_algo = "EDF"

        # If no task is ready, CPU is idle
        if not ready:
            schedule.append((time, "IDLE"))
            total_idle += 1
        else:
            # Choose task according to current algorithm
            if current_algo == "RMS":
                # Choose task with smallest period
                chosen = min(ready, key=lambda n: state[n]["T"])
            else:  # EDF
                # Choose task with earliest absolute deadline
                chosen = min(ready, key=lambda n: state[n]["abs_deadline"])

            schedule.append((time, chosen))
            state[chosen]["remaining"] -= 1

    # Collect statistics
    total_misses = {name: s["misses"] for name, s in state.items()}
    util_percent = 100.0 * (1 - total_idle / sim_time)

    return schedule, total_misses, util_percent, U, current_algo


def plot_gantt(schedule):
    """
    Plot a simple Gantt-like chart from the schedule list of (time, task_name).
    """
    # Collect segments as (task, start, end)
    segments = []
    if not schedule:
        return

    current_task = schedule[0][1]
    start_time = schedule[0][0]

    for i in range(1, len(schedule)):
        t, task = schedule[i]
        prev_t, prev_task = schedule[i - 1]
        if task != prev_task:
            segments.append((prev_task, start_time, prev_t + 1))
            start_time = t
            current_task = task

    # Append the last segment
    last_time, last_task = schedule[-1]
    segments.append((last_task, start_time, last_time + 1))

    # Map tasks to y-axis positions
    tasks = sorted(list({s[0] for s in segments}))
    task_to_y = {task: i for i, task in enumerate(tasks)}

    fig, ax = plt.subplots()
    for task, start, end in segments:
        y = task_to_y[task]
        ax.barh(y, end - start, left=start)
    ax.set_yticks(list(task_to_y.values()))
    ax.set_yticklabels(tasks)
    ax.set_xlabel("Time")
    ax.set_ylabel("Task / IDLE")
    ax.set_title("Schedule Gantt Chart")
    st.pyplot(fig)


# -------------------- UI Layout --------------------

st.subheader("Task Set Configuration")

default_data = {
    "Name": ["T1", "T2", "T3"],
    "Execution Time": [1, 2, 1],
    "Period": [4, 5, 8],
    "Deadline": [4, 5, 8],
}
df = pd.DataFrame(default_data)

st.write("Edit the task parameters below as needed:")

task_df = st.data_editor(df, num_rows="dynamic")

col1, col2, col3 = st.columns(3)
with col1:
    mode = st.selectbox("Scheduling Mode", ["RMS", "EDF", "Adaptive"])
with col2:
    sim_time = st.number_input(
        "Simulation Time (units)",
        min_value=10,
        max_value=500,
        value=50,
        step=10
    )
with col3:
    util_threshold = st.slider(
        "Adaptive Utilization Threshold",
        0.1,
        0.95,
        0.7,
        0.05
    )

if st.button("Run Simulation"):
    try:
        tasks = []
        for _, row in task_df.iterrows():
            name = str(row["Name"])
            C = int(row["Execution Time"])
            T = int(row["Period"])
            D = int(row["Deadline"])
            if C <= 0 or T <= 0 or D <= 0:
                st.error("All task parameters must be positive.")
                st.stop()
            if C > D:
                st.warning(
                    f"Execution time is greater than deadline for task {name}. "
                    "This may cause deadline misses."
                )
            tasks.append(
                {
                    "Name": name,
                    "Execution Time": C,
                    "Period": T,
                    "Deadline": D,
                }
            )

        schedule, miss_dict, util_percent, U, used_algo = simulate_scheduler(
            tasks,
            mode=mode,
            sim_time=sim_time,
            util_threshold=util_threshold
        )

        st.success(f"Simulation completed using algorithm: {used_algo}")
        st.write(f"Total CPU Utilization (simulated): **{util_percent:.2f}%**")
        st.write(f"Theoretical Utilization Sum (ΣC/T): **{U:.3f}**")

        st.subheader("Deadline Misses per Task")
        miss_df = pd.DataFrame(
            [{"Task": name, "Misses": count} for name, count in miss_dict.items()]
        )
        st.table(miss_df)

        st.subheader("Schedule Gantt Chart")
        plot_gantt(schedule)

        st.subheader("Raw Schedule (first 100 entries)")
        sched_df = pd.DataFrame(schedule, columns=["Time", "Task"])
        st.dataframe(sched_df.head(100))

    except Exception as e:
        st.error(f"Error during simulation: {e}")
else:
    st.info("Configure the tasks and click 'Run Simulation' to start the simulation.")
