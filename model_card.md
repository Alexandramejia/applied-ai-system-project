# Model Card — PawPal+

## Reliability and Evaluation

### Automated Tests

Tests are in `tests/test_pawpal.py` and run with `pytest`. They cover task completion, task count, sort order by time and priority, conflict detection, and end-to-end schedule generation.

**Result:** 6 out of 6 tests passed. The trickiest case was cross-pet conflict detection — a bug only caught because the test forced the scheduler to handle two pets at once.

**Example test run:**

```
$ python -m pytest tests/ -v
============================= test session starts ==============================
tests/test_pawpal.py::test_mark_complete                          PASSED
tests/test_pawpal.py::test_add_task_increases_count               PASSED
tests/test_pawpal.py::test_sort_by_time                           PASSED
tests/test_pawpal.py::test_sort_by_priority                       PASSED
tests/test_pawpal.py::test_conflict_detected_for_same_time_slot   PASSED
tests/test_pawpal.py::test_scheduler_generates_items_for_owner_with_pet_and_task PASSED
============================== 6 passed in 0.18s ===============================
```

### Logging and Error Handling

The Gemini API call in `ai_service.py` is wrapped in a `try/except` block — if it fails for any reason, the system falls back to a rule-based summary so the schedule always displays. The scheduler also catches `ValueError` when parsing user-entered time strings, so a badly formatted start time skips cleanly instead of crashing.

**Example guardrail — bad time string input:**

If a user enters a time like `"nine am"` instead of `"09:00"`, the scheduler catches the `ValueError` and skips that task rather than crashing:

```
ValueError: time data 'nine am' does not match format '%H:%M' — task skipped, schedule continues.
```

---

## Reflection and Ethics

### Limitations and Biases

- **No multi-pet scheduling in one session.** You can't build separate schedules for two pets at the same time. To schedule a second pet, you have to finish the first pet's tasks, delete them, and then add the second pet's tasks — there's no way to view both schedules side by side.
- **No true simultaneous tasks.** If you want to feed two pets at the same time, entering two tasks at the same slot triggers a false conflict. The workaround (`extra_pets`) isn't obvious from the UI.
- **First-pet bias.** When tasks share the same priority, whichever pet was added first always gets scheduled first — not based on urgency, just entry order.
- **Silent task drops.** If the scheduler cuts a task due to the time or budget limit, the AI summary will note that conflicts exist but won't name which tasks were dropped or why. The reasoning log (shown below the schedule in the UI) is the only place that gives that detail.

### Potential Misuse and Prevention

PawPal+ is low-risk — no shared data, no external accounts, no persistent storage. The main risk is trusting the AI summary without checking whether tasks were quietly dropped. The reasoning log is shown in the UI to address this. The API key is stored in `.env` and never hardcoded.

### What Surprised Me During Testing

What surprised me most was how many edge cases and constraints you have to consider when building a scheduling system. I kept discovering new scenarios — like what happens when two pets have tasks at the same time, or when a task gets skipped because the owner's time budget runs out — that I hadn't thought about until the tests exposed them. It made me realize that even a small system has a lot of moving parts that can break in unexpected ways.

### AI Collaboration

Throughout the project I used AI (Claude) at several stages: prompting it to help design the data model (how `Owner`, `Pet`, `Task`, and `Schedule` should relate), asking it to suggest test cases I might have missed, and using it to debug why `detect_conflicts` was returning duplicate entries. I also used it to review my Gemini prompt wording in `ai_service.py` to make the output sound more natural and less robotic. AI was most useful as a sounding board — I'd describe a design decision, it would push back or offer alternatives, and I'd decide whether the suggestion actually fit my existing code.

**Helpful:** The AI suggested using a `frozenset` of item IDs to deduplicate conflict pairs — without it, two overlapping tasks would have produced duplicate conflict entries from both scan directions.

**Flawed:** When extending the scheduler for multiple pets, the AI generated a `PetScheduler` subclass that merged results from the parent's `generate_plan`. That was unnecessary — the existing `Scheduler` already loops over all pets in one pass. I kept the original design and fixed the loop instead.

### Future Improvements

- Allow two pets to share a time slot with a user-defined flag instead of requiring the `extra_pets` workaround.
- Add a task check-off feature so owners can mark tasks as done throughout the day and track what's still left.
- Allow each pet to have its own separate schedule displayed at the same time, so an owner with multiple pets doesn't have to share one combined schedule — they could view and manage each pet's day independently.
- Add the ability to save and reload past schedules so owners can reuse a routine without re-entering tasks every time.
