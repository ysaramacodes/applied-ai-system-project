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

            # Multi-step reasoning with visible planning chain
            with st.expander("🧠 AI Planning & Reasoning", expanded=True):
                reasoning_steps = []

                # STEP 1: Analyze Requirements
                st.write("**Step 1: Analyze Requirements** 🔍")
                col1, col2, col3, col4 = st.columns(4)
                analysis = agent.analyze_scheduling_needs()
                with col1:
                    st.metric("Pets", analysis["total_pets"])
                with col2:
                    st.metric("Tasks", analysis["total_tasks"])
                with col3:
                    st.metric("Available Hours", f"{analysis['available_hours']:.1f}h")
                with col4:
                    total_required = sum(t.duration for t in owner.tasks)
                    st.metric("Total Required (min)", total_required)
                reasoning_steps.append(f"Analyzed {analysis['total_pets']} pet(s) with {analysis['total_tasks']} task(s) requiring {total_required} minutes across {analysis['available_hours']:.1f} available hours")

                # STEP 2: Check Health Constraints
                st.write("**Step 2: Assess Health Constraints** 🏥")
                health_risks = []
                if analysis["pet_health_considerations"]:
                    for pet_name, health_info in analysis["pet_health_considerations"].items():
                        conditions = health_info.get('conditions', [])
                        if conditions:
                            st.caption(f"🐾 **{pet_name}**: {', '.join(conditions)}")
                            health_risks.append(f"{pet_name} has health considerations")
                if health_risks:
                    reasoning_steps.append(f"Identified health constraints: {'; '.join(health_risks)}")
                else:
                    st.caption("✓ No health constraints detected")
                    reasoning_steps.append("No health constraints detected")

                # STEP 3: Plan Schedule Distribution
                st.write("**Step 3: Plan Task Distribution** 📊")
                recurring_count = sum(1 for t in owner.tasks if t.frequency != "one-time")
                onetime_count = sum(1 for t in owner.tasks if t.frequency == "one-time")
                col1, col2 = st.columns(2)
                with col1:
                    st.caption(f"📅 Recurring: {recurring_count} tasks")
                with col2:
                    st.caption(f"⏳ One-time: {onetime_count} tasks")

                if recurring_count > 0:
                    st.caption("Strategy: Distribute recurring tasks evenly throughout day to prevent clustering")
                    reasoning_steps.append(f"Distributing {recurring_count} recurring tasks across available hours")
                if onetime_count > 0:
                    st.caption(f"Strategy: Find optimal slots for {onetime_count} one-time task(s)")
                    reasoning_steps.append(f"Scheduling {onetime_count} one-time task(s) in optimal time slots")

                # STEP 4: Generate Schedule
                st.write("**Step 4: Generate Schedule** ⚙️")
                with st.spinner("Scheduling tasks..."):
                    schedule = agent.generate_intelligent_schedule()
                    st.session_state.last_schedule = schedule

                scheduled_count = len(schedule.scheduled_slots)
                unmet_count = len(schedule.unmet_tasks)
                success_rate = (scheduled_count / (scheduled_count + unmet_count) * 100) if (scheduled_count + unmet_count) > 0 else 0
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Scheduled", scheduled_count)
                with col2:
                    st.metric("Unmet", unmet_count)
                with col3:
                    st.metric("Success Rate", f"{success_rate:.0f}%")
                reasoning_steps.append(f"Scheduled {scheduled_count}/{scheduled_count + unmet_count} tasks ({success_rate:.0f}% success rate)")

                # STEP 5: Resolve Conflicts
                if unmet_tasks := schedule.unmet_tasks:
                    st.write("**Step 5: Conflict Resolution** 🔄")
                    st.caption(f"⚠️ {len(unmet_tasks)} task(s) couldn't fit in primary schedule")
                    conflict_reasons = []
                    for warning in schedule.warnings:
                        if "no non-conflicting slot" in warning.lower():
                            conflict_reasons.append("Schedule too full")
                        elif "conflict" in warning.lower():
                            conflict_reasons.append("Time conflicts detected")
                    if conflict_reasons:
                        st.caption(f"Reasons: {', '.join(set(conflict_reasons))}")
                    reasoning_steps.append(f"Identified {len(unmet_tasks)} unmet tasks requiring rescheduling or adaptation")
                else:
                    st.write("**Step 5: Conflict Resolution** 🔄")
                    st.success("✓ No conflicts detected - all tasks scheduled successfully!")
                    reasoning_steps.append("All tasks scheduled without conflicts")

                # Summary of reasoning
                st.divider()
                with st.expander("📝 Reasoning Chain Summary", expanded=False):
                    for i, step in enumerate(reasoning_steps, 1):
                        st.caption(f"{i}. {step}")

            # Check for tasks that require vet review with decision chain
            with st.expander("🏥 Safety Check: Vet Review Required?", expanded=True):
                st.write("**Decision Chain: Medical Safety Analysis** 🔗")

                tasks_needing_vet_review = []
                vet_review_reasoning = []

                for slot in schedule.scheduled_slots:
                    task_desc = slot.task.description.lower()
                    pet = slot.task.pet

                    is_medication = 'medication' in task_desc or 'med' in task_desc
                    has_health_condition = pet and pet.health_conditions
                    is_senior = pet and pet.age >= 10

                    activity_keywords = ['walk', 'play', 'exercise', 'run', 'fetch', 'activity', 'therapy', 'grooming', 'groom']
                    is_activity = any(word in task_desc for word in activity_keywords)

                    # Decision logic with reasoning
                    flags = []
                    if is_medication:
                        flags.append("is_medication:true")
                    if is_activity and (is_senior or has_health_condition):
                        flags.append("is_activity:true → senior/health")
                    if is_senior and has_health_condition:
                        flags.append("senior:true AND health:true")

                    if flags:
                        tasks_needing_vet_review.append(slot)
                        decision_logic = f"{slot.task.description} ({pet.name if pet else 'Unassigned'}): [{' OR '.join(flags)}] → ✓ REQUIRES REVIEW"
                        vet_review_reasoning.append(decision_logic)

                if tasks_needing_vet_review:
                    st.warning(f"⚠️ Found {len(tasks_needing_vet_review)} task(s) requiring veterinary review")
                    with st.expander("Decision Logic Details", expanded=False):
                        for reasoning in vet_review_reasoning:
                            st.caption(f"→ {reasoning}")

                    st.write("**Tasks Requiring Vet Review:**")
                    for slot in tasks_needing_vet_review:
                        reason = []
                        if 'medication' in slot.task.description.lower():
                            reason.append("📋 medication timing")
                        if slot.task.pet and slot.task.pet.health_conditions:
                            reason.append("🏥 health condition")
                        if slot.task.pet and slot.task.pet.age >= 10:
                            reason.append("👴 senior pet")

                        st.caption(f"• **{slot.task.description}** ({', '.join(reason)})")
                    st.info("💡 Review these carefully with your veterinarian before approving the schedule.")
                else:
                    st.success("✓ No medical safety concerns detected - all tasks approved for scheduling")

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

                            # Display scheduling decision chain for each slot
                            with st.expander("📊 Scheduling Decision", expanded=False):
                                st.caption("**How this task was scheduled:**")
                                decision_steps = [
                                    f"✓ Task: {slot.task.description} ({slot.task.duration} min)",
                                    f"✓ Pet: {slot.task.pet.name if slot.task.pet else 'Unassigned'} (age: {slot.task.pet.age if slot.task.pet else '?'} years)",
                                    f"✓ Frequency: {slot.task.frequency or 'one-time'}",
                                    f"✓ Priority: {slot.task.priority}",
                                    f"✓ Slot Time: {slot.start_time.strftime('%I:%M %p')} (non-conflicting)",
                                    f"✓ Confidence Score: {slot.confidence:.0%}" if hasattr(slot, 'confidence') else "✓ Slot verified",
                                ]
                                for step in decision_steps:
                                    st.caption(step)

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

                                # Show why this task couldn't be scheduled
                                with st.expander("📊 Why unscheduled?", expanded=False):
                                    st.caption("**Scheduling Decision Chain:**")
                                    st.caption(f"❌ Could not find non-conflicting slot for {task.duration} min task")
                                    st.caption(f"Reason: {related_warning if related_warning else 'Schedule too full or availability constraints'}")
                                    st.caption("**Possible solutions:**")
                                    st.caption("• Extend availability window (add more hours)")
                                    st.caption("• Reduce duration of other tasks")
                                    st.caption("• Change task frequency or schedule to different day")
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

            # Show adaptation reasoning chain
            with st.expander("🔄 Adaptation Planning", expanded=True):
                st.write("**Change Analysis & Adaptation Steps** 🔗")

                # Step 1: Validate change
                st.write("**Step 1: Validate Change Request**")
                col1, col2 = st.columns(2)
                with col1:
                    st.caption(f"Adaptation Type: {adapt_type}")
                with col2:
                    st.caption(f"Status: ✓ Valid")

                # Step 2: Identify Impact
                st.write("**Step 2: Analyze Impact**")
                impact_analysis = []
                if "new_availability" in changes:
                    impact_analysis.append(f"📍 Availability changed to: {changes['new_availability'][0]}")
                    impact_analysis.append("🔄 May affect all task placements")
                if "pet_health_update" in changes:
                    pet_name = changes['pet_health_update']['pet_name']
                    condition = changes['pet_health_update']['condition']
                    impact_analysis.append(f"🏥 {pet_name} health update: {condition}")
                    impact_analysis.append("⚠️ May require vet review of affected tasks")
                if "task_time_update" in changes:
                    task_desc = changes['task_time_update']['description']
                    impact_analysis.append(f"🕐 {task_desc} time/duration modified")
                    impact_analysis.append("🔄 May cascade into other task rescheduling")
                if "new_task" in changes:
                    new_task = changes['new_task']
                    impact_analysis.append(f"➕ New task: {new_task['description']} ({new_task['duration']} min)")
                    impact_analysis.append(f"🐾 Assigned to: {new_task['pet'].name}")

                for impact in impact_analysis:
                    st.caption(impact)

                # Step 3: Apply changes
                st.write("**Step 3: Apply Changes & Regenerate**")
                with st.spinner("Regenerating schedule with new parameters..."):
                    adaptation_summary = agent.adapt_to_changes(changes)
                    st.session_state.last_schedule = agent.current_plan
                    st.success("✓ Changes applied successfully")

                st.divider()
                st.write("**Adaptation Summary:**")
                st.write(adaptation_summary)

            st.success("✅ Adaptive schedule updated")
            st.session_state.show_updated_schedule = True
