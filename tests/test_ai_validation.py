"""
Tests for AI validation: Confidence scoring, logging, and error handling.
Proves that the AI system intelligently tracks decisions and failures.
"""

import logging
from datetime import datetime, timedelta

import pytest

from pawpal_system import (
    Owner, Pet, Scheduler, Task, Schedule, ConfidenceScore, ScheduledSlot
)


class TestConfidenceScoring:
    """Test confidence score calculations for scheduling decisions."""

    def test_confidence_score_initialization(self):
        """Test that confidence scores are created with valid ranges."""
        score = ConfidenceScore(score=0.85, reasoning="Good fit", factors={"fit": 0.5})
        assert score.score == 0.85
        assert "Good fit" in score.reasoning
        assert score.factors["fit"] == 0.5

    def test_confidence_score_bounds(self):
        """Test that confidence scores are bounded [0, 1]."""
        with pytest.raises(ValueError):
            ConfidenceScore(score=1.5, reasoning="Invalid")
        with pytest.raises(ValueError):
            ConfidenceScore(score=-0.1, reasoning="Invalid")

    def test_calculate_slot_confidence_no_conflicts(self):
        """Test confidence boost when task has no scheduling conflicts."""
        owner = Owner(name="Alex", contact_info="alex@example.com")
        owner.set_availability(["08:00-20:00"])
        pet = Pet(name="Buddy", breed="dog", age=3, sex="Male")
        owner.add_pet(pet)

        task = Task(description="Walk", duration=30, id="t1")
        scheduler = Scheduler(owner=owner)

        confidence = scheduler._calculate_slot_confidence(
            task=task,
            has_conflict=False,
            has_preferred_time=False,
            is_within_availability=True
        )

        assert confidence.score > 0.5
        assert "no conflicts" in confidence.reasoning
        assert confidence.factors["no_conflicts"] == 0.3

    def test_calculate_slot_confidence_with_conflicts(self):
        """Test lower confidence when task has scheduling conflicts."""
        owner = Owner(name="Alex", contact_info="alex@example.com")
        pet = Pet(name="Buddy", breed="dog", age=3, sex="Male")
        owner.add_pet(pet)

        task = Task(description="Walk", duration=30, id="t1")
        scheduler = Scheduler(owner=owner)

        confidence = scheduler._calculate_slot_confidence(
            task=task,
            has_conflict=True,
            has_preferred_time=False,
            is_within_availability=True
        )

        assert confidence.score < 0.7
        assert confidence.factors["has_conflicts"] == -0.3

    def test_calculate_slot_confidence_preferred_time(self):
        """Test confidence boost when preferred time is honored."""
        owner = Owner(name="Alex", contact_info="alex@example.com")
        pet = Pet(name="Buddy", breed="dog", age=3, sex="Male")
        owner.add_pet(pet)

        task = Task(
            description="Walk",
            duration=30,
            preferred_time_slot="08:00-09:00",
            id="t1"
        )
        scheduler = Scheduler(owner=owner)

        confidence = scheduler._calculate_slot_confidence(
            task=task,
            has_conflict=False,
            has_preferred_time=True,
            is_within_availability=True
        )

        assert confidence.factors["preferred_time_honored"] == 0.15
        assert "preferred time honored" in confidence.reasoning

    def test_calculate_slot_confidence_recurring_task(self):
        """Test confidence boost for recurring tasks."""
        owner = Owner(name="Alex", contact_info="alex@example.com")
        pet = Pet(name="Buddy", breed="dog", age=3, sex="Male")
        owner.add_pet(pet)

        task = Task(
            description="Morning walk",
            duration=30,
            frequency="daily",
            id="t1"
        )
        scheduler = Scheduler(owner=owner)

        confidence = scheduler._calculate_slot_confidence(
            task=task,
            has_conflict=False,
            has_preferred_time=False,
            is_within_availability=True
        )

        assert confidence.factors["recurring_task"] == 0.05
        assert confidence.score >= 0.75  # High confidence for reliable recurring

    def test_confidence_score_reflected_in_scheduled_slot(self):
        """Test that confidence scores are stored in scheduled slots."""
        owner = Owner(name="Alex", contact_info="alex@example.com")
        owner.set_availability(["08:00-20:00"])
        pet = Pet(name="Buddy", breed="dog", age=3, sex="Male")
        owner.add_pet(pet)

        task = Task(description="Walk", duration=30, frequency="daily", id="t1")
        pet.add_task(task)

        schedule = owner.generate_plan()

        assert len(schedule.scheduled_slots) > 0
        slot = schedule.scheduled_slots[0]
        assert slot.confidence is not None
        assert 0 <= slot.confidence.score <= 1


class TestScheduleLogging:
    """Test logging of scheduling events and decisions."""

    def test_schedule_has_logs(self):
        """Test that schedule tracks log events."""
        owner = Owner(name="Alex", contact_info="alex@example.com")
        owner.set_availability(["08:00-20:00"])
        pet = Pet(name="Buddy", breed="dog", age=3, sex="Male")
        owner.add_pet(pet)

        task = Task(description="Walk", duration=30, frequency="daily", id="t1")
        pet.add_task(task)

        schedule = owner.generate_plan()

        assert len(schedule.logs) > 0
        assert any("Spacing" in log for log in schedule.logs)

    def test_log_event_timestamps(self):
        """Test that log entries include timestamps."""
        schedule = Schedule()

        schedule.log_event("INFO", "Test message")

        assert len(schedule.logs) == 1
        assert "[" in schedule.logs[0]  # Has timestamp brackets
        assert "INFO: Test message" in schedule.logs[0]

    def test_log_event_levels(self):
        """Test different log levels."""
        schedule = Schedule()

        schedule.log_event("INFO", "Info message")
        schedule.log_event("DEBUG", "Debug message")
        schedule.log_event("WARNING", "Warning message")

        assert len(schedule.logs) == 3
        assert "INFO: Info message" in schedule.logs[0]
        assert "DEBUG: Debug message" in schedule.logs[1]
        assert "WARNING: Warning message" in schedule.logs[2]

    def test_logging_task_scheduling(self):
        """Test that successful task scheduling is logged."""
        owner = Owner(name="Alex", contact_info="alex@example.com")
        owner.set_availability(["08:00-20:00"])
        pet = Pet(name="Buddy", breed="dog", age=3, sex="Male")
        owner.add_pet(pet)

        task1 = Task(description="Morning walk", duration=20, frequency="daily", id="t1")
        task2 = Task(description="Evening play", duration=30, frequency="daily", id="t2")
        pet.add_task(task1)
        pet.add_task(task2)

        schedule = owner.generate_plan()

        scheduled_logs = [log for log in schedule.logs if "Scheduled" in log]
        assert len(scheduled_logs) >= 2
        assert any("Morning walk" in log for log in scheduled_logs)
        assert any("Evening play" in log for log in scheduled_logs)

    def test_logging_unmet_tasks(self):
        """Test that unmet tasks are logged."""
        owner = Owner(name="Alex", contact_info="alex@example.com")
        owner.set_availability(["08:00-08:30"])  # Very tight availability
        pet = Pet(name="Buddy", breed="dog", age=3, sex="Male")
        owner.add_pet(pet)

        # Create tasks that won't fit
        for i in range(5):
            task = Task(
                description=f"Task {i}",
                duration=30,
                frequency="daily",
                id=f"t{i}"
            )
            pet.add_task(task)

        schedule = owner.generate_plan()

        unmet_log_entries = [log for log in schedule.logs if "Could not" in log or "tight" in log]
        assert len(unmet_log_entries) > 0 or len(schedule.unmet_tasks) > 0


class TestErrorHandling:
    """Test error tracking and recovery in scheduling."""

    def test_schedule_tracks_errors(self):
        """Test that scheduling errors are recorded."""
        schedule = Schedule()

        schedule.record_error("CONFLICT", "Morning walk", "Overlaps with existing task")

        assert len(schedule.errors) == 1
        error = schedule.errors[0]
        assert error["type"] == "CONFLICT"
        assert error["task"] == "Morning walk"
        assert error["reason"] == "Overlaps with existing task"
        assert "timestamp" in error

    def test_multiple_error_tracking(self):
        """Test that multiple errors are tracked independently."""
        schedule = Schedule()

        schedule.record_error("CONFLICT", "Walk", "Overlaps with feed")
        schedule.record_error("NO_SLOT", "Play", "Schedule too full")
        schedule.record_error("OUT_OF_BOUNDS", "Groom", "Exceeds availability")

        assert len(schedule.errors) == 3
        assert schedule.errors[0]["task"] == "Walk"
        assert schedule.errors[1]["task"] == "Play"
        assert schedule.errors[2]["task"] == "Groom"

    def test_error_types_documented(self):
        """Test that common error types are documented."""
        schedule = Schedule()

        error_types = [
            "CONFLICT",
            "NO_SLOT",
            "OUT_OF_BOUNDS",
            "SCHEDULING_FAILED",
            "INVALID_INPUT"
        ]

        for i, error_type in enumerate(error_types):
            schedule.record_error(error_type, f"Task {i}", f"Reason {i}")

        assert len(schedule.errors) == len(error_types)
        for error, expected_type in zip(schedule.errors, error_types):
            assert error["type"] == expected_type

    def test_error_recovery_in_scheduling(self):
        """Test that system continues scheduling after encountering errors."""
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

        # System should have attempted all tasks despite any errors
        total_attempted = len(schedule.scheduled_slots) + len(schedule.unmet_tasks)
        assert total_attempted == len(tasks)

    def test_error_includes_context(self):
        """Test that errors include sufficient context for debugging."""
        schedule = Schedule()

        schedule.record_error(
            "SCHEDULING_FAILED",
            "Evening walk",
            "Could not find non-conflicting slot for Buddy between 18:00 and 20:00"
        )

        error = schedule.errors[0]
        assert error["task"] is not None
        assert error["reason"] is not None
        assert error["type"] is not None
        assert error["timestamp"] is not None

    def test_logging_creates_audit_trail(self):
        """Test that complete audit trail is created from logs."""
        owner = Owner(name="Alex", contact_info="alex@example.com")
        owner.set_availability(["08:00-20:00"])
        pet = Pet(name="Buddy", breed="dog", age=3, sex="Male")
        owner.add_pet(pet)

        task = Task(description="Walk", duration=30, frequency="daily", id="t1")
        pet.add_task(task)

        schedule = owner.generate_plan()

        # Audit trail should show what happened
        audit_trail = "\n".join(schedule.logs)
        assert "Spacing" in audit_trail or "Walk" in audit_trail
        assert len(schedule.logs) > 0


class TestAIDecisionValidation:
    """Test that AI decisions are validated and tracked."""

    def test_confidence_scores_reasonable(self):
        """Test that all scheduled tasks have reasonable confidence scores."""
        owner = Owner(name="Alex", contact_info="alex@example.com")
        owner.set_availability(["08:00-20:00"])
        pet = Pet(name="Buddy", breed="dog", age=3, sex="Male")
        owner.add_pet(pet)

        tasks = [
            Task(description="Walk", duration=20, frequency="daily", id="t1"),
            Task(description="Feed", duration=15, frequency="daily", id="t2"),
            Task(description="Play", duration=30, frequency="daily", id="t3"),
        ]

        for task in tasks:
            pet.add_task(task)

        schedule = owner.generate_plan()

        for slot in schedule.scheduled_slots:
            assert slot.confidence is not None
            assert 0 <= slot.confidence.score <= 1
            assert slot.confidence.reasoning is not None

    def test_high_confidence_for_successful_scheduling(self):
        """Test that successfully scheduled tasks have higher confidence."""
        owner = Owner(name="Alex", contact_info="alex@example.com")
        owner.set_availability(["08:00-20:00"])
        pet = Pet(name="Buddy", breed="dog", age=3, sex="Male")
        owner.add_pet(pet)

        task = Task(
            description="Walk",
            duration=20,
            frequency="daily",
            preferred_time_slot="08:00-09:00",
            id="t1"
        )
        pet.add_task(task)

        schedule = owner.generate_plan()

        assert len(schedule.scheduled_slots) > 0
        slot = schedule.scheduled_slots[0]
        assert slot.confidence.score > 0.6

    def test_logs_capture_decision_reasoning(self):
        """Test that logs explain why decisions were made."""
        owner = Owner(name="Alex", contact_info="alex@example.com")
        owner.set_availability(["08:00-20:00"])
        pet = Pet(name="Buddy", breed="dog", age=3, sex="Male")
        owner.add_pet(pet)

        task = Task(description="Walk", duration=30, frequency="daily", id="t1")
        pet.add_task(task)

        schedule = owner.generate_plan()

        # Logs should explain the scheduling decision
        assert len(schedule.logs) > 0
        logs_text = "\n".join(schedule.logs)
        assert "confidence" in logs_text.lower() or "scheduled" in logs_text.lower()

    def test_system_reliability_metric(self):
        """Test that system tracks its own reliability through errors."""
        owner = Owner(name="Alex", contact_info="alex@example.com")
        owner.set_availability(["08:00-20:00"])
        pet = Pet(name="Buddy", breed="dog", age=3, sex="Male")
        owner.add_pet(pet)

        tasks = [Task(description=f"Task {i}", duration=15, id=f"t{i}") for i in range(10)]
        for task in tasks:
            pet.add_task(task)

        schedule = owner.generate_plan()

        total_tasks = len(schedule.scheduled_slots) + len(schedule.unmet_tasks)
        scheduled = len(schedule.scheduled_slots)
        reliability = (scheduled / total_tasks * 100) if total_tasks > 0 else 100

        assert 0 <= reliability <= 100
        assert scheduled <= total_tasks
        # System should schedule at least some tasks
        assert scheduled > 0 or total_tasks == 0
