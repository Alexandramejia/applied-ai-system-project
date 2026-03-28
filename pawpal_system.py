"""
pawpal_system.py — PawPal+ logic layer
All backend classes live here. app.py imports from this file.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class Priority(Enum):
    """How urgent a task is. Used to rank tasks when the schedule can't fit everything."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskCategory(Enum):
    """The type of care activity. Used to assign a sensible default time slot in the schedule."""
    WALK = "walk"
    FEEDING = "feeding"
    MEDICATION = "medication"
    ENRICHMENT = "enrichment"
    GROOMING = "grooming"
    VET = "vet"
    OTHER = "other"


class ConflictType(Enum):
    """Labels what kind of problem was found in a schedule so the right fix can be suggested."""
    TIME_OVERLAP = "time_overlap"
    LOCATION_CLASH = "location_clash"
    OVER_TIME_BUDGET = "over_time_budget"
    OVER_COST_BUDGET = "over_cost_budget"
    DUPLICATE_TASK = "duplicate_task"


class DeleteScope(Enum):
    """Controls how far a delete reaches when removing a recurring task."""
    THIS_EVENT_ONLY = "this_event_only"
    THIS_AND_FUTURE = "this_and_future"
    ALL_EVENTS = "all_events"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Task:
    """
    One care activity for a pet — e.g. a walk, feeding, or vet visit.
    Stores what the task is, how long it takes, how important it is,
    where it happens, what it costs, and whether it repeats.
    """
    name: str
    category: TaskCategory
    priority: Priority
    duration_minutes: int
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    recurrence_group_id: Optional[str] = None
    is_recurring: bool = False
    frequency: str = ""          # e.g. "daily", "weekly"
    location: str = ""
    cost: float = 0.0
    notes: str = ""
    is_complete: bool = False

    def get_full_name(self) -> str:
        return f"{self.name} ({self.category.value})"

    def mark_complete(self) -> None:
        self.is_complete = True

    def edit(
        self,
        name: Optional[str] = None,
        duration_minutes: Optional[int] = None,
        priority: Optional[Priority] = None,
        location: Optional[str] = None,
        cost: Optional[float] = None,
    ) -> None:
        if name is not None:
            self.name = name
        if duration_minutes is not None:
            self.duration_minutes = duration_minutes
        if priority is not None:
            self.priority = priority
        if location is not None:
            self.location = location
        if cost is not None:
            self.cost = cost


@dataclass
class Pet:
    """
    A pet profile. Holds the animal's basic info (name, species, breed, age)
    and owns the list of care tasks assigned to it.
    """
    first_name: str
    last_name: str
    species: str
    breed: str
    age: int
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    notes: str = ""
    _tasks: list[Task] = field(default_factory=list, repr=False)

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def add_task(self, task: Task) -> None:
        self._tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        self._tasks = [t for t in self._tasks if t.id != task_id]

    def get_tasks(self) -> list[Task]:
        return list(self._tasks)


@dataclass
class Owner:
    """
    The person using the app. Stores their name, email, how many minutes
    they have free each day, and their max daily spending limit.
    Everything in the system flows from the owner — they hold the list of pets.
    """
    first_name: str
    last_name: str
    email: str
    available_minutes_per_day: int
    max_daily_budget: float
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    _pets: list[Pet] = field(default_factory=list, repr=False)

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def add_pet(self, pet: Pet) -> None:
        self._pets.append(pet)

    def remove_pet(self, pet_id: str) -> None:
        self._pets = [p for p in self._pets if p.id != pet_id]

    def get_pets(self) -> list[Pet]:
        return list(self._pets)


@dataclass
class ScheduleItem:
    """
    One entry in the daily schedule. Records which task, which pet,
    what position it falls in, what time it starts, and why it was included.
    """
    task: Task
    pet: Pet
    order: int
    time_slot: str        # e.g. "9:00 AM"
    why_chosen: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def summarize(self) -> str:
        return (
            f"{self.order}. [{self.time_slot}] {self.task.name} "
            f"for {self.pet.get_full_name()} "
            f"({self.task.duration_minutes} min, ${self.task.cost:.2f}) — {self.why_chosen}"
        )


@dataclass
class ScheduleConflict:
    """
    Captures a problem found in the schedule — e.g. the tasks exceed the time
    or cost budget, or there is a duplicate. Each conflict includes a message
    describing what went wrong and a suggested fix.
    """
    conflict_type: ConflictType
    message: str
    involved_items: list[ScheduleItem] = field(default_factory=list)

    def suggest_fix(self) -> str:
        fixes = {
            ConflictType.TIME_OVERLAP: "Shift one task to a different time slot.",
            ConflictType.LOCATION_CLASH: "Reorder tasks so location changes are minimised.",
            ConflictType.OVER_TIME_BUDGET: "Remove lowest-priority tasks to fit within available time.",
            ConflictType.OVER_COST_BUDGET: "Remove highest-cost tasks or replace with free alternatives.",
            ConflictType.DUPLICATE_TASK: "Remove the duplicate task entry.",
        }
        return fixes.get(self.conflict_type, "Review the schedule manually.")


@dataclass
class Schedule:
    """
    The finished daily plan. Holds the ordered list of ScheduleItems,
    any conflicts that were detected, the total time and cost, and a
    plain-English explanation of how the plan was built.
    """
    date: date
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    reasoning: str = ""
    items: list[ScheduleItem] = field(default_factory=list)
    conflicts: list[ScheduleConflict] = field(default_factory=list)

    def add_item(self, item: ScheduleItem) -> None:
        self.items.append(item)

    def get_total_duration(self) -> int:
        return sum(i.task.duration_minutes for i in self.items)

    def get_total_cost(self) -> float:
        return sum(i.task.cost for i in self.items)

    def has_conflicts(self) -> bool:
        return len(self.conflicts) > 0

    def display(self) -> str:
        lines = [
            f"Schedule for {self.date}",
            f"Total time: {self.get_total_duration()} min | Total cost: ${self.get_total_cost():.2f}",
            "",
        ]
        for item in self.items:
            lines.append(item.summarize())
        if self.conflicts:
            lines.append("\nConflicts:")
            for c in self.conflicts:
                lines.append(f"  [{c.conflict_type.value}] {c.message}")
                lines.append(f"    Fix: {c.suggest_fix()}")
        if self.reasoning:
            lines.append(f"\nReasoning: {self.reasoning}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# TaskManager — edit and delete tasks with recurring-scope support
# ---------------------------------------------------------------------------

class TaskManager:
    """
    Handles editing and deleting tasks, with support for recurring tasks.
    When a task repeats, the caller picks a scope (this one, this and future,
    or all occurrences) and TaskManager applies the change to the right subset.
    Recurring tasks are linked by a shared recurrence_group_id.
    """

    def _all_tasks(self, owner: Owner) -> list[tuple[Pet, Task]]:
        pairs = []
        for pet in owner.get_pets():
            for task in pet.get_tasks():
                pairs.append((pet, task))
        return pairs

    # --- Delete ---

    def delete_single(self, owner: Owner, task_id: str) -> None:
        for pet in owner.get_pets():
            pet.remove_task(task_id)

    def delete_this_and_future(self, owner: Owner, task_id: str) -> None:
        all_tasks = self._all_tasks(owner)
        # Find the target task and its recurrence group
        target = next((t for _, t in all_tasks if t.id == task_id), None)
        if target is None or not target.recurrence_group_id:
            self.delete_single(owner, task_id)
            return
        # Collect group tasks; those at or after the target index are removed
        group = [(p, t) for p, t in all_tasks if t.recurrence_group_id == target.recurrence_group_id]
        target_index = next(i for i, (_, t) in enumerate(group) if t.id == task_id)
        for pet, task in group[target_index:]:
            pet.remove_task(task.id)

    def delete_all_recurring(self, owner: Owner, recurrence_group_id: str) -> None:
        for pet in owner.get_pets():
            ids_to_remove = [t.id for t in pet.get_tasks() if t.recurrence_group_id == recurrence_group_id]
            for tid in ids_to_remove:
                pet.remove_task(tid)

    # --- Edit ---

    def edit_single(self, owner: Owner, task_id: str, changes: dict) -> None:
        for _, task in self._all_tasks(owner):
            if task.id == task_id:
                task.edit(**changes)
                return

    def edit_this_and_future(self, owner: Owner, task_id: str, changes: dict) -> None:
        all_tasks = self._all_tasks(owner)
        target = next((t for _, t in all_tasks if t.id == task_id), None)
        if target is None or not target.recurrence_group_id:
            self.edit_single(owner, task_id, changes)
            return
        group = [t for _, t in all_tasks if t.recurrence_group_id == target.recurrence_group_id]
        target_index = next(i for i, t in enumerate(group) if t.id == task_id)
        for task in group[target_index:]:
            task.edit(**changes)

    def edit_all_recurring(self, owner: Owner, recurrence_group_id: str, changes: dict) -> None:
        for _, task in self._all_tasks(owner):
            if task.recurrence_group_id == recurrence_group_id:
                task.edit(**changes)


# ---------------------------------------------------------------------------
# Scheduler — builds a daily Schedule from an Owner's pets and tasks
# ---------------------------------------------------------------------------

_PRIORITY_ORDER = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}

# Rough start time by task category (24-hour clock, minutes from midnight)
_CATEGORY_START = {
    TaskCategory.FEEDING:    7 * 60,
    TaskCategory.MEDICATION: 8 * 60,
    TaskCategory.WALK:       9 * 60,
    TaskCategory.VET:        10 * 60,
    TaskCategory.GROOMING:   11 * 60,
    TaskCategory.ENRICHMENT: 14 * 60,
    TaskCategory.OTHER:      15 * 60,
}


def _minutes_to_time_slot(minutes: int) -> str:
    h, m = divmod(minutes, 60)
    suffix = "AM" if h < 12 else "PM"
    h12 = h if 1 <= h <= 12 else (12 if h == 0 else h - 12)
    return f"{h12}:{m:02d} {suffix}"


class Scheduler:
    """
    The brain of the app. Takes an Owner (and their pets + tasks) and produces
    a Schedule for the day. It sorts tasks by priority, trims anything that
    won't fit in the available time or budget, assigns time slots based on
    task category, detects conflicts, and writes a plain-English explanation
    of every decision it made.
    """

    def rank_by_priority(self, tasks: list[Task]) -> list[Task]:
        return sorted(tasks, key=lambda t: _PRIORITY_ORDER[t.priority])

    def fit_to_time(self, tasks: list[Task], available_minutes: int) -> list[Task]:
        selected, total = [], 0
        for task in tasks:
            if total + task.duration_minutes <= available_minutes:
                selected.append(task)
                total += task.duration_minutes
        return selected

    def fit_to_budget(self, tasks: list[Task], max_budget: float) -> list[Task]:
        selected, total = [], 0.0
        for task in tasks:
            if total + task.cost <= max_budget:
                selected.append(task)
                total += task.cost
        return selected

    def detect_conflicts(self, schedule: Schedule, owner: Owner) -> list[ScheduleConflict]:
        conflicts = []

        # Over-time check
        if schedule.get_total_duration() > owner.available_minutes_per_day:
            conflicts.append(ScheduleConflict(
                conflict_type=ConflictType.OVER_TIME_BUDGET,
                message=(
                    f"Schedule needs {schedule.get_total_duration()} min but "
                    f"owner only has {owner.available_minutes_per_day} min."
                ),
                involved_items=list(schedule.items),
            ))

        # Over-budget check
        if schedule.get_total_cost() > owner.max_daily_budget:
            conflicts.append(ScheduleConflict(
                conflict_type=ConflictType.OVER_COST_BUDGET,
                message=(
                    f"Schedule costs ${schedule.get_total_cost():.2f} but "
                    f"daily budget is ${owner.max_daily_budget:.2f}."
                ),
                involved_items=list(schedule.items),
            ))

        # Duplicate task name check
        seen_names: dict[str, ScheduleItem] = {}
        for item in schedule.items:
            key = item.task.name.lower()
            if key in seen_names:
                conflicts.append(ScheduleConflict(
                    conflict_type=ConflictType.DUPLICATE_TASK,
                    message=f"'{item.task.name}' appears more than once in the schedule.",
                    involved_items=[seen_names[key], item],
                ))
            else:
                seen_names[key] = item

        return conflicts

    def resolve_conflict(self, conflict: ScheduleConflict) -> Optional[ScheduleItem]:
        """
        Simple resolution: for over-budget / over-time, drop the last (lowest-priority) item.
        Returns the removed item, or None if nothing to remove.
        """
        if conflict.conflict_type in (ConflictType.OVER_TIME_BUDGET, ConflictType.OVER_COST_BUDGET):
            if conflict.involved_items:
                return conflict.involved_items[-1]
        return None

    def explain_reasoning(self, schedule: Schedule) -> str:
        if not schedule.items:
            return "No tasks were scheduled."
        lines = ["Tasks were selected and ordered as follows:"]
        for item in schedule.items:
            lines.append(f"  • {item.task.name}: {item.why_chosen}")
        return "\n".join(lines)

    def generate_plan(self, owner: Owner, for_date: Optional[date] = None) -> Schedule:
        if for_date is None:
            from datetime import date as _date
            for_date = _date.today()

        # Gather all incomplete tasks across all pets, paired with their pet
        pet_task_pairs: list[tuple[Pet, Task]] = []
        for pet in owner.get_pets():
            for task in pet.get_tasks():
                if not task.is_complete:
                    pet_task_pairs.append((pet, task))

        # Sort by priority
        pet_task_pairs.sort(key=lambda pt: _PRIORITY_ORDER[pt[1].priority])

        # Fit to time budget (priority order so high-priority tasks are kept first)
        selected: list[tuple[Pet, Task]] = []
        total_minutes, total_cost = 0, 0.0
        for pet, task in pet_task_pairs:
            if (total_minutes + task.duration_minutes <= owner.available_minutes_per_day
                    and total_cost + task.cost <= owner.max_daily_budget):
                selected.append((pet, task))
                total_minutes += task.duration_minutes
                total_cost += task.cost

        # Build schedule items with time slots
        schedule = Schedule(date=for_date)
        cursor = 8 * 60  # start at 8:00 AM

        for order, (pet, task) in enumerate(selected, start=1):
            # Use category hint if it's later than the current cursor
            preferred = _CATEGORY_START.get(task.category, cursor)
            start = max(cursor, preferred)
            time_slot = _minutes_to_time_slot(start)
            cursor = start + task.duration_minutes

            why = (
                f"Priority: {task.priority.value}. "
                f"Fits within time ({total_minutes} min used) "
                f"and budget (${total_cost:.2f} used)."
            )
            schedule.add_item(ScheduleItem(
                task=task,
                pet=pet,
                order=order,
                time_slot=time_slot,
                why_chosen=why,
            ))

        # Detect conflicts and attach them
        schedule.conflicts = self.detect_conflicts(schedule, owner)
        schedule.reasoning = self.explain_reasoning(schedule)
        return schedule
