# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did 
you assign to each?

PawPal is a pet care scheduling system where an Owner has one or more Pets. Each pet has a list of care Tasks such as walks, feeding, medication, or grooming. A Scheduler reads all of that information and builds a Schedule, which represents the owner's daily plan.

Classes and Responsibilities :

The Owner stores the person's name, email, available minutes per day, and maximum daily budget. Everything in the system flows from the owner.

The Pet stores the animal’s basic profile — name, species, breed, age, and notes. Each pet maintains its own list of tasks.

The Task represents one care activity. It stores what the task is, how long it takes, how important it is, where it happens, how much it costs, and whether it repeats.

The TaskManager handles editing and deleting tasks, including recurring ones. It allows the user to choose whether to modify one instance, future instances, or all occurrences.

The Scheduler is the main logic of the system. It collects all tasks, sorts them by priority, ensures they fit within time and budget constraints, detects conflicts, and builds the final plan with reasoning.

The Schedule represents the final daily plan. It contains the ordered tasks, total time, total cost, and any detected issues.

A ScheduleItem represents one entry in the schedule, including the task, pet, time slot, and reasoning.

A ScheduleConflict represents issues in the plan, such as overlapping tasks or duplicate tasks, and suggests how to fix them.


### Initial UML Design

PawPal is a pet care scheduling system. The design starts with an Owner who has one or more Pets. Each pet has a list of care Tasks — things like walks, feeding, medication, or grooming. A Scheduler reads all of that information and builds a Schedule, to plan out the owner's daily plan.

### Classes & Responsibilities
Owner stores the person's name, email, how many minutes they have available in a day, and their maximum daily spending limit. Everything in the system flows from the owner.

Pet stores the animal's basic profile — name, species, breed, age, and notes. Each pet holds its own list of tasks.

Task represents one care activity. It stores what the task is, how long it takes, how important it is, where it happens, how much it costs, and whether it repeats on a schedule.

TaskManager is responsible for editing and deleting tasks. When a task repeats, it asks the owner whether they want to change just that one occurrence, that one and everything after it, or every instance of it.

Scheduler is the brain of the app. It takes the owner's pets and tasks, sorts them by priority, checks that everything fits within the available time and budget, spots any conflicts, and produces the final plan with an explanation of its decisions.

Schedule is the finished daily plan. It holds the list of scheduled items in order, the total time, the total cost for the day, and any problems that were found.

ScheduleItem is one entry in the schedule — it records which task, which pet, what time, and why that task was included in the plan.

ScheduleConflict captures when something goes wrong in the plan — for example two tasks at the same time, or tasks that exceed the owner's budget — and suggests what the owner can do to fix it.

### Enumerations
Rather than letting users type anything freely, four fixed lists keep the data consistent. Priority is always High, Medium, or Low. Task category is always one of Walk, Feeding, Medication, Enrichment, Grooming, Vet, or Other. Conflict type describes what kind of problem was detected. Delete scope describes how far a deletion should reach when removing a recurring task.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Initially, I included OVER_TIME_BUDGET and OVER_COST_BUDGET as conflict types. However, I removed them because the scheduler already filters tasks using fit_to_time and fit_to_budget. Since tasks that exceed limits are removed before the schedule is created, these conflicts became unnecessary.

Another change was adding support for shared tasks. Instead of creating a new class, I added an extra_pets field to the Task class. This allows one task to apply to multiple pets, such as walking two dogs together. The Scheduler then includes all pets when building the schedule. This approach kept the design simple while still adding useful functionality.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

My scheduler considers a few main constraints: the total time available in a day, the priority of each task, and the cost of tasks. It also only includes tasks that are not completed.

The most important constraint is priority, because high-priority tasks should always be completed first. After that, the scheduler checks if tasks fit within the available time and budget.

I chose these constraints because in real life, a pet owner would want to make sure essential tasks like feeding or medication are done first. The time and budget limits help ensure the schedule is realistic and manageable.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

One tradeoff my scheduler makes is that it keeps the logic simple instead of being super accurate or complex. For example, when I added sorting by time, it just sorts based on the "HH:MM" string instead of calculating real time overlaps or durations.

Also, the conflict detection only checks if tasks have the exact same time slot, not if they partially overlap. This makes it easier to understand and faster to run, but it might miss some more complicated scheduling conflicts.

This tradeoff is reasonable because the goal of the app is to help a busy pet owner quickly organize their day, not create a perfect real-world calendar system. Keeping the logic simple makes the app easier to build, easier to read, and less likely to break, while still being useful for basic planning.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used AI to really explain what was going on in my code so I could get a better understanding of how everything worked. I would often ask AI to break things down step by step, and then explain it back in my own words to make sure I actually understood it. This helped me not just copy code, but learn what it was doing and why. The most helpful prompts were when I asked AI to explain logic in simple terms or to walk through how different parts of my system connected.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

There were also moments where I did not fully accept AI suggestions. Sometimes AI would give solutions that were too complex or added unnecessary features, including creating too many extra functions that were not really needed. This made the code harder to follow and more complicated than it had to be. Because of that, I simplified the solutions to better match my design. This helped me stay in control of the project and keep the system clean and readable.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I tested the main behaviors of my system, including sorting tasks by time and priority, detecting conflicts when tasks have the same time slot, and making sure the scheduler generates a schedule when tasks are added. I also tested smaller features like marking tasks as complete and adding tasks to pets.

These tests were important because they verify that the core logic of my system works correctly. Since the scheduler is the “brain” of the app, I needed to make sure it was producing correct and consistent results before relying on the UI.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I am somewhat confident that my scheduler works correctly because all of my tests passed successfully. However, I am not fully confident because this is my first time relying heavily on AI to build a larger project, so there may still be cases I did not think about.

If I had more time, I would test more complex scenarios, such as handling many tasks at once or testing how the system behaves under different combinations of time and budget constraints.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I am most satisfied with how the scheduler organizes tasks for the owner. It clearly shows what needs to be done and lays everything out in a structured way for the day. I think this makes the system useful and practical for managing pet care, especially for someone with a busy schedule.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

If I had another iteration, I would improve how I approached the development process. I did not like that I was working on multiple steps at the same time. I prefer to focus on one task at a time and build gradually. Because of that, I sometimes added features that were not necessary and ended up removing them later. Next time, I would plan more carefully and keep the implementation more focused.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

One important thing I learned is that even when using AI, I still need to guide the design and make decisions about what to include. AI can generate a lot of code quickly, but it can also overcomplicate things or add unnecessary features. I learned how to simplify solutions and stay in control of the system design, which helped me better understand how everything works together.

