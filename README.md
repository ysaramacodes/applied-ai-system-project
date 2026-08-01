# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output


Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```




Owner: Alex
Pets: ['Biscuit', 'Mittens']
Tasks: 3
Today's Schedule:
08:00 - 08:30: Morning walk (Biscuit)
12:00 - 12:15: Lunchtime feeding (Biscuit)
18:00 - 18:20: Evening play (Mittens)



## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:
 python3 -m pytest

 My tests covers task completion, task scheduling, recurring task scheduling, conflict detection, ordering, daily and weekly reccuring tasks.

```
# Paste your pytest output here
                                                                                                         [100%]

============================================================= 8 passed in 0.01s =============================================================


Syetem Reliability is 4 stars based on my tests.

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | Scheduler.sort_by_time(),Scheduler.organize_tasks(), Scheduler.schedule() | | 
| Filtering | | Scheduler.filter_tasks(), Scheduler.organize_tasks(), filter_tasks() | |
| Conflict handling | | Task.is_conflicting(), Scheduler._has_conflict(), Scheduler._find_non_conflicting_slot(),Scheduler.schedule()  |   |
| Recurring tasks | | Task.is_recurring(),Task._create_next_occurrence(), Task.mark_complete(), _create_next_occurrence(), Scheduler._get_next_recurring_time() , Scheduler.schedule()   e.g., daily vs. weekly |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. The user/pet Owner have to type their information and contact information.
2. The user than has to give their pets informtion like age/sex, name.
3. The pet owner than creates tasks for their pets like sleep, walk and if its recurring or a one time task.
4. The pet owner has to then set their availability so the app can make a schedule based on their timeslot.
5. After the user creates schedule they can view todays tasks.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->








#Project 4 README

The project I decided to expand was the PawPal+ app which was project 3. The original system is Streamlit app that helps pet owners plan daily care tasks for their pets. The app was able to create and manage pet care tasks. The apps goals were intelligently schedule pet care tasks based on constraints and priorities.

My expanded project does pretty much the same thing but it also accounts for changes like changes in health and the A.I system adapts and changes the schedule based on time constraint and change in the pet's health. The project matters because it automatically generates and organizes tasks into a plan that that is easy for the pet owner to follow.


My architecture diagram shows the 4 stages in the system. The first being user input like owner information and their pets. While the system detects if everythig is valid like task duration. The second part is mainly just the A.I analyzes and generates the schedule for the pet owner based off the users input in stage 1. The third stage is the rescheduling stage incase a task can not be added due to time constraints which the system reschedules it to a later day. The fourth stage is when the plan is fully made and is presented to the user to than follow.



# Steps to run my code 

1) # Create a virtual environment
python -m venv .venv

# Activate it
source .venv/bin/activate  # macOS/Linux
# OR on Windows:
.venv\Scripts\activate


2) # Install required packages
pip install -r requirements.txt


3) # Start the Streamlit app
streamlit run app.py


## EXAMPLE 1: Simple Single Pet ✅

### 📥 INPUT:
```
Owner: Jordan (available 8am-8pm)
Pet: Mochi (Golden Retriever, 3 years old, Female)

Tasks:
  • Morning walk — 30 min, daily, critical
  • Feeding — 10 min, daily, critical
  • Afternoon play — 30 min, daily, high
  • Evening walk — 20 min, daily, critical
```

### 📤 OUTPUT:

✅ **Schedule Generated for 2026-08-01**

**📊 Summary:** 4/4 tasks scheduled  
**⏱️ Total Duration:** 90 minutes  
**Status:** ✅ Optimal

**📌 Daily Schedule:**

| Task | Time | Pet | Duration | Priority |
|------|------|-----|----------|----------|
| 1. Morning walk | 08:00 AM - 08:30 AM | Mochi | 30 min | critical |
| 2. Feeding | 10:45 AM - 10:55 AM | Mochi | 10 min | critical |
| 3. Evening walk | 1:45 PM - 2:05 PM | Mochi | 20 min | critical |
| 4. Afternoon play | 4:45 PM - 5:15 PM | Mochi | 30 min | high |

**✅ All tasks successfully scheduled!**



2nd Example

## EXAMPLE 2: Senior Pet with Health Conditions ⚠️

### 📥 INPUT:
```
Owner: Sarah (available 7am-9pm)

🐕 Pet 1: Buddy (Labrador, 11 years old, Male) — arthritis
   • Morning walk — 20 min, daily, critical
   • Medication — 5 min, daily, critical
   • Feeding — 10 min, daily, critical
   • Afternoon rest — 30 min, daily, high

🐱 Pet 2: Luna (Siamese Cat, 4 years old, Female)
   • Feeding — 5 min, daily, critical
   • Playtime — 15 min, daily, medium
```

### 📤 OUTPUT:

✅ **Schedule Generated for 2026-08-01**

**📊 Summary:** 6/9 tasks scheduled (3 unmet)  
**⏱️ Total Duration:** 65 minutes  
**Status:** ⚠️ Review needed

---

### ⚠️ TASKS REQUIRING VET REVIEW:

| Task | Pet | Reason |
|------|-----|--------|
| Morning walk | Buddy | health condition, senior pet |
| Medication | Buddy | medication timing, health condition, senior pet |
| Feeding | Buddy | health condition, senior pet |
| Afternoon rest | Buddy | health condition, senior pet |

**⚠️ Important:** All Buddy's tasks need veterinary verification due to age and arthritis condition.

---

### 📌 Daily Schedule:

| Task | Time | Pet | Duration | Priority |
|------|------|-----|----------|----------|
| 1. Morning walk | 07:00 AM - 07:14 AM | 🐕 Buddy | 14 min | critical |
| 2. Feeding | 07:00 AM - 07:05 AM | 🐱 Luna | 5 min | critical |
| 3. Medication | 10:15 AM - 10:18 AM | 🐕 Buddy | 3 min | critical |
| 4. Feeding | 1:45 PM - 1:52 PM | 🐕 Buddy | 7 min | critical |
| 5. Playtime | 1:45 PM - 2:00 PM | 🐱 Luna | 15 min | medium |
| 6. Afternoon rest | 5:15 PM - 5:36 PM | 🐕 Buddy | 21 min | high |

**Note:** System automatically reduced Buddy's walk duration from 20 to 14 min and feeding from 10 to 7 min due to age (11 years) and arthritis condition. ✅

**Unmet Tasks (3):** Luna's playtime overlap resolved in rescheduling, all critical tasks fit within availability.


















#

I built this system this way beacuse I feel like it's as realistic as the app can be like I have a section added incase if the user forgot to mention if their pet has a health issue or they forgot to add a task so it is simple for the user to naviagate the app. The tradeoffs in this system is that it can't model resource limits like only one bath at a time and it also ignores task specific timing prefereneces.





# 
            46 passed in 0.02s 

After adding and creating more tests my system passed all tests especially all 13 reliability tests so I know I have full trust that my system is reliable and good for basic use. 
