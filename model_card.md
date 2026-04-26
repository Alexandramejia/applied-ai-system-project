# Model Card — PawPal+

## Reliability and Evaluation

### Automated Tests

Tests are in `tests/test_pawpal.py` and run with `pytest`. They cover task completion, task count, sort order by time, sort order by priority, conflict detection, and end-to-end schedule generation.

**Result:** 6 out of 6 tests passed. The system handled all core scheduling behaviors correctly. The trickiest case was cross-pet conflict detection — a bug only caught because the test forced the scheduler to handle two pets at once.

---

### Logging and Error Handling

The Gemini API call in `ai_service.py` is wrapped in a `try/except` block. If the call fails for any reason — missing key, network error, bad response — the exception is caught and the system falls back to a rule-based summary built from the Python data directly. The schedule always displays; the app never crashes due to an AI failure.

The scheduler also catches `ValueError` when parsing user-entered time strings, so a badly formatted start time skips cleanly instead of breaking the schedule build.

---

