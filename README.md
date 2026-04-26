# PawPal+

**PawPal+** is an AI-powered pet care scheduling web app built with Streamlit and the Google Gemini API. It helps busy pet owners stay organized by building a prioritized daily care plan for one or more pets — detecting scheduling conflicts, respecting time and budget constraints, and summarizing the plan with an AI-generated message.

---

## Original Project

This project builds on **PawPal+ (Module 2)**, which established the core scheduling system for a single pet owner. The original goal was to let a user enter their pet's care tasks, apply priority and time constraints, and generate a structured daily plan. That version introduced the `Owner`, `Pet`, `Task`, and `Scheduler` classes and connected them to a basic Streamlit UI.

This final version expands on that foundation by adding support for **multiple pets**, **shared tasks across pets**, **AI-generated schedule summaries**, and more robust conflict detection.

---

## Architecture Overview

![System Diagram](assets/Pet%20Task%20Scheduling%20with%20AI-2026-04-18-210124.png)

The diagram shows the full flow of the system. The user starts by entering their pets, tasks, budget, and available time through the Streamlit UI (`app.py`). That input is passed to the `Scheduler`, which collects all tasks, sorts them by priority, filters out anything that exceeds the time or budget limits, and detects any time conflicts. In parallel, the test suite independently checks that the scheduler logic is producing correct results. Once the schedule is built, it is sent to the Gemini AI, which reads it and writes a plain-language summary. The final output shown to the user is the schedule table alongside any conflict warnings. The human then reviews the result — and if changes are needed, they go back into the UI to adjust tasks and re-run the process.

**Key classes:**

| Class | Responsibility |
|---|---|
| `Owner` | Stores owner info and daily time/budget limits |
| `Pet` | Stores pet profile and its list of tasks |
| `Task` | One care activity with duration, priority, cost, and time slot |
| `TaskManager` | Handles editing and deleting tasks, including recurring ones |
| `Scheduler` | Filters, sorts, and builds the daily plan; detects conflicts |
| `Schedule` | The finished daily plan with items, totals, and conflict flags |
| `ScheduleItem` | One entry in the schedule — task, pet, time slot, and reasoning |
| `ScheduleConflict` | Captures a detected conflict and suggests a resolution |

---

## Setup Instructions

**Requirements:** Python 3.10+

**1. Clone the repository and navigate to the project folder:**

```bash
git clone <your-repo-url>
cd applied-ai-system-project
```

**2. Create and activate a virtual environment:**

```bash
python -m venv .venv
source .venv/bin/activate       # macOS/Linux
.venv\Scripts\activate          # Windows
```

**3. Install dependencies:**

```bash
pip install -r requirements.txt
```

**4. Add your Gemini API key:**

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_api_key_here
```

**5. Run the app:**

```bash
streamlit run app.py
```

**6. Run the test suite:**

```bash
python -m pytest tests/
```

---

## Sample Interactions

### Example 1 — Single pet, clean schedule

**Input:**
- Owner: Jordan Smith, 120 min/day, $50 budget
- Pet: Mochi (Mixed breed dog, age 3)
- Tasks added:
  - Walk: Morning walk — High priority, 30 min, 8:00 AM
  - Feeding: Breakfast — High priority, 10 min, 8:35 AM
  - Enrichment: Enrichment puzzle — Medium priority, 20 min, 10:00 AM
  - Walk: Evening walk — Medium priority, 30 min, 5:00 PM

**Output:**

Schedule table (sorted by priority):

| Time | Task | Pet(s) | Min | Cost | Priority |
|---|---|---|---|---|---|
| 8:00 AM – 8:30 AM | Walk: Morning walk | Mochi Smith | 30 | $0.00 | 🟠 high |
| 8:35 AM – 8:45 AM | Feeding: Breakfast | Mochi Smith | 10 | $0.00 | 🟠 high |
| 10:00 AM – 10:20 AM | Enrichment: Enrichment puzzle | Mochi Smith | 20 | $0.00 | 🟡 medium |
| 5:00 PM – 5:30 PM | Walk: Evening walk | Mochi Smith | 30 | $0.00 | 🟡 medium |

AI Summary:
```
Hi Jordan! Here's your custom schedule for Mochi based on your highest
priority tasks and time commitment. Your high-priority tasks — Walk: Morning
walk and Feeding: Breakfast — are set to start the day, making sure Mochi's
essentials are covered first. Walk: Morning walk is your most time-consuming
task at 30 minutes, and your day flows nicely from morning to evening with no
gaps. Have a great day with Mochi!
```

---

### Example 2 — Two pets with a time conflict

**Input:**
- Pet 1: Mochi — Walk: Morning walk at 9:00 AM, 30 min
- Pet 2: Biscuit (Golden Retriever, age 4) — Vet: Vet visit at 9:00 AM, 45 min

**Output:**

The schedule is still generated and displayed, but a conflict banner appears at the top and the details are shown below the table:

```
⚠️ 1 conflict detected — see details below the table.

[Time Overlap]
'Walk: Morning walk' (09:00 – 09:30) and 'Vet: Vet visit' (09:00 – 09:45) overlap.

Suggested fix: Reschedule one of the overlapping tasks (Walk: Morning walk
and Vet: Vet visit) to a different time slot, or shorten its duration.
```

---

### Example 3 — Adding a second pet after the first schedule runs

**Input:**
- Step 1: Add Mochi with three tasks → click Generate Schedule → AI summary appears.
- Step 2: Add Biscuit with two new tasks → app shows "Your pets or tasks changed — regenerate the schedule."
- Step 3: Click Generate Schedule again.

**Output:**

The scheduler re-runs across both pets and produces a combined schedule. Tasks are re-sorted by priority across the full set, and any new conflicts between the two pets are detected and listed. The AI summary refreshes to reflect both pets. This demonstrates that the system correctly re-reads all pet data on each run rather than caching a stale single-pet result.

---

## Design Decisions

**Step-by-step, form-driven UI:**
Rather than accepting all input at once, the app guides the owner through adding pets, then tasks, then generating the schedule. This makes the system easier to customize, easier to debug, and more intuitive to use.

**Priority-first scheduling:**
The scheduler sorts by priority before considering time slots. High-priority tasks (feeding, medication) are always placed first. This reflects real-world pet care needs where some tasks are non-negotiable regardless of when they occur.

**Conflict detection scope:**
The conflict detector flags tasks with the same time slot (exact match). Partial overlaps — where one task ends a few minutes into another — are not currently detected. This is a deliberate simplification: the goal is a practical planning aid, not a strict calendar validator.

**Shared tasks via `extra_pets`:**
Rather than creating a new class for tasks shared across multiple pets (e.g., walking two dogs together), I added an `extra_pets` field to `Task`. This kept the design clean while supporting the feature without over-engineering it.

**AI as a summary layer, not a decision-maker:**
The Gemini API is used only at the end of the pipeline — to narrate the completed schedule in plain language. All scheduling logic (filtering, sorting, conflict detection) happens in deterministic Python code, which makes the system testable and predictable.

---

## Testing Summary

Tests are in [tests/test_pawpal.py](tests/test_pawpal.py) and cover:

- `test_mark_complete` — Verifies a task's status flips correctly when marked done.
- `test_add_task_increases_count` — Confirms a pet's task list grows when a task is added.
- `test_sort_by_time` — Checks that schedule items are returned in ascending time order.
- `test_sort_by_priority` — Checks that high-priority items come before low-priority ones.
- `test_conflict_detected_for_same_time_slot` — Verifies a `TIME_OVERLAP` conflict is raised when two tasks share a slot.
- `test_scheduler_generates_items_for_owner_with_pet_and_task` — End-to-end check that the scheduler produces a valid plan.

All six tests passed. The biggest lesson from testing was how important edge cases are. When I introduced a second pet, I had to ensure the scheduler re-read both pets' tasks and correctly detected cross-pet conflicts — behavior that hadn't been considered in the original single-pet design. Catching this through testing rather than in production was a clear example of why thorough test coverage matters.

---

## Reflection

This project taught me that building an AI system is less about writing one clever function and more about carefully managing the relationships between many small pieces. Every class has to behave predictably on its own, and then the connections between them have to be just as deliberate. This is also why edge cases matter since they expose where those relationships break down.

Working with AI tools during development reinforced that lesson. AI can generate code quickly, but it can also overcomplicate things, like adding functions and edge cases that weren't needed and making the system harder to follow. I learned to use AI as a collaborator I could interrogate and simplify, not a source of final answers. Asking it to explain code step by step, then restating that explanation in my own words, helped me stay in genuine control of the design. The biggest shift in my thinking was realizing that clarity and simplicity are features — a scheduler that handles the real use case cleanly is more valuable than one that handles every hypothetical case messily.
