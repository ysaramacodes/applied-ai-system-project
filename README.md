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

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
