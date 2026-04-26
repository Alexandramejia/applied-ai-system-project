from datetime import datetime

import streamlit as st

from ai_service import generate_schedule_message
from pawpal_system import Owner, Pet, Task, Priority, TaskCategory, Scheduler


def _fmt_time(hhmm: str) -> str:
    """Convert 24-hour 'HH:MM' to '9:30 AM' style."""
    try:
        dt = datetime.strptime(hhmm.strip(), "%H:%M")
        hour = dt.hour % 12 or 12
        period = "AM" if dt.hour < 12 else "PM"
        return f"{hour}:{dt.strftime('%M')} {period}"
    except ValueError:
        return hhmm


def _fmt_slot(slot: str) -> str:
    """Convert '09:00 – 09:30' to '9:00 AM – 9:30 AM'."""
    parts = slot.split("–")
    if len(parts) == 2:
        return f"{_fmt_time(parts[0])} – {_fmt_time(parts[1])}"
    return slot

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

if "owner" not in st.session_state:
    st.session_state.owner = Owner(
        first_name="Jordan",
        last_name="Smith",
        available_minutes_per_day=120,
        max_daily_budget=50.0,
    )

owner: Owner = st.session_state.owner

with st.sidebar:
    st.header("Owner Settings")
    with st.form("owner_form"):
        first = st.text_input("First name", value=owner.first_name)
        last = st.text_input("Last name", value=owner.last_name)
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
        pet_gender = st.selectbox("Gender", ["male", "female", "unknown"])

    if st.form_submit_button("Add pet"):
        new_pet = Pet(
            first_name=pet_first,
            last_name=pet_last,
            species=pet_species,
            breed=pet_breed,
            age=int(pet_age),
            gender=pet_gender,
        )
        owner.add_pet(new_pet)
        st.session_state.schedule_stale = True
        st.rerun()

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
                for t in tasks:
                    col_info, col_btn = st.columns([5, 1])
                    with col_info:
                        st.markdown(
                            f"**{t.get_full_name()}** — {t.duration_minutes} min, "
                            f"{t.priority.value} priority"
                            + (f", starts {_fmt_time(t.start_time)}" if t.start_time else "")
                        )
                    with col_btn:
                        if st.button("Remove", key=f"remove_task_{t.id}"):
                            pet.remove_task(t.id)
                            st.session_state.schedule_stale = True
                            st.rerun()
            else:
                st.caption("No tasks yet for this pet.")

            with st.form(f"add_task_{pet.id}"):
                st.write("**Add a task**")
                tr1, tr2, tr3 = st.columns(3)
                with tr1:
                    task_name = st.text_input("Task name", value="Morning walk", key=f"name_{pet.id}")
                with tr2:
                    task_category = st.selectbox(
                        "Category",
                        [c.value for c in TaskCategory],
                        key=f"cat_{pet.id}",
                    )
                with tr3:
                    task_priority = st.selectbox(
                        "Priority",
                        [p.value for p in Priority],
                        key=f"pri_{pet.id}",
                    )

                tr4, tr5, tr6, tr7, tr8 = st.columns([1, 1, 1, 2, 2])
                with tr4:
                    task_hour = st.selectbox("Hour", list(range(1, 13)), key=f"hour_{pet.id}")
                with tr5:
                    task_minute = st.number_input("Min", min_value=0, max_value=59, value=0, key=f"min_{pet.id}")
                with tr6:
                    task_ampm = st.selectbox("AM/PM", ["AM", "PM"], key=f"ampm_{pet.id}")
                with tr7:
                    task_duration = st.number_input(
                        "Duration (min)", min_value=1, max_value=240, value=20, key=f"dur_{pet.id}"
                    )
                with tr8:
                    task_cost = st.number_input(
                        "Cost ($)", min_value=0.0, max_value=500.0,
                        value=0.0, step=1.0, key=f"cost_{pet.id}"
                    )

                if st.form_submit_button("Add task"):
                    hour_24 = (task_hour % 12) + (12 if task_ampm == "PM" else 0)
                    start_time_24 = f"{hour_24:02d}:{int(task_minute):02d}"
                    new_task = Task(
                        name=task_name,
                        category=TaskCategory(task_category),
                        priority=Priority(task_priority),
                        duration_minutes=int(task_duration),
                        cost=float(task_cost),
                        start_time=start_time_24,
                    )
                    pet.add_task(new_task)
                    st.session_state.schedule_stale = True
                    st.session_state.ai_message = ""
                    st.rerun()

            if st.button("Remove this pet", key=f"remove_{pet.id}"):
                owner.remove_pet(pet.id)
                st.session_state.schedule_stale = True
                st.session_state.ai_message = ""
                st.rerun()

st.divider()

# Generate Schedule 
st.subheader("Generate Daily Schedule")
st.caption(
    f"Fits tasks into **{owner.available_minutes_per_day} min** and "
    f"**${owner.max_daily_budget:.2f}** for {owner.get_full_name()}."
)

# Sort control lives outside the button so changing it doesn't regenerate the schedule
sort_mode = st.radio("View schedule as", ["✅ Today's Priorities", "🕐 Full Day Schedule"], horizontal=True, key="sort_mode")

if st.session_state.get("schedule_stale") and "schedule" in st.session_state:
    st.warning("Your pets or tasks changed — regenerate the schedule to include all updates.")

if st.button("Generate schedule", type="primary"):
    if not pets:
        st.warning("Add at least one pet with tasks first.")
    else:
        scheduler = Scheduler()
        st.session_state.schedule = scheduler.generate_plan(owner)
        st.session_state.schedule_stale = False
        with st.spinner("Personalizing your schedule summary..."):
            st.session_state.ai_message = generate_schedule_message(
                owner, st.session_state.schedule
            )

if "schedule" in st.session_state:
    schedule = st.session_state.schedule

    ai_msg = st.session_state.get("ai_message", "")
    if ai_msg:
        st.info(ai_msg)

    st.success(f"Schedule built for {schedule.date}!")

    if schedule.items:
        if schedule.has_conflicts():
            n = len(schedule.conflicts)
            st.error(f"⚠️ {n} conflict{'s' if n > 1 else ''} detected — see details below the table.")

        sorted_items = (
            schedule.sort_by_priority() if sort_mode == "✅ Today's Priorities"
            else schedule.sort_by_time()
        )

        _PRIORITY_ICON = {"urgent": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}

        schedule_rows = [
            {
                "Time": _fmt_slot(item.time_slot),
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
