# Model Card — PawPal+

## Reliability and Evaluation

### Automated Tests

Tests are in `tests/test_pawpal.py` and run with `pytest`. They cover task completion, task count, sort order by time and priority, conflict detection, and end-to-end schedule generation.

**Result:** 6 out of 6 tests passed. The trickiest case was cross-pet conflict detection — a bug only caught because the test forced the scheduler to handle two pets at once.

### Logging and Error Handling

The Gemini API call in `ai_service.py` is wrapped in a `try/except` block — if it fails for any reason, the system falls back to a rule-based summary so the schedule always displays. The scheduler also catches `ValueError` when parsing user-entered time strings, so a badly formatted start time skips cleanly instead of crashing.

---

## Reflection and Ethics

### Limitations and Biases

- **Partial overlaps aren't caught.** The conflict detector only flags tasks at the exact same time slot. A task ending at 9:30 AM and another starting at 9:15 AM won't trigger a warning.
- **No true simultaneous tasks.** If you want to feed two pets at the same time, entering two tasks at the same slot triggers a false conflict. The workaround (`extra_pets`) isn't obvious from the UI.
- **First-pet bias.** When tasks share the same priority, whichever pet was added first always gets scheduled first — not based on urgency, just entry order.
- **Silent task drops.** If the scheduler cuts a task due to the time or budget limit, the AI summary won't mention it — it will sound like everything was handled.

### Potential Misuse and Prevention

PawPal+ is low-risk — no shared data, no external accounts, no persistent storage. The main risk is trusting the AI summary without checking whether tasks were quietly dropped. The reasoning log is shown in the UI to address this. The API key is stored in `.env` and never hardcoded.

### What Surprised Me During Testing

The end-to-end test broke twice during development — once when I removed an email field from `Owner`, and once when I changed `generate_plan` to skip completed tasks but forgot to mark the test task as incomplete. Both times the test caught the regression before I ran the app.

### AI Collaboration

**Helpful:** The AI suggested using a `frozenset` of item IDs to deduplicate conflict pairs — without it, two overlapping tasks would have produced duplicate conflict entries from both scan directions.

**Flawed:** When extending the scheduler for multiple pets, the AI generated a `PetScheduler` subclass that merged results from the parent's `generate_plan`. That was unnecessary — the existing `Scheduler` already loops over all pets in one pass. I kept the original design and fixed the loop instead.
