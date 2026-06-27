"""PawPal+ app entrypoint."""

from datetime import datetime

from pawpal_system import Owner, Pet, Task


def main() -> None:
    owner = Owner(name="Alex", contact_info="alex@example.com")
    pet1 = Pet(name="Biscuit", breed="Golden Retriever", age=4, sex="Male")
    pet2 = Pet(name="Mittens", breed="Tabby", age=2, sex="Female")
    owner.add_pet(pet1)
    owner.add_pet(pet2)

    task1 = Task(
        description="Morning walk",
        duration=30,
        frequency="daily",
        preferred_time_slot="08:00-09:00",
        time=datetime(2026, 6, 26, 8, 0),
        id="task-001",
    )
    task2 = Task(
        description="Lunchtime feeding",
        duration=15,
        frequency="daily",
        preferred_time_slot="12:00-12:30",
        time=datetime(2026, 6, 26, 12, 0),
        id="task-002",
    )
    task3 = Task(
        description="Evening play",
        duration=20,
        frequency="daily",
        preferred_time_slot="18:00-18:30",
        time=datetime(2026, 6, 26, 18, 0),
        id="task-003",
    )
    owner.create_task(pet1, task1)
    owner.create_task(pet1, task2)
    owner.create_task(pet2, task3)

    schedule = owner.generate_plan()
    print(f"Owner: {owner.name}")
    print(f"Pets: {[pet.name for pet in owner.pets]}")
    print(f"Tasks: {len(owner.tasks)}")
    print()
    print("Today's Schedule")
    print("----------------")
    if schedule.scheduled_slots:
        for slot in schedule.scheduled_slots:
            start = slot.start_time.strftime("%H:%M")
            end = slot.end_time.strftime("%H:%M")
            pet_name = slot.task.pet.name if slot.task.pet else "Unknown Pet"
            print(f"{start} - {end}: {slot.task.description} ({pet_name})")
    else:
        print("No scheduled tasks yet.")

    if schedule.unmet_tasks:
        print()
        print("Unmet Tasks")
        print("-----------")
        for task in schedule.unmet_tasks:
            pet_name = task.pet.name if task.pet else "Unknown Pet"
            time_str = task.time.strftime("%H:%M") if task.time else "unscheduled"
            print(f"{time_str}: {task.description} ({pet_name})")


if __name__ == "__main__":
    main()
