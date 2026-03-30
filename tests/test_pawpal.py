"""
tests/test_pawpal.py — Unit tests for PawPal+ system.
Run with:  python -m pytest tests/
"""

from datetime import date

from pawpal_system import (
    Owner, Pet, Task, TaskCategory, Priority,
    Schedule, ScheduleItem, Scheduler,
)


def test_mark_complete():
    """Verify that calling mark_complete() changes the task's status to True."""
    task = Task("Morning walk", TaskCategory.WALK, Priority.HIGH, 30)
    assert task.is_complete is False
    task.mark_complete()
    assert task.is_complete is True


def test_add_task_increases_count():
    """Verify that adding a task to a Pet increases that pet's task count."""
    pet = Pet("Biscuit", "Rivera", "Dog", "Golden Retriever", 4)
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task("Breakfast", TaskCategory.FEEDING, Priority.HIGH, 10))
    assert len(pet.get_tasks()) == 1


# ---------------------------------------------------------------------------
# Helpers — reusable objects shared across the new tests
# ---------------------------------------------------------------------------

def make_pet():
    return Pet("Mochi", "Smith", "dog", "Mixed", 3)


def make_schedule_with_two_items(time_a, time_b, priority_a, priority_b):
    """Build a Schedule containing two ScheduleItems with the given slots and priorities."""
    pet = make_pet()
    task_a = Task("Walk", TaskCategory.WALK, priority_a, 20)
    task_b = Task("Feeding", TaskCategory.FEEDING, priority_b, 10)
    item_a = ScheduleItem(task=task_a, pet=pet, order=1, time_slot=time_a, why_chosen="test")
    item_b = ScheduleItem(task=task_b, pet=pet, order=2, time_slot=time_b, why_chosen="test")
    schedule = Schedule(date=date.today())
    schedule.add_item(item_a)
    schedule.add_item(item_b)
    return schedule, item_a, item_b


# ---------------------------------------------------------------------------
# New tests
# ---------------------------------------------------------------------------

def test_sort_by_time():
    """sort_by_time returns items in ascending time-slot order."""
    schedule, item_a, item_b = make_schedule_with_two_items(
        "15:00", "07:00", Priority.LOW, Priority.HIGH
    )
    result = schedule.sort_by_time()
    assert result[0].time_slot == "07:00"
    assert result[1].time_slot == "15:00"


def test_sort_by_priority():
    """sort_by_priority returns the High-priority item before the Low-priority item."""
    schedule, item_a, item_b = make_schedule_with_two_items(
        "07:00", "15:00", Priority.LOW, Priority.HIGH
    )
    result = schedule.sort_by_priority()
    assert result[0].task.priority == Priority.HIGH
    assert result[1].task.priority == Priority.LOW


def test_conflict_detected_for_same_time_slot():
    """detect_conflicts flags a TIME_OVERLAP when two tasks share the same time slot."""
    schedule, _, _ = make_schedule_with_two_items(
        "09:00", "09:00", Priority.HIGH, Priority.MEDIUM
    )
    conflicts = Scheduler().detect_conflicts(schedule)
    assert len(conflicts) >= 1
    conflict_types = [c.conflict_type.value for c in conflicts]
    assert "time_overlap" in conflict_types


def test_scheduler_generates_items_for_owner_with_pet_and_task():
    """generate_plan produces at least one ScheduleItem when the owner has a pet with a task."""
    owner = Owner("Jordan", "Smith", "j@example.com", 120, 50.0)
    pet = make_pet()
    pet.add_task(Task("Morning walk", TaskCategory.WALK, Priority.HIGH, 30))
    owner.add_pet(pet)

    schedule = Scheduler().generate_plan(owner)

    assert len(schedule.items) == 1
    assert schedule.items[0].task.name == "Morning walk"
