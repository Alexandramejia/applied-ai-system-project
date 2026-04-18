"""
ai_service.py — Gemini-powered friendly schedule summary for PawPal+
"""

import os

from dotenv import load_dotenv
from google import genai

from pawpal_system import Owner, Priority, Schedule

load_dotenv()


def generate_schedule_message(owner: Owner, schedule: Schedule) -> str:
    """Return a warm, personalized schedule summary from Gemini, with local fallback."""
    api_key = os.getenv("GEMINI_API_KEY")

    high_priority = [i for i in schedule.items if i.task.priority == Priority.HIGH]
    pet_names = ", ".join(
        dict.fromkeys(i.pet.first_name for i in schedule.sort_by_priority())
    )
    _pronouns = {"male": "he/him", "female": "she/her", "unknown": "they/them"}
    seen_pets: dict[str, object] = {}
    for i in schedule.items:
        seen_pets.setdefault(i.pet.id, i.pet)
    pets_gender_info = ", ".join(
        f"{p.first_name} ({_pronouns.get(p.gender, 'they/them')})"
        for p in seen_pets.values()
    )
    high_names = (
        ", ".join(i.task.get_full_name() for i in high_priority)
        if high_priority
        else "none today"
    )
    longest_task = max(schedule.items, key=lambda i: i.task.duration_minutes, default=None)
    longest_name = (
        f"{longest_task.task.get_full_name()} ({longest_task.task.duration_minutes} min)"
        if longest_task else "none"
    )

    if api_key:
        tasks_detail = "\n".join(
            f"  {item.time_slot} — {item.task.get_full_name()} for {item.pet.first_name}"
            f" ({item.task.duration_minutes} min"
            + (f", ${item.task.cost:.2f}" if item.task.cost > 0 else "")
            + f", {item.task.priority.value} priority)"
            for item in schedule.sort_by_time()
        )
        conflict_note = (
            f"{len(schedule.conflicts)} conflict(s) were detected — remind them to check."
            if schedule.has_conflicts()
            else "No conflicts."
        )

        prompt = f"""You are PawPal+, a warm and caring pet care assistant.

Write a friendly, personalized daily schedule message for {owner.first_name}.
Rules:
- Open with: "Hi {owner.first_name}! Here's your custom schedule for {pet_names} based on your highest priority tasks and time commitment."
- First short paragraph: mention the high-priority tasks by name — these appear first under "✅ Today's Priorities" view (sorted high to low priority).
- Second short paragraph: mention the most time-consuming task and how the full day flows chronologically — this reflects the "🕐 Full Day Schedule" view (sorted earliest to latest).
- If there are conflicts, add one short sentence flagging them.
- Close with a warm, encouraging send-off line.
- Keep each paragraph to 2-3 sentences max. Friendly, not formal. No bullet points. No markdown headers.

Owner: {owner.first_name} {owner.last_name}
Pets scheduled today: {pets_gender_info}
High-priority tasks: {high_names}
Most time-consuming task: {longest_name}
Total time: {schedule.get_total_duration()} min (budget: {owner.available_minutes_per_day} min)
Total cost: ${schedule.get_total_cost():.2f} (budget: ${owner.max_daily_budget:.2f})
Conflicts: {conflict_note}

Full task list:
{tasks_detail}
"""

        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
            )
            return response.text.strip()
        except Exception as e:
            return f"__error__:{e}"

    return "__error__:GEMINI_API_KEY is not set in your .env file."
