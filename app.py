import streamlit as st
import pandas as pd
from datetime import datetime
from pawpal_system import Pet, Task, Owner, Schedule, Scheduler, get_or_create_owner, get_or_create_pet, get_or_create_task
from agent import CareAgent

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

# Initialize adaptive care agent in session state
if "care_agent" not in st.session_state:
    st.session_state.care_agent = CareAgent(owner=owner, scheduler=Scheduler(owner=owner))
else:
    st.session_state.care_agent.owner = owner
    st.session_state.care_agent.scheduler.owner = owner
    st.session_state.care_agent.scheduler.availability = owner.availability

# Initialize adaptive schedule state
if "show_updated_schedule" not in st.session_state:
    st.session_state.show_updated_schedule = False
if "last_schedule" not in st.session_state:
    st.session_state.last_schedule = None

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

# Display updated schedule from adaptive scheduling at the top
if st.session_state.show_updated_schedule or st.session_state.last_schedule:
    st.success("✅ Schedule updated! Here's your new plan:")
    st.balloons()

    agent = st.session_state.care_agent
    if st.session_state.last_schedule:
        schedule = st.session_state.last_schedule
    else:
        schedule = agent.generate_intelligent_schedule()
        st.session_state.last_schedule = schedule

    with st.expander(f"📅 Updated Schedule for {schedule.date}", expanded=True):
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
                        if st.button("✅ Done", key=f"complete_updated_{i}", use_container_width=True):
                            slot.task.mark_complete(slot.end_time)
                            st.rerun()

                    agent_explanation = agent.explain_decision(slot)
                    st.info(f"🤖 {agent_explanation}")
        else:
            st.info("No tasks scheduled.")

        if schedule.unmet_tasks:
            st.divider()
            with st.expander(f"⚠️ Unmet Tasks ({len(schedule.unmet_tasks)})", expanded=False):
                for task in schedule.unmet_tasks:
                    with st.container(border=True):
                        st.write(f"• **{task.description}**")
                        st.caption(f"Pet: {task.pet.name if task.pet else 'Unassigned'} | Duration: {task.duration} min")

    st.divider()
    st.session_state.show_updated_schedule = False

st.markdown("### Tasks")
st.caption("Add care tasks to your pet.")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    task_title = st.text_input("Task description", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    frequency = st.selectbox("Frequency", ["one-time", "daily", "weekly", "monthly"])
with col4:
    # FIX 1: Task priority selector
    task_priority = st.selectbox("Priority", ["critical", "high", "medium", "low"], index=2, help="Critical: must schedule | High: prioritize | Medium: normal | Low: optional")
with col5:
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

        # FIX 1: Set task priority
        task.priority = task_priority

        # Assign task to the selected pet
        selected_pet = next((p for p in owner.pets if p.name == selected_pet_name), owner.pets[0])

        if task not in selected_pet.tasks:
            owner.create_task(selected_pet, task)
            st.success(f"✅ Task '{task_title}' assigned to {selected_pet.name}! (Priority: {task_priority})")
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
    if "availability_input" not in st.session_state:
        st.session_state.availability_input = "8am-8pm"
    availability_input = st.text_input("Availability (e.g., 8am-5pm)", value=st.session_state.availability_input, key="availability_widget")
with col2:
    if st.button("Set availability"):
        st.session_state.availability_input = st.session_state.availability_widget
        # Split by comma to support multiple windows (e.g., "6am-9am, 6pm-9pm")
        availability_windows = [w.strip() for w in st.session_state.availability_widget.split(",")]
        owner.set_availability(availability_windows)
        st.session_state.care_agent.scheduler.availability = availability_windows
        st.session_state.show_updated_schedule = True
        st.success(f"✅ Availability set to: {st.session_state.availability_widget}")

if st.button("Generate schedule with AI", use_container_width=True, type="primary", key="generate_with_ai_btn"):
    st.session_state.show_updated_schedule = True
    if not owner.pets or not owner.tasks:
        st.error("❌ Please add a pet and at least one task before generating a schedule.")
    else:
        try:
            agent = st.session_state.care_agent
            agent.owner = owner
            agent.scheduler.owner = owner
            agent.scheduler.availability = owner.availability
            schedule = agent.generate_intelligent_schedule()
            st.session_state.last_schedule = schedule

            # FIX 2: Automation bias warning - check for low confidence scores
            low_confidence_tasks = [slot for slot in schedule.scheduled_slots if slot.confidence and slot.confidence.score < 0.7]
            if low_confidence_tasks:
                st.warning("⚠️ **Low Confidence Tasks Detected**")
                st.write(f"Found {len(low_confidence_tasks)} task(s) with confidence <70%:")
                for slot in low_confidence_tasks:
                    st.caption(f"• {slot.task.description}: {slot.confidence.score:.0%} - {slot.confidence.reasoning}")
                st.info("💡 Review these carefully before approving the schedule.")

            st.success("✅ AI schedule generated successfully!")

            analysis = agent.analyze_scheduling_needs()
            with st.expander("🤖 AI Agent Analysis", expanded=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Pets", analysis["total_pets"])
                with col2:
                    st.metric("Total Tasks", analysis["total_tasks"])
                with col3:
                    st.metric("Available Hours", f"{analysis['available_hours']:.1f}h")

                if analysis["pet_health_considerations"]:
                    st.warning("🏥 Health Considerations:")
                    for pet_name, health_info in analysis["pet_health_considerations"].items():
                        st.caption(f"**{pet_name}**: {', '.join(health_info['conditions'] or ['No conditions recorded'])}")

            exact_conflicts = [w for w in schedule.warnings if "Exact-start conflict" in w]
            no_slot_conflicts = [w for w in schedule.warnings if "no non-conflicting slot" in w]
            if schedule.unmet_tasks or exact_conflicts or no_slot_conflicts:
                st.warning(f"⚠️ **Schedule has {len(schedule.unmet_tasks)} unmet task(s)**")
                col1, col2 = st.columns(2)
                with col1:
                    if exact_conflicts:
                        st.error(f"🚨 **Exact Time Conflicts:** {len(exact_conflicts)}")
                        st.caption("Tasks scheduled at the exact same time for the same pet")
                with col2:
                    if no_slot_conflicts:
                        st.warning(f"📅 **No Available Slot:** {len(no_slot_conflicts)}")
                        st.caption("Schedule is too full to fit these tasks")
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
                            if slot.explanation:
                                st.info(f"💡 {slot.explanation}")
                else:
                    st.info("No tasks scheduled.")

                if schedule.unmet_tasks:
                    st.divider()
                    with st.expander(f"⚠️ Unmet Tasks ({len(schedule.unmet_tasks)})", expanded=True):
                        for task in schedule.unmet_tasks:
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
                                with col2:
                                    st.caption(task.frequency or "one-time")
                if schedule.warnings:
                    st.divider()
                    with st.expander(f"📋 All Schedule Notes ({len(schedule.warnings)})", expanded=False):
                        for warning in schedule.warnings:
                            st.caption(f"• {warning}")
        except Exception as e:
            st.error(f"Error generating schedule: {str(e)}")

st.divider()
st.subheader("Adapt Schedule")
st.caption("Apply AI adaptation after availability, pet health, task time updates, or missing tasks.")

adapt_type = st.selectbox(
    "Adaptation type",
    ["Availability change", "Pet health update", "Task time update", "Add missing task"],
)

new_availability_input = ""
selected_health_pet = None
health_condition = ""
selected_task_option = None
new_task_time = ""
new_task_duration = 20
new_task_description = ""
new_task_frequency = "one-time"
new_task_pet = None

if adapt_type == "Availability change":
    new_availability_input = st.text_input("Updated availability (e.g. 7am-7pm)", value="")

if adapt_type == "Pet health update":
    health_pet_names = [p.name for p in owner.pets] if owner.pets else []
    selected_health_pet = st.selectbox("Pet for health update", health_pet_names, index=0 if health_pet_names else None)
    health_condition = st.text_input("Health condition or note", value="")

if adapt_type == "Task time update":
    pending_tasks = [task for task in owner.tasks if not task.completion_status]
    task_options = [f"{task.description} ({task.pet.name if task.pet else 'Unassigned'})" for task in pending_tasks]
    if task_options:
        selected_task_option = st.selectbox("Task to update", task_options)
        new_task_time = st.text_input("New preferred time slot (e.g. 08:30-09:00)", value="")
        new_task_duration = st.number_input("New duration (minutes)", min_value=1, max_value=240, value=20)
    else:
        st.info("No pending tasks available for time update.")

if adapt_type == "Add missing task":
    new_task_description = st.text_input("Task description", value="")
    new_task_duration = st.number_input("Task duration (minutes)", min_value=1, max_value=240, value=20)
    new_task_frequency = st.selectbox("Task frequency", ["one-time", "daily", "weekly", "monthly"])
    pet_names = [p.name for p in owner.pets] if owner.pets else []
    if pet_names:
        new_task_pet = st.selectbox("Assign to pet", pet_names)
    else:
        st.info("Add a pet before adding a task.")

if st.button("Apply adaptive changes", key="adapt_schedule_btn"):
    changes = {}
    if adapt_type == "Availability change" and new_availability_input:
        changes["new_availability"] = [new_availability_input]
    if adapt_type == "Pet health update" and selected_health_pet and health_condition:
        changes["pet_health_update"] = {
            "pet_name": selected_health_pet,
            "condition": health_condition,
        }
    if adapt_type == "Task time update" and selected_task_option:
        task_description = selected_task_option.split(" (")[0]
        pet_name = selected_task_option.split("(")[-1].rstrip(")")
        changes["task_time_update"] = {
            "pet_name": pet_name,
            "description": task_description,
            "preferred_time_slot": new_task_time,
            "new_duration": int(new_task_duration),
        }
    if adapt_type == "Add missing task" and new_task_description and new_task_pet:
        pet_obj = next((p for p in owner.pets if p.name == new_task_pet), None)
        if pet_obj:
            changes["new_task"] = {
                "description": new_task_description,
                "duration": int(new_task_duration),
                "frequency": new_task_frequency,
                "pet": pet_obj,
            }

    if not changes:
        st.error("Please enter a valid adaptation option before applying changes.")
    else:
        if not st.session_state.last_schedule and adapt_type != "Add missing task":
            st.error("Please build a schedule first before applying adaptive changes.")
        else:
            agent = st.session_state.care_agent
            agent.owner = owner
            agent.scheduler.owner = owner
            agent.scheduler.availability = owner.availability
            if not agent.current_plan and st.session_state.last_schedule:
                agent.current_plan = st.session_state.last_schedule

            adaptation_summary = agent.adapt_to_changes(changes)
            st.success("✅ Adaptive schedule updated")
            st.write(adaptation_summary)
            st.session_state.last_schedule = agent.current_plan
            st.session_state.show_updated_schedule = True
