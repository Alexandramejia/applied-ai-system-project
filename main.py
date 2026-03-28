"""
main.py — Demo script for PawPal+ system.
"""

from pawpal_system import Owner, Pet, Task, TaskCategory, Priority, Scheduler

# Create owner
owner = Owner("Jake", "Rivera", "jake@example.com", available_minutes_per_day=180, max_daily_budget=200.0)

# Create two pets
dog = Pet("Biscuit", "Rivera", "Dog", "Golden Retriever", 4)
cat = Pet("Mochi", "Rivera", "Cat", "Siamese", 2)

# Add tasks with different durations
dog.add_task(Task("Morning walk", TaskCategory.WALK, Priority.HIGH, duration_minutes=30, cost=0.0))
dog.add_task(Task("Breakfast", TaskCategory.FEEDING, Priority.HIGH, duration_minutes=10, cost=3.50))
cat.add_task(Task("Grooming session", TaskCategory.GROOMING, Priority.LOW, duration_minutes=45, cost=25.00))

owner.add_pet(dog)
owner.add_pet(cat)

# Generate and print today's schedule
schedule = Scheduler().generate_plan(owner)
print(schedule.display())
