"""
pawpal_system.py — PawPal+ logic layer
All backend classes live here. app.py imports from this file.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Optional


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
    DUPLICATE_TASK = "duplicate_task"
    TIME_LIMIT_EXCEEDED = "time_limit_exceeded"
    BUDGET_EXCEEDED = "budget_exceeded"


class DeleteScope(Enum):
    """Controls how far a delete reaches when removing a recurring task."""
    THIS_EVENT_ONLY = "this_event_only"
    THIS_AND_FUTURE = "this_and_future"
    ALL_EVENTS = "all_events"


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
    frequency: str = ""
    start_time: str = ""
    location: str = ""
    cost: float = 0.0
    notes: str = ""
    is_complete: bool = False
    extra_pets: list[Pet] = field(default_factory=list, repr=False)

    def __post_init__(self) -> None:
        self.name = self.name.strip()

    def get_full_name(self) -> str:
        """Return a display name combining the category and task name."""
        return f"{self.category.value.capitalize()}: {self.name}"

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.is_complete = True

    def edit(
        self,
        name: Optional[str] = None,
        duration_minutes: Optional[int] = None,
        priority: Optional[Priority] = None,
        start_time: Optional[str] = None,
        cost: Optional[float] = None,
    ) -> None:
        """Update whichever fields are provided; leave the rest unchanged."""
        if name is not None:
            self.name = name.strip()
        if duration_minutes is not None:
            self.duration_minutes = duration_minutes
        if priority is not None:
            self.priority = priority
        if start_time is not None:
            self.start_time = start_time
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
    gender: str = "unknown"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    notes: str = ""
    _tasks: list[Task] = field(default_factory=list, repr=False)

    def get_full_name(self) -> str:
        """Return the pet's full name."""
        return f"{self.first_name} {self.last_name}"

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet."""
        self._tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove the task with the given id from this pet's list."""
        self._tasks = [t for t in self._tasks if t.id != task_id]

    def get_tasks(self) -> list[Task]:
        """Return all tasks assigned to this pet."""
        return list(self._tasks)


@dataclass
class Owner:
    """
    The person using the app. Stores their name, how many minutes
    they have free each day, and their max daily spending limit.
    Everything in the system flows from the owner — they hold the list of pets.
    """
    first_name: str
    last_name: str
    available_minutes_per_day: int
    max_daily_budget: float
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    _pets: list[Pet] = field(default_factory=list, repr=False)

    def get_full_name(self) -> str:
        """Return the owner's full name."""
        return f"{self.first_name} {self.last_name}"

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list."""
        self._pets.append(pet)

    def remove_pet(self, pet_id: str) -> None:
        """Remove the pet with the given id from this owner's list."""
        self._pets = [p for p in self._pets if p.id != pet_id]

    def get_pets(self) -> list[Pet]:
        """Return all pets belonging to this owner."""
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
    time_slot: str
    why_chosen: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    extra_pets: list[Pet] = field(default_factory=list, repr=False)

    def get_all_pets(self) -> list[Pet]:
        """Return the primary pet plus any extra pets sharing this task."""
        return [self.pet] + self.extra_pets

    def summarize(self) -> str:
        """Return a one-line description of this schedule entry, listing all pets."""
        status = "✓" if self.task.is_complete else "○"
        pet_names = " & ".join(p.get_full_name() for p in self.get_all_pets())
        return (
            f"{self.order}. [{status}] {self.time_slot} — "
            f"{self.task.get_full_name()} for {pet_names} "
            f"({self.task.duration_minutes} min, ${self.task.cost:.2f})"
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
        """Return a plain-English suggestion for resolving this conflict."""
        if self.conflict_type == ConflictType.TIME_OVERLAP:
            names = " and ".join(i.task.get_full_name() for i in self.involved_items)
            return (
                f"Reschedule one of the overlapping tasks ({names}) to a different "
                f"time slot, or shorten its duration."
            )
        if self.conflict_type == ConflictType.LOCATION_CLASH:
            names = " and ".join(i.task.get_full_name() for i in self.involved_items)
            return (
                f"Tasks {names} share the same time slot but require different "
                f"locations. Move one of them to an earlier or later slot."
            )
        if self.conflict_type == ConflictType.DUPLICATE_TASK:
            names = " and ".join(i.task.get_full_name() for i in self.involved_items)
            return (
                f"Duplicate task detected ({names}). Remove one occurrence or "
                f"adjust its recurrence settings."
            )
        if self.conflict_type == ConflictType.TIME_LIMIT_EXCEEDED:
            return (
                "Increase your available minutes per day in Owner Settings, "
                "or reduce the duration of this task."
            )
        if self.conflict_type == ConflictType.BUDGET_EXCEEDED:
            return (
                "Increase your daily budget in Owner Settings, "
                "or reduce the cost of this task."
            )
        return "Review the conflicting items and adjust the schedule manually."


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
        """Append a ScheduleItem to this schedule."""
        self.items.append(item)

    def get_total_duration(self) -> int:
        """Return the sum of all task durations in minutes."""
        return sum(item.task.duration_minutes for item in self.items)

    def get_total_cost(self) -> float:
        """Return the total cost of all scheduled tasks."""
        return sum(item.task.cost for item in self.items)

    def has_conflicts(self) -> bool:
        """Return True if any conflicts were detected."""
        return len(self.conflicts) > 0

    def sort_by_time(self) -> list[ScheduleItem]:
        """Return items sorted by time slot (earliest first)."""
        return sorted(self.items, key=lambda i: i.time_slot)

    def sort_by_priority(self) -> list[ScheduleItem]:
        """Return items sorted by priority (High → Medium → Low)."""
        return sorted(self.items, key=lambda i: _PRIORITY_ORDER[i.task.priority.value])

    def display(self) -> str:
        """Return a formatted plain-text view of the full daily schedule."""
        lines = [
            f"=== PawPal+ Schedule for {self.date} ===",
            "",
        ]
        if not self.items:
            lines.append("No tasks scheduled for today.")
        else:
            for item in self.items:
                lines.append(item.summarize())
        lines += [
            "",
            f"Total time : {self.get_total_duration()} min",
            f"Total cost : ${self.get_total_cost():.2f}",
        ]
        if self.has_conflicts():
            lines += ["", "--- Conflicts ---"]
            for conflict in self.conflicts:
                lines.append(f"  [{conflict.conflict_type.value}] {conflict.message}")
                lines.append(f"  Fix: {conflict.suggest_fix()}")
        if self.reasoning:
            lines += ["", "--- Reasoning ---", self.reasoning]
        return "\n".join(lines)


class TaskManager:
    """
    Handles editing and deleting tasks, with support for recurring tasks.
    When a task repeats, the caller picks a scope (this one, this and future,
    or all occurrences) and TaskManager applies the change to the right subset.
    Recurring tasks are linked by a shared recurrence_group_id.
    """

    def __init__(self, tasks: list[Task]) -> None:
        self._tasks = tasks

    def _find(self, task_id: str) -> Optional[Task]:
        for t in self._tasks:
            if t.id == task_id:
                return t
        return None

    def _group_members(self, recurrence_group_id: str) -> list[Task]:
        return [t for t in self._tasks if t.recurrence_group_id == recurrence_group_id]

    def delete_single(self, task_id: str) -> None:
        """Remove exactly the one task with this id."""
        task = self._find(task_id)
        if task:
            self._tasks.remove(task)

    def delete_this_and_future(self, task_id: str) -> None:
        """Remove the specified task and all later tasks sharing its recurrence group."""
        task = self._find(task_id)
        if task is None:
            return
        if task.recurrence_group_id is None:
            self._tasks.remove(task)
            return
        target_index = self._tasks.index(task)
        to_remove = [
            t for i, t in enumerate(self._tasks)
            if t.recurrence_group_id == task.recurrence_group_id and i >= target_index
        ]
        for t in to_remove:
            self._tasks.remove(t)

    def delete_all_recurring(self, recurrence_group_id: str) -> None:
        """Remove every task that belongs to the given recurrence group."""
        to_remove = self._group_members(recurrence_group_id)
        for t in to_remove:
            self._tasks.remove(t)

    def edit_single(self, task_id: str, changes: dict) -> None:
        """Apply changes to exactly the one task with this id."""
        task = self._find(task_id)
        if task:
            task.edit(**changes)

    def edit_this_and_future(self, task_id: str, changes: dict) -> None:
        """Apply changes to the specified task and all later tasks in its recurrence group."""
        task = self._find(task_id)
        if task is None:
            return
        if task.recurrence_group_id is None:
            task.edit(**changes)
            return
        target_index = self._tasks.index(task)
        for i, t in enumerate(self._tasks):
            if t.recurrence_group_id == task.recurrence_group_id and i >= target_index:
                t.edit(**changes)

    def edit_all_recurring(self, recurrence_group_id: str, changes: dict) -> None:
        """Apply changes to every task in the given recurrence group."""
        for t in self._group_members(recurrence_group_id):
            t.edit(**changes)


# Default start times assigned per task category.
_CATEGORY_TIME_SLOTS: dict[TaskCategory, str] = {
    TaskCategory.MEDICATION:  "07:00",
    TaskCategory.FEEDING:     "08:00",
    TaskCategory.WALK:        "09:00",
    TaskCategory.VET:         "10:00",
    TaskCategory.GROOMING:    "11:00",
    TaskCategory.OTHER:       "13:00",
    TaskCategory.ENRICHMENT:  "15:00",
}

_PRIORITY_ORDER: dict[str, int] = {
    "high":   0,
    "medium": 1,
    "low":    2,
}


class Scheduler:
    """
    The brain of the app. Takes an Owner (and their pets + tasks) and produces
    a Schedule for the day. It sorts tasks by priority, trims anything that
    won't fit in the available time or budget, assigns time slots based on
    task category, detects conflicts, and writes a plain-English explanation
    of every decision it made.
    """

    def generate_plan(self, owner: Owner) -> Schedule:
        """Collect, rank, filter, and slot all pet tasks into a Schedule for today."""
        today = date.today()
        schedule = Schedule(date=today)
        reasoning_parts: list[str] = []

        pet_task_pairs: list[tuple[Pet, Task]] = []
        for pet in owner.get_pets():
            for task in pet.get_tasks():
                if not task.is_complete:
                    pet_task_pairs.append((pet, task))

        reasoning_parts.append(
            f"Collected {len(pet_task_pairs)} incomplete task(s) across "
            f"{len(owner.get_pets())} pet(s)."
        )

        pet_task_pairs.sort(key=lambda pt: _PRIORITY_ORDER[pt[1].priority.value])
        reasoning_parts.append("Sorted tasks by priority (High → Medium → Low).")

        task_to_pet = {t.id: p for p, t in pet_task_pairs}
        all_tasks = [t for _, t in pet_task_pairs]
        kept_tasks = set(t.id for t in self.fit_to_time(all_tasks, owner.available_minutes_per_day))
        dropped_time = [t for t in all_tasks if t.id not in kept_tasks]
        time_conflicts: list[ScheduleConflict] = []
        if dropped_time:
            names = ", ".join(t.get_full_name() for t in dropped_time)
            reasoning_parts.append(
                f"Dropped {len(dropped_time)} task(s) that exceeded the "
                f"{owner.available_minutes_per_day}-minute daily limit: {names}."
            )
            for task in dropped_time:
                pet = task_to_pet[task.id]
                time_conflicts.append(ScheduleConflict(
                    conflict_type=ConflictType.TIME_LIMIT_EXCEEDED,
                    message=(
                        f"'{task.get_full_name()}' for {pet.get_full_name()} "
                        f"({task.duration_minutes} min) was dropped — your "
                        f"{owner.available_minutes_per_day}-min daily limit was reached."
                    ),
                ))
        pet_task_pairs = [(p, t) for p, t in pet_task_pairs if t.id in kept_tasks]

        remaining_tasks = [t for _, t in pet_task_pairs]
        kept_tasks = set(t.id for t in self.fit_to_budget(remaining_tasks, owner.max_daily_budget))
        dropped_budget = [t for t in remaining_tasks if t.id not in kept_tasks]
        budget_conflicts: list[ScheduleConflict] = []
        if dropped_budget:
            names = ", ".join(t.get_full_name() for t in dropped_budget)
            reasoning_parts.append(
                f"Dropped {len(dropped_budget)} task(s) that exceeded the "
                f"${owner.max_daily_budget:.2f} daily budget: {names}."
            )
            for task in dropped_budget:
                pet = task_to_pet[task.id]
                budget_conflicts.append(ScheduleConflict(
                    conflict_type=ConflictType.BUDGET_EXCEEDED,
                    message=(
                        f"'{task.get_full_name()}' for {pet.get_full_name()} "
                        f"(${task.cost:.2f}) was dropped — your "
                        f"${owner.max_daily_budget:.2f} daily budget was reached."
                    ),
                ))
        pet_task_pairs = [(p, t) for p, t in pet_task_pairs if t.id in kept_tasks]

        for order, (pet, task) in enumerate(pet_task_pairs, start=1):
            start = task.start_time if task.start_time else _CATEGORY_TIME_SLOTS.get(task.category, "12:00")
            try:
                end_dt = datetime.strptime(start, "%H:%M") + timedelta(minutes=task.duration_minutes)
                time_slot = f"{start} – {end_dt.strftime('%H:%M')}"
            except ValueError:
                time_slot = start
            all_pets = [pet] + task.extra_pets
            pet_names = " & ".join(p.get_full_name() for p in all_pets)
            why = (
                f"Included as a {task.priority.value}-priority "
                f"{task.category.value} task for {pet_names}."
            )
            item = ScheduleItem(
                task=task,
                pet=pet,
                order=order,
                time_slot=time_slot,
                why_chosen=why,
                extra_pets=task.extra_pets,
            )
            schedule.add_item(item)
            if task.extra_pets:
                reasoning_parts.append(
                    f"'{task.get_full_name()}' is a shared task for {pet_names}."
                )

        conflicts = self.detect_conflicts(schedule) + time_conflicts + budget_conflicts
        schedule.conflicts = conflicts
        if conflicts:
            reasoning_parts.append(
                f"Detected {len(conflicts)} conflict(s): "
                + "; ".join(c.message for c in conflicts)
            )

        schedule.reasoning = self.explain_reasoning(schedule)
        schedule.reasoning = "\n".join(reasoning_parts) + "\n\n" + schedule.reasoning

        return schedule

    def rank_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted from highest to lowest priority."""
        return sorted(tasks, key=lambda t: _PRIORITY_ORDER[t.priority.value])

    def fit_to_time(self, tasks: list[Task], available_minutes: int) -> list[Task]:
        """Return the highest-priority tasks that fit within the available minutes."""
        ranked = self.rank_by_priority(tasks)
        kept: list[Task] = []
        used = 0
        for task in ranked:
            if used + task.duration_minutes <= available_minutes:
                kept.append(task)
                used += task.duration_minutes
        return kept

    def fit_to_budget(self, tasks: list[Task], max_budget: float) -> list[Task]:
        """Return the highest-priority tasks whose total cost fits within the budget."""
        ranked = self.rank_by_priority(tasks)
        kept: list[Task] = []
        spent = 0.0
        for task in ranked:
            if spent + task.cost <= max_budget:
                kept.append(task)
                spent += task.cost
        return kept

    @staticmethod
    def _parse_slot(time_slot: str) -> tuple[datetime, datetime] | None:
        """Return (start, end) datetimes from a 'HH:MM – HH:MM' slot string, or None if unparseable."""
        try:
            parts = time_slot.split("–")
            start = datetime.strptime(parts[0].strip(), "%H:%M")
            end = datetime.strptime(parts[1].strip(), "%H:%M")
            return start, end
        except (ValueError, IndexError):
            return None

    def detect_conflicts(self, schedule: Schedule) -> list[ScheduleConflict]:
        """Scan the schedule and return all time overlaps and duplicate tasks."""
        conflicts: list[ScheduleConflict] = []

        items = schedule.items
        reported: set[frozenset[str]] = set()

        for i, a in enumerate(items):
            range_a = self._parse_slot(a.time_slot)
            if range_a is None:
                continue
            for b in items[i + 1:]:
                range_b = self._parse_slot(b.time_slot)
                if range_b is None:
                    continue
                a_start, a_end = range_a
                b_start, b_end = range_b
                if a_start < b_end and b_start < a_end:
                    pair = frozenset([a.id, b.id])
                    if pair not in reported:
                        reported.add(pair)
                        conflicts.append(ScheduleConflict(
                            conflict_type=ConflictType.TIME_OVERLAP,
                            message=(
                                f"'{a.task.get_full_name()}' ({a.time_slot}) and "
                                f"'{b.task.get_full_name()}' ({b.time_slot}) overlap."
                            ),
                            involved_items=[a, b],
                        ))

        # Same (pet, task name) pair appearing more than once is a duplicate.
        seen: dict[tuple[str, str], ScheduleItem] = {}
        for item in schedule.items:
            key = (item.pet.id, item.task.name.lower())
            if key in seen:
                conflicts.append(ScheduleConflict(
                    conflict_type=ConflictType.DUPLICATE_TASK,
                    message=(
                        f"'{item.task.name}' appears more than once for "
                        f"{item.pet.get_full_name()}."
                    ),
                    involved_items=[seen[key], item],
                ))
            else:
                seen[key] = item

        return conflicts

    def resolve_conflict(self, conflict: ScheduleConflict) -> ScheduleItem:
        """Return the highest-priority item from the conflict to keep."""
        return min(
            conflict.involved_items,
            key=lambda i: _PRIORITY_ORDER[i.task.priority.value],
        )

    def explain_reasoning(self, schedule: Schedule) -> str:
        """Return a plain-English summary of the schedule's task count, time, cost, and conflicts."""
        count = len(schedule.items)
        duration = schedule.get_total_duration()
        cost = schedule.get_total_cost()

        if count == 0:
            return "No tasks were scheduled for today."

        lines = [
            f"The plan for {schedule.date} includes {count} task(s) "
            f"totalling {duration} minute(s) and ${cost:.2f}."
        ]

        if schedule.items:
            high = [i for i in schedule.items if i.task.priority == Priority.HIGH]
            if high:
                names = ", ".join(i.task.get_full_name() for i in high)
                lines.append(f"High-priority tasks scheduled first: {names}.")

        if schedule.has_conflicts():
            lines.append(
                f"{len(schedule.conflicts)} conflict(s) were detected. "
                "Review the conflicts section for suggested fixes."
            )
        else:
            lines.append("No conflicts were detected.")

        return " ".join(lines)
