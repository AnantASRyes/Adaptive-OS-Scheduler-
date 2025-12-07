def simulate_edf(tasks, sim_time=20):
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
            "misses": 0
        }

    schedule = []

    for time in range(sim_time):

        # Release new jobs
        for name, s in state.items():
            if time >= s["next_release"]:

                # deadline missed?
                if s["remaining"] > 0 and time > s["abs_deadline"]:
                    s["misses"] += 1

                s["remaining"] = s["C"]
                s["abs_deadline"] = time + s["D"]
                s["next_release"] += s["T"]

        # Ready queue
        ready = [name for name, s in state.items() if s["remaining"] > 0]

        if not ready:
            schedule.append((time, "IDLE"))
        else:
            # EDF = earliest absolute deadline
            chosen = min(ready, key=lambda n: state[n]["abs_deadline"])
            state[chosen]["remaining"] -= 1
            schedule.append((time, chosen))

    return schedule, {name: s["misses"] for name, s in state.items()}  
    if st.button("Run EDF"):
    schedule, misses = simulate_edf(task_df)
    st.success("EDF Simulation Completed!")

    st.subheader("Schedule Output (First 50 slots):")
    st.write(schedule[:50])

    st.subheader("Deadline Misses Per Task:")
    st.write(misses)



