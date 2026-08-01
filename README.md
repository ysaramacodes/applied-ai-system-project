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


EXAMPLE 1: Simple Single Pet ✅
Owner:    Sarah (sarah@example.com)
Pet:      Biscuit (Golden Retriever, 4 years old, Female)
Availability: 8am - 8pm (12 hours)

Tasks:
  1. Morning walk    → 30 min, daily, CRITICAL
  2. Feeding         → 10 min, daily, CRITICAL
  3. Afternoon play  → 30 min, daily, HIGH
  4. Evening walk    → 20 min, daily, CRITICAL

Output (Both Runs Identical ✅)

📌 SCHEDULE FOR 2026-08-01:

1. MORNING WALK
   ⏰ 08:00 AM - 08:30 AM (30 min)
   🐾 Biscuit | Priority: CRITICAL | Confidence: 100%

2. FEEDING
   ⏰ 10:45 AM - 10:55 AM (10 min)
   🐾 Biscuit | Priority: CRITICAL | Confidence: 100%

3. EVENING WALK
   ⏰ 1:45 PM - 2:05 PM (20 min)
   🐾 Biscuit | Priority: CRITICAL | Confidence: 100%

4. AFTERNOON PLAY
   ⏰ 4:45 PM - 5:15 PM (30 min)
   🐾 Biscuit | Priority: HIGH | Confidence: 100%

📊 Summary:
   ✅ Tasks scheduled: 4/4 (100%)
   ⏱️ Total duration: 90 minutes
   📈 Utilization: 12.5% of available time
   ❌ Unmet tasks: 0



2nd Example

Input

Owner:    Alex (alex@example.com)
Availability: 8am - 8pm (12 hours)

🐾 Pet 1: Max (Labrador, 3 years old, Male)
   • Morning walk      → 30 min, daily, CRITICAL
   • Feeding           → 10 min, daily, CRITICAL
   • Evening walk      → 25 min, daily, CRITICAL
   • Play fetch        → 20 min, daily, HIGH

🐱 Pet 2: Luna (Siamese Cat, 5 years old, Female)
   • Feeding           → 5 min, daily, CRITICAL
   • Litter box clean  → 10 min, daily, HIGH
   • Playtime          → 15 min, daily, MEDIUM

Output (Both Runs Identical ✅)

📅 SCHEDULE FOR 2026-08-01 (7 tasks, 115 min total):

1. MORNING WALK
   ⏰ 08:00 AM - 08:30 AM (30 min)
   🐾 Max | Priority: CRITICAL | Confidence: 100%

2. FEEDING
   ⏰ 08:00 AM - 08:05 AM (5 min)
   🐱 Luna | Priority: CRITICAL | Confidence: 100%

3. FEEDING
   ⏰ 10:45 AM - 10:55 AM (10 min)
   🐾 Max | Priority: CRITICAL | Confidence: 100%

4. LITTER BOX CLEANING
   ⏰ 11:45 AM - 11:55 AM (10 min)
   🐱 Luna | Priority: HIGH | Confidence: 100%

5. EVENING WALK
   ⏰ 1:45 PM - 2:10 PM (25 min)
   🐾 Max | Priority: CRITICAL | Confidence: 100%

6. PLAYTIME
   ⏰ 3:45 PM - 4:00 PM (15 min)
   🐱 Luna | Priority: MEDIUM | Confidence: 100%

7. PLAY FETCH
   ⏰ 4:45 PM - 5:05 PM (20 min)
   🐾 Max | Priority: HIGH | Confidence: 100%


















#

I built this system this way beacuse I feel like it's as realistic as the app can be like I have a section added incase if the user forgot to mention if their pet has a health issue or they forgot to add a task so it is simple for the user to naviagate the app. The tradeoffs in this system is that it can't model resource limits like only one bath at a time and it also ignores task specific timing prefereneces.





# 
            46 passed in 0.02s 

After adding and creating more tests my system passed all tests especially all 13 reliability tests so I know I have full trust that my system is reliable. 
