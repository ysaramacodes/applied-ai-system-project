import streamlit as st
import pandas as pd
from datetime import datetime
from pawpal_system import Pet, Task, Owner, Schedule, Scheduler, get_or_create_owner, get_or_create_pet, get_or_create_task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
contact_info = st.text_input("Contact info", value="")

# Get or create owner from vault (session_state)
owner = get_or_create_owner(st.session_state, owner_name, contact_info)

st.markdown("### Pet Information")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
pet_age = st.number_input("Pet age (years)", min_value=0, max_value=30, value=2)
pet_sex = st.selectbox("Pet sex", ["Male", "Female"])

# Get or create pet from vault
pet = get_or_create_pet(st.session_state, pet_name, breed=species, age=pet_age, sex=pet_sex)

# Add pet to owner
if st.button("Add pet to owner"):
    if pet not in owner.pets:
        owner.add_pet(pet)
        st.success(f"✅ Added {pet_name} to {owner_name}'s pets!")
    else:
        st.info(f"{pet_name} is already in {owner_name}'s pets.")

if owner.pets:
    with st.expander(f"🐕 {owner_name}'s Pets ({len(owner.pets)})", expanded=True):
        cols = st.columns(len(owner.pets))
        for i, p in enumerate(owner.pets):
            with cols[i]:
                st.info(f"**{p.name}**")
                st.caption(f"{p.breed} • {p.age} years • {p.sex}")
else:
    st.info("No pets added yet.")

st.divider()

st.markdown("### Tasks")
st.caption("Add care tasks to your pet.")

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task description", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    frequency = st.selectbox("Frequency", ["one-time", "daily", "weekly", "monthly"])
with col4:
    pet_names = [p.name for p in owner.pets] if owner.pets else []
    if pet_names:
        selected_pet_name = st.selectbox("Pet", pet_names)
    else:
        selected_pet_name = None

if st.button("Create and assign task"):
    if not owner.pets:
        st.error("❌ Please add a pet first before creating tasks.")
    elif not selected_pet_name:
        st.error("❌ Please select a pet to assign the task to.")
    else:
        # Get or create task from vault
        task = get_or_create_task(st.session_state, task_title, duration=int(duration), frequency=frequency)

        # Assign task to the selected pet
        selected_pet = next((p for p in owner.pets if p.name == selected_pet_name), owner.pets[0])

        if task not in selected_pet.tasks:
            owner.create_task(selected_pet, task)
            st.success(f"✅ Task '{task_title}' assigned to {selected_pet.name}!")
        else:
            st.info(f"Task '{task_title}' is already assigned to {selected_pet.name}.")

# Display tasks for all pets using Scheduler
if owner.tasks:
    with st.expander(f"📋 All Tasks for {owner_name} ({len(owner.tasks)} total)", expanded=True):
        scheduler = Scheduler(owner=owner)
        
        for pet in owner.pets:
            if pet.tasks:
                with st.expander(f"🐾 {pet.name} ({len(pet.tasks)} tasks)"):
                    # Use scheduler to organize tasks by time, recurrence, etc.
                    organized_tasks = scheduler.organize_tasks(pet_name=pet.name, include_completed=False)
                    
                    task_data = []
                    for task in organized_tasks:
                        scheduled_time = ""
                        if task.time:
                            scheduled_time = task.time.strftime('%I:%M %p')
                        
                        task_data.append({
                            "Description": task.description,
                            "Duration (min)": task.duration,
                            "Frequency": task.frequency or "one-time",
                            "Scheduled": scheduled_time or "—",
                            "Status": "✅ Complete" if task.completion_status else "⏳ Pending"
                        })
                    st.dataframe(pd.DataFrame(task_data), use_container_width=True, hide_index=True)
else:
    st.info("No tasks yet. Add a pet and then create tasks.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generate a daily care plan based on tasks and availability.")

col1, col2 = st.columns(2)
with col1:
    availability_input = st.text_input("Availability (e.g., 8am-5pm)", value="8am-8pm")
with col2:
    if st.button("Set availability"):
        owner.set_availability([availability_input])
        st.success(f"✅ Availability set to: {availability_input}")

if st.button("Generate schedule", use_container_width=True, type="primary"):
    if not owner.pets or not owner.tasks:
        st.error("❌ Please add a pet and at least one task before generating a schedule.")
    else:
        try:
            # Generate the schedule using the Scheduler
            schedule = owner.generate_plan()

            st.success("✅ Schedule generated successfully!")
            
            # Separate conflicts by type
            exact_conflicts = [w for w in schedule.warnings if "Exact-start conflict" in w]
            no_slot_conflicts = [w for w in schedule.warnings if "no non-conflicting slot" in w]
            
            # Show prominent alert if there are conflicts
            if schedule.unmet_tasks or exact_conflicts or no_slot_conflicts:
                st.warning(f"⚠️ **Schedule has {len(schedule.unmet_tasks)} unmet task(s)**")
                
                # Show conflict breakdown
                col1, col2 = st.columns(2)
                with col1:
                    if exact_conflicts:
                        st.error(f"🚨 **Exact Time Conflicts:** {len(exact_conflicts)}")
                        st.caption("Tasks scheduled at the exact same time for the same pet")
                with col2:
                    if no_slot_conflicts:
                        st.warning(f"📅 **No Available Slot:** {len(no_slot_conflicts)}")
                        st.caption("Schedule is too full to fit these tasks")
                
                # Offer suggestions
                with st.expander("💡 How to fix conflicts", expanded=True):
                    st.markdown("""
                    **Try these solutions:**
                    - **Extend availability** — Set a wider time window (e.g., 7am-9pm instead of 8am-8pm)
                    - **Adjust task duration** — Shorten tasks that don't require full time
                    - **Reschedule tasks** — Move some tasks to a different preferred time
                    - **Add more time slots** — Space out daily recurring tasks
                    - **Review priorities** — Some tasks may be optional or combined
                    """)
            
            with st.expander(f"📅 Schedule for {schedule.date}", expanded=True):
                # Display metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Scheduled Tasks", len(schedule.scheduled_slots))
                with col2:
                    st.metric("Total Duration", f"{schedule.total_duration} min")
                with col3:
                    st.metric("Unmet Tasks", len(schedule.unmet_tasks))
                
                st.divider()

                if schedule.scheduled_slots:
                    st.subheader("📌 Daily Schedule")
                    for i, slot in enumerate(schedule.get_slots(), 1):
                        with st.container(border=True):
                            col1, col2, col3 = st.columns([2, 2, 1])
                            with col1:
                                st.write(f"**{i}. {slot.task.description}**")
                                st.caption(f"Pet: {slot.task.pet.name if slot.task.pet else 'Unassigned'}")
                            with col2:
                                st.caption(f"⏱️ {slot.start_time.strftime('%I:%M %p')} - {slot.end_time.strftime('%I:%M %p')}")
                                st.caption(f"Duration: {slot.task.duration} min")
                            with col3:
                                if st.button("✅ Done", key=f"complete_{i}", use_container_width=True):
                                    slot.task.mark_complete(slot.end_time)
                                    st.rerun()
                            
                            # Display explanation from scheduler
                            if slot.explanation:
                                st.info(f"💡 {slot.explanation}")
                else:
                    st.info("No tasks scheduled.")

                if schedule.unmet_tasks:
                    st.divider()
                    with st.expander(f"⚠️ Unmet Tasks ({len(schedule.unmet_tasks)})", expanded=True):
                        for task in schedule.unmet_tasks:
                            # Find related warning
                            related_warning = None
                            for w in schedule.warnings:
                                if task.description in w:
                                    related_warning = w
                                    break
                            
                            with st.container(border=True):
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.write(f"• **{task.description}**")
                                    st.caption(f"Pet: {task.pet.name if task.pet else 'Unassigned'} | Duration: {task.duration} min")
                                    if related_warning:
                                        st.caption(f"⚠️ {related_warning.split(':', 1)[1].strip() if ':' in related_warning else related_warning}")

                                    # Suggest the next available slot for this unmet task
                                    try:
                                        scheduler_local = Scheduler(owner=owner)
                                        scheduler_local.scheduled_plan = schedule
                                        earliest_dt = task.time if task.time else datetime.now()
                                        suggestion = scheduler_local.next_available_slot(
                                            duration_minutes=task.duration,
                                            earliest=earliest_dt,
                                            pet_name=task.pet.name if task.pet else None,
                                            search_days=7,
                                        )
                                        if suggestion:
                                            s_start, s_end = suggestion
                                            st.caption(f"Next available: {s_start.strftime('%Y-%m-%d %I:%M %p')} - {s_end.strftime('%I:%M %p')}")
                                            # Ensure a unique button key; fall back to description+start when id is empty
                                            try:
                                                safe_id = task.id if task.id else task.description.replace(" ", "_")
                                            except Exception:
                                                safe_id = "task"
                                            button_key = f"schedule_suggest_{safe_id}_{s_start.strftime('%Y%m%d%H%M')}"
                                            if st.button("Schedule here", key=button_key, use_container_width=True):
                                                # Prevent overlapping schedule entries
                                                conflict = scheduler_local._has_conflict(s_start, s_end, schedule, task=task)
                                                if conflict:
                                                    # Find a conflicting slot to report
                                                    conflicting_slot = None
                                                    for slot in schedule.scheduled_slots:
                                                        if not (slot.end_time <= s_start or slot.start_time >= s_end):
                                                            if not task.pet or (slot.task.pet and slot.task.pet.name == task.pet.name):
                                                                conflicting_slot = slot
                                                                break
                                                    if conflicting_slot:
                                                        st.error(f"Cannot schedule: overlaps with '{conflicting_slot.task.description}' ({conflicting_slot.start_time.strftime('%I:%M %p')} - {conflicting_slot.end_time.strftime('%I:%M %p')}).")
                                                    else:
                                                        st.error("Cannot schedule: selected slot overlaps an existing task.")
                                                else:
                                                    task.schedule(s_start, s_end)
                                                    schedule.add_scheduled_task_entry(task, s_start, s_end)
                                                    if task in schedule.unmet_tasks:
                                                        schedule.unmet_tasks.remove(task)
                                                    st.success("Scheduled suggested slot")
                                                    st.experimental_rerun()
                                        else:
                                            st.caption("No available slot found in next 7 days")
                                    except Exception:
                                        st.caption("Could not compute next available slot")
                                with col2:
                                    st.caption(task.frequency or "one-time")
                
                if schedule.warnings:
                    st.divider()
                    with st.expander(f"📋 All Schedule Notes ({len(schedule.warnings)})", expanded=False):
                        for warning in schedule.warnings:
                            st.caption(f"• {warning}")

        except Exception as e:
            st.error(f"Error generating schedule: {str(e)}")
