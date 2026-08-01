"""
PawPal+ Care Agent
An agentic workflow system that intelligently manages pet care scheduling.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Tuple
from pawpal_system import Owner, Pet, Task, Schedule, Scheduler, ScheduledSlot


@dataclass
class AgentDecision:
    """Represents a decision made by the agent with reasoning."""
    action: str
    task: Optional[Task] = None
    reasoning: str = ""
    confidence: float = 0.95
    alternative_actions: List[str] = field(default_factory=list)


@dataclass
class AgentMemory:
    """Tracks agent decisions and patterns for learning."""
    past_decisions: List[Dict] = field(default_factory=list)
    owner_preferences: Dict = field(default_factory=dict)
    pet_patterns: Dict = field(default_factory=dict)
    conflict_history: List[str] = field(default_factory=list)


class CareAgent:
    """
    An intelligent agent that autonomously manages pet care scheduling.

    The agent acts as the decision-making layer between the UI and the scheduling system,
    providing intelligent recommendations and autonomous scheduling decisions.
    """

    def __init__(self, owner: Owner, scheduler: Optional[Scheduler] = None):
        """Initialize the care agent with an owner and optional scheduler."""
        self.owner = owner
        self.scheduler = scheduler or Scheduler(owner=owner)
        self.memory = AgentMemory()
        self.current_plan: Optional[Schedule] = None
        self.last_recommendation: Optional[str] = None

    def analyze_scheduling_needs(self) -> Dict:
        """
        Analyze the owner's pet care needs and constraints.

        Returns:
            Dict with analysis of tasks, pets, availability, and conflicts.
        """
        analysis = {
            "total_pets": len(self.owner.pets),
            "total_tasks": len(self.owner.tasks),
            "available_hours": self._parse_availability(),
            "recurring_tasks": sum(1 for t in self.owner.tasks if t.is_recurring()),
            "one_time_tasks": sum(1 for t in self.owner.tasks if not t.is_recurring()),
            "pet_health_considerations": self._identify_health_needs(),
        }
        return analysis

    def generate_intelligent_schedule(self) -> Schedule:
        """
        Generate an optimized schedule using intelligent decision-making.

        Returns:
            A Schedule with optimized task placement and explanations.
        """
        # Step 1: Analyze current state
        analysis = self.analyze_scheduling_needs()

        # Step 2: Generate base schedule
        schedule = self.scheduler.schedule()
        self.current_plan = schedule

        # Step 3: Attempt to resolve conflicts intelligently
        if schedule.unmet_tasks:
            schedule = self._resolve_conflicts_intelligently(schedule)

        # Step 4: Add explanations to scheduled slots
        schedule = self._add_slot_explanations(schedule)

        # Step 5: Generate recommendations
        self.last_recommendation = self._generate_recommendations(schedule, analysis)

        return schedule

    def get_scheduling_recommendation(self, task: Task) -> str:
        """
        Get an intelligent recommendation for scheduling a specific task.

        Args:
            task: The task to recommend scheduling for.

        Returns:
            A recommendation string with reasoning.
        """
        if not self.current_plan:
            self.generate_intelligent_schedule()

        if task in self.current_plan.unmet_tasks:
            suggestion = self.scheduler.next_available_slot(
                duration_minutes=task.duration,
                pet_name=task.pet.name if task.pet else None,
                search_days=7
            )

            if suggestion:
                start, end = suggestion
                reason = self._explain_recommendation(task, start, end)
                self.memory.past_decisions.append({
                    "task": task.description,
                    "suggested_time": start.isoformat(),
                    "reason": reason,
                    "timestamp": datetime.now().isoformat()
                })
                return reason
            else:
                return f"No available slot found for '{task.description}' in the next 7 days. Consider extending availability or rescheduling other tasks."
        else:
            # Task is already scheduled
            for slot in self.current_plan.scheduled_slots:
                if slot.task == task:
                    return f"Already scheduled: {slot.start_time.strftime('%I:%M %p')} - {slot.end_time.strftime('%I:%M %p')}"

        return "Task status unknown."

    def adapt_to_changes(self, changes: Dict) -> str:
        """
        Adapt the schedule based on changes (availability, new tasks, pet health, etc.).

        Args:
            changes: Dict with keys like 'new_availability', 'new_task', 'pet_health_update', etc.

        Returns:
            A message describing the adaptation and its impact.
        """
        adaptations = []

        if "new_availability" in changes:
            self.owner.set_availability(changes["new_availability"])
            adaptations.append(f"✓ Updated availability to: {', '.join(changes['new_availability'])}")
            self.scheduler.availability = changes["new_availability"]

        if "new_task" in changes:
            task_data = changes["new_task"]
            new_task = Task(
                description=task_data["description"],
                duration=task_data.get("duration", 30),
                frequency=task_data.get("frequency", "one-time"),
                pet=task_data.get("pet")
            )
            if new_task.pet:
                self.owner.create_task(new_task.pet, new_task)
            adaptations.append(f"✓ Added new task: '{task_data['description']}'")

        if "pet_health_update" in changes:
            health_info = changes["pet_health_update"]
            pet_name = health_info.get("pet_name")
            condition = health_info.get("condition")
            pet = next((p for p in self.owner.pets if p.name == pet_name), None)
            if pet and condition:
                pet.health_conditions.append(condition)
                adaptations.append(f"✓ Recorded health condition for {pet_name}: {condition}")
                self.memory.pet_patterns[pet_name] = condition

        if "task_time_update" in changes:
            update_info = changes["task_time_update"]
            pet_name = update_info.get("pet_name")
            task_description = update_info.get("description")
            preferred_time_slot = update_info.get("preferred_time_slot")
            new_duration = update_info.get("new_duration")

            task = None
            for pet in self.owner.pets:
                if pet.name == pet_name:
                    task = next((t for t in pet.tasks if t.description == task_description), None)
                    break

            if task:
                if preferred_time_slot:
                    task.preferred_time_slot = preferred_time_slot
                    adaptations.append(f"✓ Updated preferred time slot for '{task_description}' to {preferred_time_slot}")
                if new_duration:
                    task.duration = new_duration
                    adaptations.append(f"✓ Updated duration for '{task_description}' to {new_duration} minutes")

        # Regenerate schedule after adaptations
        new_schedule = self.generate_intelligent_schedule()

        impact_summary = self._summarize_schedule_impact(self.current_plan, new_schedule)

        return "\n".join(adaptations) + "\n\nSchedule Impact:\n" + impact_summary

    def explain_decision(self, slot: ScheduledSlot) -> str:
        """
        Explain why a particular task was scheduled at a specific time.

        Args:
            slot: The scheduled slot to explain.

        Returns:
            A human-readable explanation of the scheduling decision.
        """
        task = slot.task
        pet_name = task.pet.name if task.pet else "Unknown"
        duration = task.duration

        reasons = [
            f"Task: {task.description} ({duration} min) for {pet_name}",
            f"Scheduled: {slot.start_time.strftime('%I:%M %p')} - {slot.end_time.strftime('%I:%M %p')}",
        ]

        if task.frequency:
            reasons.append(f"Frequency: {task.frequency}")

        if slot.explanation:
            reasons.append(f"Decision: {slot.explanation}")

        # Add constraint-based reasoning
        if task.preferred_time_slot:
            reasons.append(f"Preferred slot: {task.preferred_time_slot}")

        return " | ".join(reasons)

    # ============ Private Helper Methods ============

    def _parse_availability(self) -> float:
        """Parse availability strings and return total available hours."""
        total_hours = 0
        for avail in self.owner.availability:
            try:
                start_str, end_str = avail.split("-")
                # Handle both "8am" and "8:00" formats
                if "am" in start_str.lower() or "pm" in start_str.lower():
                    # Parse "8am" or "8pm" format
                    start_hour = int(''.join(filter(str.isdigit, start_str.split(":")[0])))
                    if "pm" in start_str.lower() and start_hour != 12:
                        start_hour += 12
                    elif "am" in start_str.lower() and start_hour == 12:
                        start_hour = 0

                    end_hour = int(''.join(filter(str.isdigit, end_str.split(":")[0])))
                    if "pm" in end_str.lower() and end_hour != 12:
                        end_hour += 12
                    elif "am" in end_str.lower() and end_hour == 12:
                        end_hour = 0
                else:
                    # Parse "8:00" format
                    start_hour = int(start_str.split(":")[0])
                    end_hour = int(end_str.split(":")[0])

                total_hours += (end_hour - start_hour)
            except (ValueError, AttributeError, IndexError):
                pass
        return total_hours

    def _identify_health_needs(self) -> Dict:
        """Identify health considerations that impact scheduling."""
        health_needs = {}
        for pet in self.owner.pets:
            if pet.health_conditions or pet.medications:
                health_needs[pet.name] = {
                    "conditions": pet.health_conditions,
                    "medications": pet.medications,
                }
        return health_needs

    def _resolve_conflicts_intelligently(self, schedule: Schedule) -> Schedule:
        """Attempt to resolve unmet tasks through intelligent rescheduling."""
        unmet = list(schedule.unmet_tasks)

        for task in unmet:
            # Try to find next available slot
            suggestion = self.scheduler.next_available_slot(
                duration_minutes=task.duration,
                pet_name=task.pet.name if task.pet else None,
                search_days=7
            )

            if suggestion:
                start, end = suggestion
                # Check if this can be added without new conflicts
                if not self.scheduler._has_conflict(start, end, schedule, task):
                    task.schedule(start, end)
                    schedule.add_scheduled_task_entry(task, start, end)
                    schedule.unmet_tasks.remove(task)
                    schedule.warnings.append(
                        f"Auto-resolved '{task.description}' to {start.strftime('%I:%M %p')} (original slot unavailable)"
                    )

        return schedule

    def _add_slot_explanations(self, schedule: Schedule) -> Schedule:
        """Add intelligent explanations to each scheduled slot."""
        for slot in schedule.scheduled_slots:
            if not slot.explanation:
                slot.explanation = self._generate_slot_explanation(slot)
        return schedule

    def _generate_slot_explanation(self, slot: ScheduledSlot) -> str:
        """Generate an explanation for why a task is scheduled at a specific time."""
        task = slot.task
        pet_name = task.pet.name if task.pet else "Your pet"

        explanations = [
            f"Scheduled to fit {pet_name}'s needs",
            f"Placed within owner availability window",
            f"Ordered by priority and recurrence",
        ]

        if task.is_recurring():
            explanations.append(f"Next occurrence of recurring task")

        return " → ".join(explanations)

    def _generate_recommendations(self, schedule: Schedule, analysis: Dict) -> str:
        """Generate smart recommendations based on schedule and analysis."""
        recommendations = []

        # Check for overbooked schedule
        total_scheduled_mins = sum(
            (slot.end_time - slot.start_time).total_seconds() / 60
            for slot in schedule.scheduled_slots
        )
        available_mins = analysis["available_hours"] * 60

        utilization = (total_scheduled_mins / available_mins * 100) if available_mins > 0 else 0

        if utilization > 80:
            recommendations.append(
                f"⚠️ High utilization ({utilization:.0f}% of available time). "
                "Consider extending availability or consolidating tasks."
            )
        elif utilization > 60:
            recommendations.append(
                f"✓ Good schedule balance ({utilization:.0f}% utilization). "
                "Schedule is healthy but room for flexibility."
            )

        # Check for pet-specific needs
        for pet in self.owner.pets:
            if pet.health_conditions:
                recommendations.append(
                    f"💊 {pet.name} has health considerations. Review task timing for medication/vet requirements."
                )

        # Check for conflict patterns
        if len(schedule.unmet_tasks) > 2:
            recommendations.append(
                f"📅 Multiple unmet tasks ({len(schedule.unmet_tasks)}). "
                "Suggest extending availability or prioritizing critical tasks."
            )

        return "\n".join(recommendations) if recommendations else "✓ Schedule is optimal for current setup."

    def _explain_recommendation(self, task: Task, start: datetime, end: datetime) -> str:
        """Explain why a specific time slot is recommended for a task."""
        pet_name = task.pet.name if task.pet else "Your pet"
        day_name = start.strftime("%A")
        time_range = f"{start.strftime('%I:%M %p')} - {end.strftime('%I:%M %p')}"

        explanation = f"Next available slot for '{task.description}' ({task.duration} min) is {day_name} at {time_range}."
        explanation += f" This fits {pet_name}'s schedule and owner availability."

        return explanation

    def _summarize_schedule_impact(self, old_schedule: Optional[Schedule], new_schedule: Schedule) -> str:
        """Summarize how schedule changed due to adaptations."""
        if not old_schedule:
            return f"Generated new schedule with {len(new_schedule.scheduled_slots)} tasks."

        old_count = len(old_schedule.scheduled_slots)
        new_count = len(new_schedule.scheduled_slots)
        old_unmet = len(old_schedule.unmet_tasks)
        new_unmet = len(new_schedule.unmet_tasks)

        changes = []
        if new_count > old_count:
            changes.append(f"+{new_count - old_count} newly scheduled tasks")
        elif new_count < old_count:
            changes.append(f"-{old_count - new_count} tasks rescheduled")

        if new_unmet < old_unmet:
            changes.append(f"✓ Resolved {old_unmet - new_unmet} unmet task(s)")
        elif new_unmet > old_unmet:
            changes.append(f"⚠️ {new_unmet - old_unmet} new unmet task(s)")

        return " | ".join(changes) if changes else "Schedule remains unchanged."
