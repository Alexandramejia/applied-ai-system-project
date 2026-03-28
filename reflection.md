# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did 
you assign to each?

PawPal is a pet care scheduling system. The Owner who has one or more Pets. Each pet has a list of care Tasks: walks, feeding, medication, or grooming. A Scheduler reads all of that information and builds a Schedule, which is the owner's daily plan.

Classes and Responsibilities: 

Owner stores the person's name, email, how many minutes they have available in a day, and their maximum daily spending limit. Everything in the system flows from the owner.

Pet stores the animal's basic profile — name, species, breed, age, and notes. Each pet holds its own list of tasks.

Task represents one care activity. It stores what the task is, how long it takes, how important it is, where it happens, how much it costs, and whether it repeats on a schedule.

TaskManager is responsible for editing and deleting tasks. When a task repeats, it asks the owner whether they want to change just that one occurrence, that one and everything after it, or every instance of it.

Scheduler is the brain of the app. It takes the owner's pets and tasks, sorts them by priority, checks that everything fits within the available time and budget, spots any conflicts, and produces the final plan with an explanation of its decisions.

Schedule is the finished daily plan. It holds the list of scheduled items in order, the total time, the total cost for the day, and any problems that were found.

ScheduleItem is one entry in the schedule — it records which task, which pet, what time, and why that task was included in the plan.

ScheduleConflict captures when something goes wrong in the plan — for example two tasks at the same time, or tasks that exceed the owner's budget — and suggests what the owner can do to fix it.

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

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
