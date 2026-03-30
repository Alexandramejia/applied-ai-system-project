import streamlit as st

from pawpal_system import Owner, Pet, Task, Priority, TaskCategory, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

if "owner" not in st.session_state:
    st.session_state.owner = Owner(
        first_name="Jordan",
        last_name="Smith",
        email="jordan@example.com",
        available_minutes_per_day=120,
        max_daily_budget=50.0,
    )

owner: Owner = st.session_state.owner

with st.sidebar:
    st.header("Owner Settings")
    with st.form("owner_form"):
        first = st.text_input("First name", value=owner.first_name)
        last = st.text_input("Last name", value=owner.last_name)
        email = st.text_input("Email", value=owner.email)
        mins = st.number_input(
            "Available minutes / day", min_value=10, max_value=1440, value=owner.available_minutes_per_day
        )
        budget = st.number_input(
            "Max daily budget ($)", min_value=0.0, max_value=1000.0,
            value=owner.max_daily_budget, step=5.0
        )
        if st.form_submit_button("Save owner"):
            owner.first_name = first
            owner.last_name = last
            owner.email = email
            owner.available_minutes_per_day = int(mins)
            owner.max_daily_budget = float(budget)
            st.success("Owner updated!")

    st.caption(f"Logged in as **{owner.get_full_name()}**")


# Add a Pet 
st.subheader("Add a Pet")
with st.form("add_pet_form"):
    col1, col2 = st.columns(2)
    with col1:
        pet_first = st.text_input("First name", value="Mochi")
        pet_species = st.selectbox("Species", ["dog", "cat", "rabbit", "bird", "other"])
        pet_age = st.number_input("Age (years)", min_value=0, max_value=30, value=2)
    with col2:
        pet_last = st.text_input("Last name", value="Smith")
        pet_breed = st.text_input("Breed", value="Mixed")

    if st.form_submit_button("Add pet"):
        new_pet = Pet(
            first_name=pet_first,
            last_name=pet_last,
            species=pet_species,
            breed=pet_breed,
            age=int(pet_age),
        )
        owner.add_pet(new_pet)
        st.success(f"Added **{new_pet.get_full_name()}** ({pet_species})!")

st.divider()

# Current Pets & Add Tasks 
pets = owner.get_pets()

if not pets:
    st.info("No pets yet. Add one above.")
else:
    st.subheader("Your Pets")

    for pet in pets:
        with st.expander(f"🐾 {pet.get_full_name()} — {pet.species}, age {pet.age}"):
            tasks = pet.get_tasks()

            if tasks:
                st.write("**Scheduled tasks:**")
                task_rows = [
                    {
                        "Task": t.get_full_name(),
                        "Duration (min)": t.duration_minutes,
                        "Priority": t.priority.value,
                        "Done": "✓" if t.is_complete else "",
                    }
                    for t in tasks
                ]
                st.table(task_rows)
            else:
                st.caption("No tasks yet for this pet.")

            with st.form(f"add_task_{pet.id}"):
                st.write("**Add a task**")
                tc1, tc2, tc3 = st.columns(3)
                with tc1:
                    task_name = st.text_input("Task name", value="Morning walk", key=f"name_{pet.id}")
                    task_category = st.selectbox(
                        "Category",
                        [c.value for c in TaskCategory],
                        key=f"cat_{pet.id}",
                    )
                with tc2:
                    task_duration = st.number_input(
                        "Duration (min)", min_value=1, max_value=240, value=20, key=f"dur_{pet.id}"
                    )
                    task_priority = st.selectbox(
                        "Priority",
                        [p.value for p in Priority],
                        key=f"pri_{pet.id}",
                    )
                with tc3:
                    task_cost = st.number_input(
                        "Cost ($)", min_value=0.0, max_value=500.0,
                        value=0.0, step=1.0, key=f"cost_{pet.id}"
                    )
                    task_location = st.text_input("Location", value="", key=f"loc_{pet.id}")

                if st.form_submit_button("Add task"):
                    new_task = Task(
                        name=task_name,
                        category=TaskCategory(task_category),
                        priority=Priority(task_priority),
                        duration_minutes=int(task_duration),
                        cost=float(task_cost),
                        location=task_location,
                    )
                    pet.add_task(new_task)
                    st.success(f"Added **{new_task.get_full_name()}** to {pet.get_full_name()}!")

            if st.button("Remove this pet", key=f"remove_{pet.id}"):
                owner.remove_pet(pet.id)
                st.rerun()

st.divider()

# Generate Schedule 
st.subheader("Generate Daily Schedule")
st.caption(
    f"Fits tasks into **{owner.available_minutes_per_day} min** and "
    f"**${owner.max_daily_budget:.2f}** for {owner.get_full_name()}."
)

# Sort control lives outside the button so changing it doesn't regenerate the schedule
sort_mode = st.radio("Sort schedule by", ["Time", "Priority"], horizontal=True, key="sort_mode")

if st.button("Generate schedule", type="primary"):
    if not pets:
        st.warning("Add at least one pet with tasks first.")
    else:
        scheduler = Scheduler()
        st.session_state.schedule = scheduler.generate_plan(owner)

if "schedule" in st.session_state:
    schedule = st.session_state.schedule
    st.success(f"Schedule built for {schedule.date}!")

    if schedule.items:
        if schedule.has_conflicts():
            n = len(schedule.conflicts)
            st.error(f"⚠️ {n} conflict{'s' if n > 1 else ''} detected — see details below the table.")

        sorted_items = (
            schedule.sort_by_time() if sort_mode == "Time"
            else schedule.sort_by_priority()
        )

        _PRIORITY_ICON = {"urgent": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}

        schedule_rows = [
            {
                "Time": item.time_slot,
                "Task": item.task.get_full_name(),
                "Pet(s)": " & ".join(p.get_full_name() for p in item.get_all_pets()),
                "Min": item.task.duration_minutes,
                "Cost": f"${item.task.cost:.2f}",
                "Priority": f"{_PRIORITY_ICON.get(item.task.priority.value, '')} {item.task.priority.value}",
            }
            for item in sorted_items
        ]
        st.dataframe(schedule_rows, use_container_width=True, hide_index=True)

        col_t, col_c = st.columns(2)
        col_t.metric("Total time", f"{schedule.get_total_duration()} min")
        col_c.metric("Total cost", f"${schedule.get_total_cost():.2f}")

        if schedule.has_conflicts():
            st.divider()
            st.subheader("Conflict Details")
            for conflict in schedule.conflicts:
                label = conflict.conflict_type.value.replace("_", " ").title()
                st.error(f"**{label}** — {conflict.message}")
                st.warning(f"Suggested fix: {conflict.suggest_fix()}")
    else:
        st.info("No tasks fit within the current time/budget constraints.")

    with st.expander("Reasoning"):
        st.text(schedule.reasoning)
