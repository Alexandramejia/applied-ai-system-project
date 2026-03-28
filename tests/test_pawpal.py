"""
tests/test_pawpal.py — Unit tests for PawPal+ system.
Run with:  python -m pytest tests/
"""

from pawpal_system import Pet, Task, TaskCategory, Priority


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
