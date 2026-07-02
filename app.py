import streamlit as st
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
    st.write(f"**{owner_name}'s Pets ({len(owner.pets)}):**")
    for p in owner.pets:
        st.write(f"- {p.name} ({p.breed}, {p.age} years old, {p.sex})")
else:
    st.info("No pets added yet.")

st.divider()

st.markdown("### Tasks")
st.caption("Add care tasks to your pet.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task description", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    frequency = st.selectbox("Frequency", ["one-time", "daily", "weekly", "monthly"])

if st.button("Create and assign task"):
    if not owner.pets:
        st.error("❌ Please add a pet first before creating tasks.")
    else:
        # Get or create task from vault
        task = get_or_create_task(st.session_state, task_title, duration=int(duration), frequency=frequency)

        # Assign task to the first pet (or you could let user select which pet)
        selected_pet = owner.pets[0]  # Default to first pet

        if task not in selected_pet.tasks:
            owner.create_task(selected_pet, task)
            st.success(f"✅ Task '{task_title}' assigned to {selected_pet.name}!")
        else:
            st.info(f"Task '{task_title}' is already assigned to {selected_pet.name}.")

# Display tasks for all pets
if owner.tasks:
    st.write(f"**All Tasks for {owner_name}:**")
    for pet in owner.pets:
        if pet.tasks:
            st.write(f"*{pet.name}'s tasks:*")
            task_data = []
            for task in pet.tasks:
                task_data.append({
                    "Description": task.description,
                    "Duration (min)": task.duration,
                    "Frequency": task.frequency or "one-time",
                    "Status": "✅ Complete" if task.completion_status else "⏳ Pending"
                })
            st.table(task_data)
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

if st.button("Generate schedule"):
    if not owner.pets or not owner.tasks:
        st.error("❌ Please add a pet and at least one task before generating a schedule.")
    else:
        try:
            # Generate the schedule using the Scheduler
            schedule = owner.generate_plan()

            st.success("✅ Schedule generated successfully!")
            st.write(f"**Schedule for {schedule.date}**")

            if schedule.scheduled_slots:
                st.write(f"Total duration: {schedule.total_duration} minutes")
                st.divider()

                for i, slot in enumerate(schedule.get_slots(), 1):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{i}. {slot.task.description}**")
                        st.caption(f"Pet: {slot.task.pet.name if slot.task.pet else 'Unassigned'} | Duration: {slot.task.duration} min")
                        st.caption(f"Time: {slot.start_time.strftime('%I:%M %p')} - {slot.end_time.strftime('%I:%M %p')}")
                    with col2:
                        if st.button("✅", key=f"complete_{i}"):
                            slot.task.mark_complete(slot.end_time)
                            st.rerun()
            else:
                st.info("No tasks scheduled.")

            if schedule.unmet_tasks:
                st.warning(f"⚠️ {len(schedule.unmet_tasks)} task(s) could not be scheduled")
                for task in schedule.unmet_tasks:
                    st.write(f"- {task.description}")

        except Exception as e:
            st.error(f"Error generating schedule: {str(e)}")
