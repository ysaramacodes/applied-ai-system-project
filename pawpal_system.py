"""
PawPal+ System Classes
A pet care scheduling assistant for busy owners.
"""

from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import List, Optional


@dataclass
class Pet:
    """Represents a pet with care requirements and health information."""
    name: str
    breed: str
    age: int
    sex: str
    health_conditions: List[str] = field(default_factory=list)
    medications: List[str] = field(default_factory=list)
    emergency_contact: str = ""
    activities: List[str] = field(default_factory=list)
    grooming: str = ""
    tasks: List["Task"] = field(default_factory=list)

    def add_task(self, task: "Task") -> None:
        """Assign a task to this pet."""
        task.pet = self
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove a task from this pet."""
        self.tasks = [task for task in self.tasks if task.id != task_id]

    def eat(self) -> None:
        """Record feeding event."""
        pass

    def sleep(self) -> None:
        """Record sleep event."""
        pass

    def walk(self) -> None:
        """Record walk event."""
        pass

    def take_medication(self) -> None:
        """Record medication administration."""
        pass

    def play(self) -> None:
        """Record play/enrichment event."""
        pass

    def potty(self) -> None:
        """Record potty break."""
        pass

    def groom(self) -> None:
        """Record grooming event."""
        pass


@dataclass
class Task:
    """Represents a single pet care activity."""
    description: str
    time: Optional[datetime] = None
    duration: int = 0
    frequency: str = ""
    completion_status: bool = False
    pet: Optional[Pet] = None
    id: str = ""
    preferred_time_slot: str = ""
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    assigned_to: Optional[str] = None
    notes: List[str] = field(default_factory=list)

    def schedule(self, start_time: datetime, end_time: datetime) -> None:
        """Schedule the task for a time slot."""
        if end_time <= start_time:
            raise ValueError("End time must be after start time.")
        self.scheduled_start = start_time
        self.scheduled_end = end_time
        self.time = start_time
        self.completion_status = False

    def reschedule(self, new_start: datetime, new_end: datetime) -> None:
        """Reschedule the task to a different time."""
        self.schedule(new_start, new_end)

    def mark_complete(self, completed_time: datetime, notes: str = "") -> None:
        """Mark the task as completed."""
        self.completion_status = True
        self.scheduled_end = completed_time
        if notes:
            self.notes.append(notes)

    def cancel(self, reason: str = "") -> None:
        """Cancel the task."""
        self.completion_status = False
        if reason:
            self.notes.append(f"Cancelled: {reason}")

    def is_recurring(self) -> bool:
        """Return whether this task is recurring."""
        return bool(self.frequency)

    def is_conflicting(self, other: "Task") -> bool:
        """Check whether this task conflicts with another scheduled task."""
        if not self.scheduled_start or not self.scheduled_end:
            return False
        if not other.scheduled_start or not other.scheduled_end:
            return False
        return not (
            self.scheduled_end <= other.scheduled_start
            or self.scheduled_start >= other.scheduled_end
        )

    def to_dict(self) -> dict:
        """Serialize task to dictionary."""
        return {
            "id": self.id,
            "description": self.description,
            "time": self.time.isoformat() if self.time else None,
            "duration": self.duration,
            "frequency": self.frequency,
            "completion_status": self.completion_status,
            "pet": self.pet.name if self.pet else None,
            "preferred_time_slot": self.preferred_time_slot,
            "scheduled_start": self.scheduled_start.isoformat() if self.scheduled_start else None,
            "scheduled_end": self.scheduled_end.isoformat() if self.scheduled_end else None,
            "assigned_to": self.assigned_to,
            "notes": self.notes,
        }


@dataclass
class Owner:
    """Represents a pet owner."""
    name: str
    contact_info: str
    availability: List[str] = field(default_factory=list)
    preferences: dict = field(default_factory=dict)
    pets: List[Pet] = field(default_factory=list)

    @property
    def tasks(self) -> List[Task]:
        """Return all tasks assigned to the owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's collection."""
        self.pets.append(pet)

    def create_task(self, pet: Pet, task: Task) -> None:
        """Assign a task to a pet."""
        if pet not in self.pets:
            self.add_pet(pet)
        pet.add_task(task)

    def set_availability(self, availability: List[str]) -> None:
        """Set availability windows."""
        self.availability = availability

    def set_preferences(self, preferences: dict) -> None:
        """Set scheduling preferences."""
        self.preferences = preferences

    def generate_plan(self) -> "Schedule":
        """Generate a daily care plan."""
        scheduler = Scheduler(owner=self, pets=self.pets, tasks=self.tasks)
        return scheduler.schedule()


@dataclass
class ScheduledSlot:
    """A time slot within a schedule with an assigned task."""
    task: Task
    start_time: datetime
    end_time: datetime
    explanation: str = ""


@dataclass
class Schedule:
    """Represents a daily schedule of pet care tasks."""
    date: date = field(default_factory=date.today)
    day: str = ""
    availability: List[str] = field(default_factory=list)
    scheduled_slots: List[ScheduledSlot] = field(default_factory=list)
    total_duration: int = 0
    owner: Optional[Owner] = None
    unmet_tasks: List[Task] = field(default_factory=list)
    status: str = "draft"

    def add_scheduled_task_entry(self, task: Task, start_time: datetime, end_time: datetime) -> None:
        """Add a scheduled task entry to the schedule."""
        slot = ScheduledSlot(task=task, start_time=start_time, end_time=end_time)
        self.scheduled_slots.append(slot)
        self.total_duration += (end_time - start_time).seconds // 60

    def remove_scheduled_entry(self, slot_index: int) -> None:
        """Remove a scheduled entry."""
        if 0 <= slot_index < len(self.scheduled_slots):
            slot = self.scheduled_slots.pop(slot_index)
            self.total_duration -= (slot.end_time - slot.start_time).seconds // 60

    def modify_slot(self, slot_index: int, new_start: datetime, new_end: datetime) -> None:
        """Modify an existing slot's time."""
        if 0 <= slot_index < len(self.scheduled_slots):
            slot = self.scheduled_slots[slot_index]
            old_duration = (slot.end_time - slot.start_time).seconds // 60
            new_duration = (new_end - new_start).seconds // 60
            self.total_duration += new_duration - old_duration
            slot.start_time = new_start
            slot.end_time = new_end

    def get_slots(self) -> List[ScheduledSlot]:
        """Get all scheduled slots."""
        return self.scheduled_slots

    def validate(self) -> bool:
        """Validate the schedule against constraints."""
        if not self.scheduled_slots:
            return True

        ordered_slots = sorted(self.scheduled_slots, key=lambda s: s.start_time)
        for index in range(1, len(ordered_slots)):
            prev_slot = ordered_slots[index - 1]
            current_slot = ordered_slots[index]
            if prev_slot.end_time > current_slot.start_time:
                return False
        return True


class Scheduler:
    """The brain that retrieves, organizes, and manages tasks across owner pets."""

    def __init__(self, owner: Owner, pets: Optional[List[Pet]] = None, tasks: Optional[List[Task]] = None):
        """Initialize the scheduler with an owner, their pets, and tasks to manage."""
        self.owner = owner
        self.pets = pets if pets is not None else owner.pets
        self.tasks = tasks if tasks is not None else self.retrieve_tasks()
        self.availability = owner.availability
        self.constraints = {}
        self.scheduled_plan: Optional[Schedule] = None

    def retrieve_tasks(self) -> List[Task]:
        """Collect all pet tasks from the owner."""
        return [task for pet in self.owner.pets for task in pet.tasks]

    def organize_tasks(self) -> List[Task]:
        """Sort tasks by completion status and scheduled time."""
        return sorted(
            self.tasks,
            key=lambda task: (
                task.completion_status,
                task.time or datetime.max,
            ),
        )

    def schedule(self) -> Schedule:
        """Generate an optimized schedule."""
        self.tasks = self.retrieve_tasks()
        organized_tasks = self.organize_tasks()
        plan = Schedule(owner=self.owner, availability=self.availability)

        for task in organized_tasks:
            if task.scheduled_start and task.scheduled_end:
                plan.add_scheduled_task_entry(task, task.scheduled_start, task.scheduled_end)
            elif task.time:
                end_time = task.time + timedelta(minutes=task.duration)
                task.schedule(task.time, end_time)
                plan.add_scheduled_task_entry(task, task.time, end_time)
            else:
                plan.unmet_tasks.append(task)

        self.scheduled_plan = plan
        return plan

    def manage_task(self, task: Task) -> None:
        """Update or reschedule a specific task."""
        if task not in self.tasks:
            self.tasks.append(task)

    def explain_decision(self, slot: ScheduledSlot) -> str:
        """Explain the reasoning for a scheduling decision."""
        return slot.explanation or "Scheduled to fit owner availability and pet needs."
