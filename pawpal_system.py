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
        """Mark the task as completed and create next occurrence if recurring."""
        self.completion_status = True
        self.scheduled_end = completed_time
        if notes:
            self.notes.append(notes)
        
        # Create next occurrence if recurring
        if self.is_recurring() and self.pet:
            self._create_next_occurrence()

    def _create_next_occurrence(self) -> None:
        """Create a new task instance for the next occurrence of a recurring task."""
        if not self.frequency or not self.pet:
            return

        base_time = self.time or datetime.now()
        frequency_key = self.frequency.lower()
        interval_map = {
            "daily": timedelta(days=1),
            "weekly": timedelta(weeks=1),
        }

        if frequency_key in interval_map:
            next_time = base_time + interval_map[frequency_key]
        elif frequency_key == "monthly":
            try:
                from dateutil.relativedelta import relativedelta

                next_time = base_time + relativedelta(months=1)
            except ImportError:
                next_time = base_time + timedelta(days=30)
        else:
            return

        if any(task.description == self.description and task.time == next_time for task in self.pet.tasks):
            return

        next_task = Task(
            description=self.description,
            time=next_time,
            duration=self.duration,
            frequency=self.frequency,
            preferred_time_slot=self.preferred_time_slot,
            id=f"{self.id}-{next_time.strftime('%Y%m%d')}",
        )
        self.pet.add_task(next_task)

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
    warnings: List[str] = field(default_factory=list)
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
        """Get all scheduled slots sorted by start time."""
        return sorted(self.scheduled_slots, key=lambda s: s.start_time)

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


def get_or_create_owner(vault: dict, owner_name: str, contact_info: str = "") -> Owner:
    """
    Get an existing owner from the vault or create a new one if it doesn't exist.

    Args:
        vault: Dictionary serving as the object vault (e.g., st.session_state)
        owner_name: The name of the owner to look up or create
        contact_info: Contact info for new owners (optional)

    Returns:
        An Owner instance, either existing or newly created
    """
    owners_key = "owners_vault"

    if owners_key not in vault:
        vault[owners_key] = {}

    owners = vault[owners_key]

    if owner_name in owners:
        return owners[owner_name]

    new_owner = Owner(name=owner_name, contact_info=contact_info)
    owners[owner_name] = new_owner
    return new_owner


def get_or_create_pet(vault: dict, pet_name: str, breed: str = "", age: int = 0, sex: str = "") -> Pet:
    """
    Get an existing pet from the vault or create a new one if it doesn't exist.

    Args:
        vault: Dictionary serving as the object vault (e.g., st.session_state)
        pet_name: The name of the pet to look up or create
        breed: Breed of the pet (optional, for new pets)
        age: Age of the pet (optional, for new pets)
        sex: Sex of the pet (optional, for new pets)

    Returns:
        A Pet instance, either existing or newly created
    """
    pets_key = "pets_vault"

    if pets_key not in vault:
        vault[pets_key] = {}

    pets = vault[pets_key]

    if pet_name in pets:
        return pets[pet_name]

    new_pet = Pet(name=pet_name, breed=breed, age=age, sex=sex)
    pets[pet_name] = new_pet
    return new_pet


def get_or_create_task(vault: dict, task_description: str, duration: int = 0, frequency: str = "") -> Task:
    """
    Get an existing task from the vault or create a new one if it doesn't exist.

    Args:
        vault: Dictionary serving as the object vault (e.g., st.session_state)
        task_description: The description of the task to look up or create
        duration: Duration in minutes (optional, for new tasks)
        frequency: Frequency of the task (optional, for new tasks)

    Returns:
        A Task instance, either existing or newly created
    """
    tasks_key = "tasks_vault"

    if tasks_key not in vault:
        vault[tasks_key] = {}

    tasks = vault[tasks_key]

    if task_description in tasks:
        return tasks[task_description]

    new_task = Task(description=task_description, duration=duration, frequency=frequency)
    tasks[task_description] = new_task
    return new_task


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

    def filter_tasks(self, pet_name: Optional[str] = None, include_completed: bool = False) -> List[Task]:
        """Return a filtered list of tasks.

        Args:
            pet_name: Optional pet name to filter tasks by owner pet.
            include_completed: If False, only pending tasks are returned.

        Returns:
            A list of Task objects matching the filter criteria.
        """
        filtered_tasks = [task for task in self.tasks if include_completed or not task.completion_status]
        if pet_name:
            filtered_tasks = [task for task in filtered_tasks if task.pet and task.pet.name == pet_name]
        return filtered_tasks

    def organize_tasks(self, pet_name: Optional[str] = None, include_completed: bool = False) -> List[Task]:
        """Order tasks by completion, recurrence, and scheduled time.

        This method prepares task ordering for scheduling by:
        - keeping pending tasks before completed tasks,
        - preferring recurring tasks before one-off tasks,
        - sorting by task time and preferred time slot.
        """
        tasks_to_organize = self.filter_tasks(pet_name=pet_name, include_completed=include_completed)
        return sorted(
            tasks_to_organize,
            key=lambda task: (
                task.completion_status,
                not task.is_recurring(),
                task.time or datetime.max,
                task.preferred_time_slot,
            ),
        )

    def sort_by_time(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Sort tasks by their scheduled time, placing unscheduled tasks last."""
        tasks_to_sort = tasks if tasks is not None else self.tasks
        return sorted(
            tasks_to_sort,
            key=lambda task: task.time or datetime.max,
        )

    def _parse_preferred_start(self, task: Task) -> Optional[datetime]:
        """Extract the start time from a preferred_time_slot string."""
        if not task.preferred_time_slot:
            return None

        try:
            start_str = task.preferred_time_slot.split("-")[0]
            hours, minutes = map(int, start_str.split(":"))
            return datetime(date.today().year, date.today().month, date.today().day, hours, minutes)
        except ValueError:
            return None

    def _get_next_recurring_time(self, task: Task) -> datetime:
        """Compute the next date/time for a recurring task based on its frequency."""
        if task.time:
            next_time = task.time
        else:
            next_time = self._parse_preferred_start(task) or datetime.combine(date.today(), datetime.min.time()).replace(hour=9)

        now = datetime.now()
        if next_time < now:
            if task.frequency.lower() == "daily":
                while next_time < now:
                    next_time += timedelta(days=1)
            elif task.frequency.lower() == "weekly":
                while next_time < now:
                    next_time += timedelta(weeks=1)
            elif task.frequency.lower() == "monthly":
                while next_time < now:
                    next_time += timedelta(days=30)
        return next_time

    def _has_conflict(self, start_time: datetime, end_time: datetime, plan: Schedule, task: Optional[Task] = None) -> bool:
        """Return True if the proposed slot overlaps with conflicting scheduled slots.

        If a task is provided and has a pet, conflicts are limited to slots for
        the same pet. Otherwise, any overlapping slot is considered a conflict.
        """
        def overlaps(slot: ScheduledSlot) -> bool:
            return not (slot.end_time <= start_time or slot.start_time >= end_time)

        if task and task.pet:
            return any(
                overlaps(slot) and slot.task and slot.task.pet and slot.task.pet.name == task.pet.name
                for slot in plan.scheduled_slots
            )

        return any(overlaps(slot) for slot in plan.scheduled_slots)

    def _is_within_availability(self, start_time: datetime, end_time: datetime) -> bool:
        """Check if a time slot falls within the owner's availability window."""
        if not self.availability:
            return True

        start_hour, start_min = start_time.hour, start_time.minute
        end_hour, end_min = end_time.hour, end_time.minute

        for avail_window in self.availability:
            try:
                start_str, end_str = avail_window.split("-")
                # Parse start time
                start_parts = start_str.replace("am", "").replace("pm", "").replace(":", "").strip()
                start_is_pm = "pm" in start_str.lower()
                avail_start_hour = int(start_parts.split(":")[0] if ":" in start_str else start_parts[:len(start_parts)-1] if len(start_parts) > 2 else start_parts)
                if start_is_pm and avail_start_hour != 12:
                    avail_start_hour += 12
                elif not start_is_pm and avail_start_hour == 12:
                    avail_start_hour = 0

                # Parse end time
                end_parts = end_str.replace("am", "").replace("pm", "").replace(":", "").strip()
                end_is_pm = "pm" in end_str.lower()
                avail_end_hour = int(end_parts.split(":")[0] if ":" in end_str else end_parts[:len(end_parts)-1] if len(end_parts) > 2 else end_parts)
                if end_is_pm and avail_end_hour != 12:
                    avail_end_hour += 12
                elif not end_is_pm and avail_end_hour == 12:
                    avail_end_hour = 0

                # Check if slot is within this availability window
                if start_hour >= avail_start_hour and end_hour <= avail_end_hour:
                    return True
            except (ValueError, IndexError):
                continue

        return False

    def _find_non_conflicting_slot(self, task: Task, start_time: datetime, end_time: datetime, plan: Schedule) -> Optional[tuple[datetime, datetime]]:
        """Find the nearest available slot around a requested time.

        The search looks forward and backward in 15-minute increments up to two
        hours from the requested start time, respecting availability constraints.
        """
        if not self._has_conflict(start_time, end_time, plan, task) and self._is_within_availability(start_time, end_time):
            return start_time, end_time

        duration = end_time - start_time
        search_window = 120
        for offset in range(15, search_window + 1, 15):
            for delta in (timedelta(minutes=offset), timedelta(minutes=-offset)):
                candidate_start = start_time + delta
                candidate_end = candidate_start + duration
                if candidate_start.date() != start_time.date():
                    continue
                if not self._has_conflict(candidate_start, candidate_end, plan, task) and self._is_within_availability(candidate_start, candidate_end):
                    return candidate_start, candidate_end

        return None

    def next_available_slot(self, duration_minutes: int, earliest: Optional[datetime] = None, pet_name: Optional[str] = None, search_days: int = 7) -> Optional[tuple[datetime, datetime]]:
        """Find the next available time slot for a given duration.

        Args:
            duration_minutes: Length of desired slot in minutes.
            earliest: Earliest datetime to consider. Defaults to now.
            pet_name: If provided, ensure no conflicts for this pet.
            search_days: How many days ahead to search.

        Returns:
            A tuple (start_datetime, end_datetime) for the next free slot, or None if not found.
        """
        if earliest is None:
            earliest = datetime.now()

        # Build or refresh a current plan to check conflicts against
        plan = self.scheduled_plan or self.schedule()

        # Create a lightweight dummy task to use pet-scoped conflict checks
        dummy_pet = None
        if pet_name:
            for p in self.pets:
                if p.name == pet_name:
                    dummy_pet = p
                    break

        class _DummyTask:
            def __init__(self, pet):
                self.pet = pet

        dummy_task = _DummyTask(dummy_pet)

        duration = timedelta(minutes=duration_minutes)

        # Parse availability windows if present. Expect strings like '09:00-17:00'
        availability_windows = []
        for a in (self.availability or []):
            try:
                start_s, end_s = a.split("-")
                sh, sm = map(int, start_s.split(":"))
                eh, em = map(int, end_s.split(":"))
                availability_windows.append((sh, sm, eh, em))
            except Exception:
                continue

        # If no availability provided, allow day windows from 08:00-20:00
        if not availability_windows:
            availability_windows = [(8, 0, 20, 0)]

        # Align search to next quarter-hour
        minute = (earliest.minute // 15) * 15
        current = earliest.replace(minute=minute, second=0, microsecond=0)
        if current < earliest:
            current += timedelta(minutes=15)

        end_search = current + timedelta(days=search_days)

        while current <= end_search:
            # For each day's availability window, construct candidate starts
            for (sh, sm, eh, em) in availability_windows:
                window_start = current.replace(hour=sh, minute=sm, second=0, microsecond=0)
                window_end = current.replace(hour=eh, minute=em, second=0, microsecond=0)

                # If window_end before window_start (overnight), skip that window for simplicity
                if window_end <= window_start:
                    continue

                candidate = max(current, window_start)
                # Step through window in 15-minute increments
                while candidate + duration <= window_end:
                    candidate_end = candidate + duration
                    if not self._has_conflict(candidate, candidate_end, plan, task=dummy_task):
                        return candidate, candidate_end
                    candidate += timedelta(minutes=15)

            # Move to next day at the same aligned minute
            current = (current + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

        return None

    def schedule(self, pet_name: Optional[str] = None, include_completed: bool = False) -> Schedule:
        """Generate a daily schedule of pet tasks for the owner.

        Tasks are retrieved, ordered, and placed into slots. If a task cannot
        be scheduled because of a same-pet conflict or no available nearby slot,
        it is added to unmet_tasks and a warning is recorded.
        """
        self.tasks = self.retrieve_tasks()
        organized_tasks = self.organize_tasks(pet_name=pet_name, include_completed=include_completed)
        plan = Schedule(owner=self.owner, availability=self.availability)

        for task in organized_tasks:
            if task.is_recurring():
                task.time = self._get_next_recurring_time(task)

            if task.scheduled_start and task.scheduled_end:
                start_time, end_time = task.scheduled_start, task.scheduled_end
            elif task.time:
                start_time = task.time
                end_time = task.time + timedelta(minutes=task.duration)
            else:
                plan.unmet_tasks.append(task)
                continue

            # If there's already a slot with the exact same start time for the same pet,
            # treat this as an unrecoverable conflict: leave the existing slot and mark
            # this task as unmet with a warning (do not auto-reschedule).
            if task.pet and any(
                slot.start_time == start_time and slot.task and slot.task.pet and slot.task.pet.name == task.pet.name
                for slot in plan.scheduled_slots
            ):
                # Attempt to chain after the conflicting slot with a 10-minute buffer
                conflicting_slots = [
                    slot for slot in plan.scheduled_slots
                    if slot.start_time == start_time and slot.task and slot.task.pet and slot.task.pet.name == task.pet.name
                ]
                conflicting_slot = max(conflicting_slots, key=lambda s: s.end_time) if conflicting_slots else None
                buffer_minutes = 10
                if conflicting_slot:
                    candidate_start = conflicting_slot.end_time + timedelta(minutes=buffer_minutes)
                    candidate_end = candidate_start + (end_time - start_time)
                    chained_match = self._find_non_conflicting_slot(task, candidate_start, candidate_end, plan)
                    if chained_match:
                        chained_start, chained_end = chained_match
                        task.schedule(chained_start, chained_end)
                        plan.add_scheduled_task_entry(task, chained_start, chained_end)
                        continue

                # If chaining failed, mark unmet and warn
                plan.unmet_tasks.append(task)
                pet_name = task.pet.name if task.pet else "Unknown Pet"
                time_str = start_time.strftime("%Y-%m-%d %H:%M") if start_time else "unspecified"
                plan.warnings.append(
                    f"Exact-start conflict: could not schedule '{task.description}' for {pet_name} at {time_str}; another task already starts then."
                )
                continue

            match = self._find_non_conflicting_slot(task, start_time, end_time, plan)
            if match:
                scheduled_start, scheduled_end = match
                task.schedule(scheduled_start, scheduled_end)
                plan.add_scheduled_task_entry(task, scheduled_start, scheduled_end)
            else:
                plan.unmet_tasks.append(task)
                # Add a lightweight, human-readable warning rather than raising
                pet_name = task.pet.name if task.pet else "Unknown Pet"
                time_str = start_time.strftime("%Y-%m-%d %H:%M") if start_time else "unspecified"
                plan.warnings.append(
                    f"Could not schedule '{task.description}' for {pet_name} at {time_str}; no non-conflicting slot found."
                )

        self.scheduled_plan = plan
        return plan

    def manage_task(self, task: Task) -> None:
        """Update or reschedule a specific task."""
        if task not in self.tasks:
            self.tasks.append(task)

    def explain_decision(self, slot: ScheduledSlot) -> str:
        """Explain the reasoning for a scheduling decision."""
        return slot.explanation or "Scheduled to fit owner availability and pet needs."
