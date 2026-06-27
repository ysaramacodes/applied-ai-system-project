from datetime import datetime

from pawpal_system import Pet, Task


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

