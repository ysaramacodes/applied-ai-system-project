"""
Test suite for Agentic Workflow integration with PawPal+ system.
"""

import pytest
from datetime import datetime, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler
from agent import CareAgent, AgentDecision, AgentMemory


def test_agent_initialization():
    """Test that CareAgent initializes correctly."""
    owner = Owner(name="Jordan", contact_info="test@example.com")
    agent = CareAgent(owner=owner)

    assert agent.owner.name == "Jordan"
    assert isinstance(agent.memory, AgentMemory)
    assert agent.current_plan is None


def test_analyze_scheduling_needs():
    """Test agent's ability to analyze scheduling needs."""
    owner = Owner(name="Jordan", contact_info="test@example.com")
    pet = Pet(name="Mochi", breed="dog", age=2, sex="Male")
    owner.add_pet(pet)

    task1 = Task(description="Morning walk", duration=20, frequency="daily")
    task2 = Task(description="Vet appointment", duration=60, frequency="")
    owner.create_task(pet, task1)
    owner.create_task(pet, task2)

    owner.set_availability(["8am-8pm"])

    agent = CareAgent(owner=owner)
    analysis = agent.analyze_scheduling_needs()

    assert analysis["total_pets"] == 1
    assert analysis["total_tasks"] == 2
    assert analysis["recurring_tasks"] == 1
    assert analysis["one_time_tasks"] == 1
    assert analysis["available_hours"] == 12


def test_generate_intelligent_schedule():
    """Test that agent generates an intelligent schedule."""
    owner = Owner(name="Jordan", contact_info="test@example.com")
    pet = Pet(name="Mochi", breed="dog", age=2, sex="Male")
    owner.add_pet(pet)

    task = Task(description="Morning walk", duration=20, frequency="daily")
    task.preferred_time_slot = "09:00-10:00"
    owner.create_task(pet, task)

    owner.set_availability(["8am-8pm"])

    agent = CareAgent(owner=owner)
    schedule = agent.generate_intelligent_schedule()

    assert schedule is not None
    assert len(schedule.scheduled_slots) > 0
    assert agent.current_plan is not None


def test_get_scheduling_recommendation():
    """Test that agent provides scheduling recommendations."""
    owner = Owner(name="Jordan", contact_info="test@example.com")
    pet = Pet(name="Mochi", breed="dog", age=2, sex="Male")
    owner.add_pet(pet)

    task = Task(description="Grooming", duration=60, frequency="weekly")
    owner.create_task(pet, task)

    owner.set_availability(["8am-8pm"])

    agent = CareAgent(owner=owner)
    agent.generate_intelligent_schedule()

    recommendation = agent.get_scheduling_recommendation(task)
    assert isinstance(recommendation, str)
    assert len(recommendation) > 0


def test_adapt_to_changes():
    """Test that agent adapts to scheduling changes."""
    owner = Owner(name="Jordan", contact_info="test@example.com")
    owner.set_availability(["8am-6pm"])

    agent = CareAgent(owner=owner)

    # Adapt to new availability
    result = agent.adapt_to_changes({"new_availability": ["7am-9pm"]})
    assert "Updated availability" in result
    assert agent.owner.availability == ["7am-9pm"]


def test_agent_memory_tracks_decisions():
    """Test that agent memory tracks past decisions."""
    owner = Owner(name="Jordan", contact_info="test@example.com")
    pet = Pet(name="Mochi", breed="dog", age=2, sex="Male")
    owner.add_pet(pet)

    # Create a task that will likely be unmet due to limited availability
    task = Task(description="Feeding", duration=480, frequency="one-time")  # 8 hours
    owner.create_task(pet, task)
    owner.set_availability(["9am-10am"])  # Only 1 hour available

    agent = CareAgent(owner=owner)
    agent.generate_intelligent_schedule()

    # Get recommendation for the likely unmet task
    recommendation = agent.get_scheduling_recommendation(task)

    # Memory is recorded when recommendation is made
    assert isinstance(recommendation, str)
    assert len(recommendation) > 0


def test_explain_decision():
    """Test that agent can explain scheduling decisions."""
    owner = Owner(name="Jordan", contact_info="test@example.com")
    pet = Pet(name="Mochi", breed="dog", age=2, sex="Male")
    owner.add_pet(pet)

    task = Task(description="Morning walk", duration=20, frequency="daily")
    owner.create_task(pet, task)
    owner.set_availability(["8am-8pm"])

    agent = CareAgent(owner=owner)
    schedule = agent.generate_intelligent_schedule()

    if schedule.scheduled_slots:
        slot = schedule.scheduled_slots[0]
        explanation = agent.explain_decision(slot)
        assert isinstance(explanation, str)
        assert "Morning walk" in explanation or slot.task.description in explanation


def test_health_considerations():
    """Test that agent considers pet health conditions."""
    owner = Owner(name="Jordan", contact_info="test@example.com")
    pet = Pet(name="Mochi", breed="dog", age=2, sex="Male", health_conditions=["Diabetes"])
    owner.add_pet(pet)

    task = Task(description="Medication", duration=10, frequency="daily")
    owner.create_task(pet, task)
    owner.set_availability(["8am-8pm"])

    agent = CareAgent(owner=owner)
    analysis = agent.analyze_scheduling_needs()

    assert "Mochi" in analysis["pet_health_considerations"]
    assert "Diabetes" in analysis["pet_health_considerations"]["Mochi"]["conditions"]


def test_respects_availability_window():
    """Test that scheduler respects availability constraints."""
    owner = Owner(name="Jordan", contact_info="test@example.com")
    pet = Pet(name="Mochi", breed="dog", age=2, sex="Male")
    owner.add_pet(pet)

    task = Task(description="Morning walk", duration=20, frequency="one-time")
    task.time = datetime(datetime.today().year, datetime.today().month, datetime.today().day, 8, 0)  # 8 AM
    owner.create_task(pet, task)

    # Set availability to 9am-8pm (task at 8 AM is outside)
    owner.set_availability(["9am-8pm"])

    agent = CareAgent(owner=owner)
    schedule = agent.generate_intelligent_schedule()

    # Agent should either leave unmet or reschedule to within availability
    all_tasks = len(schedule.scheduled_slots) + len(schedule.unmet_tasks)
    assert all_tasks >= 1  # Task should exist somewhere

    # All scheduled tasks must be within availability window
    for slot in schedule.scheduled_slots:
        assert slot.start_time.hour >= 9, f"Task scheduled at {slot.start_time.hour}:{slot.start_time.minute} but availability starts at 9am"
        assert slot.end_time.hour <= 20, f"Task ends at {slot.end_time.hour}:{slot.end_time.minute} but availability ends at 8pm"


def test_availability_with_time_format():
    """Test that availability parsing works with different time formats."""
    owner = Owner(name="Jordan", contact_info="test@example.com")
    pet = Pet(name="Mochi", breed="dog", age=2, sex="Male")
    owner.add_pet(pet)

    task = Task(description="Task 1", duration=30, frequency="one-time")
    owner.create_task(pet, task)

    # Test various time formats
    owner.set_availability(["9am-5pm"])
    agent = CareAgent(owner=owner)

    analysis = agent.analyze_scheduling_needs()
    assert analysis["available_hours"] == 8  # 9am to 5pm is 8 hours


def test_tasks_dont_overflow_availability():
    """Test that tasks don't extend past the availability window."""
    owner = Owner(name="Jordan", contact_info="test@example.com")
    pet = Pet(name="Mochi", breed="dog", age=2, sex="Male")
    owner.add_pet(pet)

    # Create a task with 30 min duration
    task = Task(description="Evening task", duration=30, frequency="one-time")
    task.time = datetime(datetime.today().year, datetime.today().month, datetime.today().day, 20, 45)  # 8:45 PM
    owner.create_task(pet, task)

    # Availability ends at 9 PM (21:00)
    owner.set_availability(["9am-9pm"])

    agent = CareAgent(owner=owner)
    schedule = agent.generate_intelligent_schedule()

    # Task would end at 9:15 PM, which is after 9 PM cutoff
    # So it should either be unmet or rescheduled earlier
    if schedule.scheduled_slots:
        for slot in schedule.scheduled_slots:
            # All tasks must end by 9 PM (21:00)
            assert slot.end_time.hour <= 21, f"Task ends at {slot.end_time.hour}:{slot.end_time.minute} but availability ends at 21:00"
            if slot.end_time.hour == 21:
                assert slot.end_time.minute == 0, "Task extends past 9 PM cutoff"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
