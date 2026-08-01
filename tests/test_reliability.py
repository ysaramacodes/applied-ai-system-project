"""
Tests for ACTUAL system reliability (not just transparency).
Measures: task success rate, constraint compliance, edge case handling.
"""

from datetime import datetime, timedelta
import pytest

from pawpal_system import Owner, Pet, Scheduler, Task, Schedule


class TestSchedulingReliability:
    """Test that the scheduling system reliably produces valid schedules."""

    def test_no_task_conflicts_in_schedule(self):
        """Reliability: No two tasks for same pet should overlap."""
        owner = Owner(name="Alex", contact_info="alex@example.com")
        owner.set_availability(["08:00-20:00"])
        pet = Pet(name="Buddy", breed="dog", age=3, sex="Male")
        owner.add_pet(pet)

        tasks = [
            Task(description="Walk 1", duration=30, frequency="daily", id="t1"),
            Task(description="Walk 2", duration=30, frequency="daily", id="t2"),
            Task(description="Walk 3", duration=30, frequency="daily", id="t3"),
        ]
        for task in tasks:
            pet.add_task(task)

        schedule = owner.generate_plan()

        # Check NO overlaps for same pet
        for i, slot1 in enumerate(schedule.scheduled_slots):
            for slot2 in schedule.scheduled_slots[i+1:]:
                if slot1.task.pet and slot2.task.pet:
                    if slot1.task.pet.name == slot2.task.pet.name:
                        # Same pet: slots must not overlap
                        assert slot1.end_time <= slot2.start_time or slot1.start_time >= slot2.end_time, \
                            f"Tasks overlap: {slot1.task.description} and {slot2.task.description}"

    def test_all_scheduled_tasks_within_availability(self):
        """Reliability: All scheduled tasks must be within owner's availability."""
        owner = Owner(name="Alex", contact_info="alex@example.com")
        owner.set_availability(["09:00-17:00"])
        pet = Pet(name="Buddy", breed="dog", age=3, sex="Male")
        owner.add_pet(pet)

        tasks = [
            Task(description="Walk", duration=30, id="t1"),
            Task(description="Feed", duration=20, id="t2"),
            Task(description="Play", duration=30, id="t3"),
        ]
        for task in tasks:
            pet.add_task(task)

        schedule = owner.generate_plan()

        for slot in schedule.scheduled_slots:
            # Parse availability
            start_h, start_m = 9, 0
            end_h, end_m = 17, 0
            avail_start = slot.start_time.replace(hour=start_h, minute=start_m)
            avail_end = slot.start_time.replace(hour=end_h, minute=end_m)

            assert slot.start_time >= avail_start, \
                f"{slot.task.description} starts before availability"
            assert slot.end_time <= avail_end, \
                f"{slot.task.description} ends after availability"

    def test_scheduled_time_matches_task_duration(self):
        """Reliability: Slot duration must exactly match task duration."""
        owner = Owner(name="Alex", contact_info="alex@example.com")
        owner.set_availability(["08:00-20:00"])
        pet = Pet(name="Buddy", breed="dog", age=3, sex="Male")
        owner.add_pet(pet)

        task = Task(description="Walk", duration=25, id="t1")
        pet.add_task(task)

        schedule = owner.generate_plan()

        assert len(schedule.scheduled_slots) == 1
        slot = schedule.scheduled_slots[0]
        actual_duration = (slot.end_time - slot.start_time).total_seconds() / 60

        assert actual_duration == task.duration, \
            f"Slot duration {actual_duration} doesn't match task duration {task.duration}"

    def test_task_success_rate(self):
        """Reliability: Measure % of tasks that can be scheduled."""
        owner = Owner(name="Alex", contact_info="alex@example.com")
        owner.set_availability(["08:00-20:00"])
        pet = Pet(name="Buddy", breed="dog", age=3, sex="Male")
        owner.add_pet(pet)

        # Add realistic number of tasks
        tasks = [
            Task(description="Morning walk", duration=30, frequency="daily", id="t1"),
            Task(description="Breakfast", duration=15, frequency="daily", id="t2"),
            Task(description="Midday walk", duration=30, frequency="daily", id="t3"),
            Task(description="Lunch prep", duration=20, frequency="daily", id="t4"),
            Task(description="Afternoon play", duration=30, frequency="daily", id="t5"),
            Task(description="Evening walk", duration=30, frequency="daily", id="t6"),
        ]
        for task in tasks:
            pet.add_task(task)

        schedule = owner.generate_plan()

        total = len(schedule.scheduled_slots) + len(schedule.unmet_tasks)
        success_rate = len(schedule.scheduled_slots) / total if total > 0 else 0

        # System should schedule at least 80% of tasks
        assert success_rate >= 0.8, \
            f"Success rate {success_rate:.0%} below 80% threshold"

    def test_recurring_tasks_distributed_not_clustered(self):
        """Reliability: Multiple recurring tasks shouldn't cluster at same time."""
        owner = Owner(name="Alex", contact_info="alex@example.com")
        owner.set_availability(["08:00-20:00"])
        pet = Pet(name="Buddy", breed="dog", age=3, sex="Male")
        owner.add_pet(pet)

        tasks = [
            Task(description="Walk 1", duration=20, frequency="daily", id="t1"),
            Task(description="Walk 2", duration=20, frequency="daily", id="t2"),
            Task(description="Walk 3", duration=20, frequency="daily", id="t3"),
        ]
        for task in tasks:
            pet.add_task(task)

        schedule = owner.generate_plan()

        start_hours = [slot.start_time.hour for slot in schedule.scheduled_slots]

        # Should have at least 2 different hours (not all clustered)
        unique_hours = len(set(start_hours))
        assert unique_hours >= 2, \
            f"Tasks clustered at {unique_hours} hour(s); should be distributed"

    def test_schedule_is_deterministic(self):
        """Reliability: Same input should produce same output (deterministic)."""
        def create_schedule():
            owner = Owner(name="Alex", contact_info="alex@example.com")
            owner.set_availability(["08:00-20:00"])
            pet = Pet(name="Buddy", breed="dog", age=3, sex="Male")
            owner.add_pet(pet)

            tasks = [
                Task(description="Walk", duration=30, frequency="daily", id="t1"),
                Task(description="Feed", duration=20, frequency="daily", id="t2"),
            ]
            for task in tasks:
                pet.add_task(task)

            return owner.generate_plan()

        schedule1 = create_schedule()
        schedule2 = create_schedule()

        # Both should schedule same number of tasks
        assert len(schedule1.scheduled_slots) == len(schedule2.scheduled_slots)

        # Tasks should be at same times
        for slot1, slot2 in zip(schedule1.scheduled_slots, schedule2.scheduled_slots):
            assert slot1.start_time == slot2.start_time
            assert slot1.end_time == slot2.end_time

    def test_handles_very_tight_schedule(self):
        """Reliability: Gracefully handles impossibly tight schedules."""
        owner = Owner(name="Alex", contact_info="alex@example.com")
        owner.set_availability(["09:00-09:30"])  # Only 30 minutes
        pet = Pet(name="Buddy", breed="dog", age=3, sex="Male")
        owner.add_pet(pet)

        tasks = [
            Task(description="Walk", duration=30, id="t1"),
            Task(description="Feed", duration=30, id="t2"),
            Task(description="Play", duration=30, id="t3"),
        ]
        for task in tasks:
            pet.add_task(task)

        # Should not crash
        schedule = owner.generate_plan()

        # Should schedule at least 1 task
        assert len(schedule.scheduled_slots) >= 1
        # Should have unmet tasks recorded
        assert len(schedule.unmet_tasks) > 0
        # Should log errors
        assert len(schedule.errors) > 0 or len(schedule.warnings) > 0

    def test_handles_single_task(self):
        """Reliability: Handles edge case of single task."""
        owner = Owner(name="Alex", contact_info="alex@example.com")
        owner.set_availability(["08:00-20:00"])
        pet = Pet(name="Buddy", breed="dog", age=3, sex="Male")
        owner.add_pet(pet)

        task = Task(description="Walk", duration=30, id="t1")
        pet.add_task(task)

        schedule = owner.generate_plan()

        assert len(schedule.scheduled_slots) == 1
        assert len(schedule.unmet_tasks) == 0

    def test_handles_zero_tasks(self):
        """Reliability: Handles edge case of no tasks."""
        owner = Owner(name="Alex", contact_info="alex@example.com")
        owner.set_availability(["08:00-20:00"])
        pet = Pet(name="Buddy", breed="dog", age=3, sex="Male")
        owner.add_pet(pet)

        # No tasks added

        schedule = owner.generate_plan()

        assert len(schedule.scheduled_slots) == 0
        assert len(schedule.unmet_tasks) == 0

    def test_schedule_validates_correctly(self):
        """Reliability: Schedule.validate() should catch invalid schedules."""
        schedule = Schedule()

        base_time = datetime.now()
        slot1_start = base_time
        slot1_end = base_time + timedelta(minutes=30)
        slot2_start = base_time + timedelta(minutes=20)  # Overlaps!
        slot2_end = base_time + timedelta(minutes=50)

        # Create an invalid schedule manually
        task1 = Task(description="Task 1", duration=30, id="t1")
        task2 = Task(description="Task 2", duration=30, id="t2")

        from pawpal_system import ScheduledSlot
        schedule.scheduled_slots.append(ScheduledSlot(task=task1, start_time=slot1_start, end_time=slot1_end))
        schedule.scheduled_slots.append(ScheduledSlot(task=task2, start_time=slot2_start, end_time=slot2_end))

        # Validation should catch the overlap
        is_valid = schedule.validate()
        assert not is_valid, "Validation should detect overlapping slots"


class TestReliabilityMetrics:
    """Calculate and report on system reliability."""

    def test_calculate_system_reliability_score(self):
        """Measure overall system reliability as percentage."""
        owner = Owner(name="Alex", contact_info="alex@example.com")
        owner.set_availability(["08:00-20:00"])
        pet = Pet(name="Buddy", breed="dog", age=3, sex="Male")
        owner.add_pet(pet)

        tasks = [
            Task(description=f"Task {i}", duration=20, id=f"t{i}")
            for i in range(10)
        ]
        for task in tasks:
            pet.add_task(task)

        schedule = owner.generate_plan()

        total = len(schedule.scheduled_slots) + len(schedule.unmet_tasks)
        reliability_pct = len(schedule.scheduled_slots) / total * 100 if total > 0 else 100

        assert 0 <= reliability_pct <= 100
        # Store as metric
        assert reliability_pct > 0, "System should schedule at least some tasks"

    def test_no_task_duration_mismatch(self):
        """Reliability: No scheduled slot should have wrong duration."""
        owner = Owner(name="Alex", contact_info="alex@example.com")
        owner.set_availability(["08:00-20:00"])
        pet = Pet(name="Buddy", breed="dog", age=3, sex="Male")
        owner.add_pet(pet)

        task = Task(description="Walk", duration=27, id="t1")  # Odd duration
        pet.add_task(task)

        schedule = owner.generate_plan()

        for slot in schedule.scheduled_slots:
            slot_duration_minutes = (slot.end_time - slot.start_time).total_seconds() / 60
            assert slot_duration_minutes == slot.task.duration, \
                f"Duration mismatch: slot={slot_duration_minutes}, task={slot.task.duration}"

    def test_15min_alignment_preserved(self):
        """Reliability: All scheduled times should align to 15-minute boundaries."""
        owner = Owner(name="Alex", contact_info="alex@example.com")
        owner.set_availability(["08:00-20:00"])
        pet = Pet(name="Buddy", breed="dog", age=3, sex="Male")
        owner.add_pet(pet)

        task = Task(description="Walk", duration=20, id="t1")
        pet.add_task(task)

        schedule = owner.generate_plan()

        for slot in schedule.scheduled_slots:
            # Check start time is on 15-minute boundary
            assert slot.start_time.minute % 15 == 0, \
                f"Start time {slot.start_time} not aligned to 15-min boundary"
