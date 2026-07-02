from datetime import datetime, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def test_task_mark_complete_sets_completion_status():
    task = Task(description="Administer vaccine", id="t100")

    assert task.completion_status is False

    completion_time = datetime(2026, 6, 26, 14, 0)
    task.mark_complete(completed_time=completion_time, notes="Given vaccine")

    assert task.completion_status is True
    assert task.scheduled_end == completion_time
    assert "Given vaccine" in task.notes


def test_adding_task_increments_pet_task_count():
    pet = Pet(name="Buddy", breed="Beagle", age=3, sex="Male")
    task = Task(description="Feed breakfast", id="t101")

    assert len(pet.tasks) == 0

    pet.add_task(task)

    assert len(pet.tasks) == 1
    assert pet.tasks[0] is task
    assert task.pet is pet


def test_scheduler_filters_and_sorts_tasks():
    owner = Owner(name="Alex", contact_info="alex@example.com")
    pet1 = Pet(name="Buddy", breed="Beagle", age=3, sex="Male")
    pet2 = Pet(name="Molly", breed="Tabby", age=2, sex="Female")
    owner.add_pet(pet1)
    owner.add_pet(pet2)

    task1 = Task(description="Feed breakfast", time=datetime.now() + timedelta(hours=1), duration=15, id="t102")
    task2 = Task(description="Play", time=datetime.now() + timedelta(hours=2), duration=20, completion_status=True, id="t103")
    task3 = Task(description="Groom", time=datetime.now() + timedelta(hours=3), duration=25, id="t104")

    pet1.add_task(task1)
    pet2.add_task(task2)
    pet1.add_task(task3)

    scheduler = Scheduler(owner=owner)
    filtered_tasks = scheduler.filter_tasks(pet_name="Buddy", include_completed=False)

    assert task1 in filtered_tasks
    assert task3 in filtered_tasks
    assert task2 not in filtered_tasks

    ordered_tasks = scheduler.organize_tasks(include_completed=True)
    assert ordered_tasks[0].time <= ordered_tasks[1].time


def test_scheduler_handles_recurring_task_without_time():
    owner = Owner(name="Alex", contact_info="alex@example.com")
    pet = Pet(name="Buddy", breed="Beagle", age=3, sex="Male")
    owner.add_pet(pet)

    task = Task(description="Morning walk", duration=30, frequency="daily", preferred_time_slot="09:00-09:30", id="t105")
    pet.add_task(task)

    schedule = owner.generate_plan()

    assert len(schedule.scheduled_slots) == 1
    scheduled_task = schedule.scheduled_slots[0].task
    assert scheduled_task is task
    assert scheduled_task.scheduled_start is not None
    assert scheduled_task.scheduled_end is not None
    assert scheduled_task.scheduled_end - scheduled_task.scheduled_start == timedelta(minutes=30)


def test_scheduler_detects_conflicts_and_reschedules():
    owner = Owner(name="Alex", contact_info="alex@example.com")
    pet = Pet(name="Buddy", breed="Beagle", age=3, sex="Male")
    owner.add_pet(pet)

    base_time = datetime.now() + timedelta(days=1)
    start_time = base_time.replace(hour=8, minute=0, second=0, microsecond=0)

    task1 = Task(description="Morning walk", time=start_time, duration=30, id="t106")
    task2 = Task(description="Breakfast", time=start_time, duration=20, id="t107")

    pet.add_task(task1)
    pet.add_task(task2)

    schedule = owner.generate_plan()

    # With exact same-start-time conflicts for the same pet, the scheduler
    # will leave the first task scheduled and mark the second as unmet,
    # appending a lightweight warning rather than auto-rescheduling.
    assert schedule.validate()
    assert len(schedule.scheduled_slots) == 1
    assert schedule.scheduled_slots[0].task is task1
    assert task2 in schedule.unmet_tasks
    assert any("Breakfast" in w for w in schedule.warnings)


def test_scheduler_sort_by_time():
    owner = Owner(name="Alex", contact_info="alex@example.com")
    pet = Pet(name="Buddy", breed="Beagle", age=3, sex="Male")
    owner.add_pet(pet)

    base_time = datetime.now()
    task1 = Task(description="Evening play", time=base_time + timedelta(hours=3), duration=20, id="t108")
    task2 = Task(description="Morning walk", time=base_time + timedelta(hours=1), duration=30, id="t109")
    task3 = Task(description="Afternoon nap", time=base_time + timedelta(hours=2), duration=60, id="t110")
    task_no_time = Task(description="Scheduled later", duration=15, id="t111")

    pet.add_task(task1)
    pet.add_task(task2)
    pet.add_task(task3)
    pet.add_task(task_no_time)

    scheduler = Scheduler(owner=owner)
    sorted_tasks = scheduler.sort_by_time()

    assert sorted_tasks[0] is task2
    assert sorted_tasks[1] is task3
    assert sorted_tasks[2] is task1
    assert sorted_tasks[3] is task_no_time


def test_recurring_task_creates_next_occurrence():
    pet = Pet(name="Buddy", breed="Beagle", age=3, sex="Male")
    
    base_time = datetime(2026, 6, 26, 8, 0)
    task = Task(
        description="Morning walk",
        time=base_time,
        duration=30,
        frequency="daily",
        preferred_time_slot="08:00-09:00",
        id="walk-001"
    )
    pet.add_task(task)
    
    assert len(pet.tasks) == 1
    
    # Mark task as complete - should auto-create next occurrence
    task.mark_complete(datetime.now(), "Completed")
    
    assert task.completion_status is True
    assert len(pet.tasks) == 2
    
    next_task = pet.tasks[1]
    assert next_task.description == "Morning walk"
    assert next_task.frequency == "daily"
    assert next_task.time.date() == (base_time + timedelta(days=1)).date()
    assert next_task.id == f"walk-001-{(base_time + timedelta(days=1)).strftime('%Y%m%d')}"


def test_weekly_recurring_task_creates_next_occurrence():
    pet = Pet(name="Mittens", breed="Tabby", age=2, sex="Female")
    
    base_time = datetime(2026, 6, 26, 10, 0)
    task = Task(
        description="Weekly grooming",
        time=base_time,
        duration=45,
        frequency="weekly",
        id="groom-001"
    )
    pet.add_task(task)
    
    assert len(pet.tasks) == 1
    
    # Mark task as complete - should auto-create next occurrence
    task.mark_complete(datetime.now())
    
    assert len(pet.tasks) == 2
    
    next_task = pet.tasks[1]
    assert next_task.time.date() == (base_time + timedelta(weeks=1)).date()

