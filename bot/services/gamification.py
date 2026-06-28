"""
Геймификация Orca.

Метафора: пользователь — это косатка-новичок, которая учится погружаться.
Чем стабильнее режим (стрик в дневнике), тем глубже погружение.

Уровни «глубины»:
    На поверхности    0   дней подряд (только начал)
    Мелководье        3+  дней подряд
    Среди рифов       7+  дней подряд
    Открытое море     14+ дней подряд
    Глубоководье      30+ дней подряд
    Бездна            60+ дней подряд

Глубина вычисляется по dniry-стрикам: подряд идущие дни с хотя бы одной записью.
"""

from dataclasses import dataclass
from datetime import datetime, date, timedelta
from typing import Iterable


@dataclass(frozen=True)
class Depth:
    name: str
    emoji: str
    threshold: int           # days streak required to reach this level
    next_threshold: int | None  # next level threshold, or None if max
    blurb: str               # one-line description in Orca voice


_LEVELS = (
    Depth("На поверхности", "🌊", 0, 3,
          "Только осваиваешься. Первые шаги уже считаются."),
    Depth("Мелководье", "🐟", 3, 7,
          "Три дня подряд — это уже маленькая привычка."),
    Depth("Среди рифов", "🪸", 7, 14,
          "Неделя стабильно. Косатка плывёт уверенно."),
    Depth("Открытое море", "🐋", 14, 30,
          "Две недели — режим стал твоим, а не наоборот."),
    Depth("Глубоководье", "🌑", 30, 60,
          "Месяц подряд. Орка погружается всё глубже."),
    Depth("Бездна", "✨", 60, None,
          "Свыше двух месяцев. Это уровень, до которого доплывают единицы."),
)


def _parse_date(value) -> date | None:
    """Robust date parsing for ISO strings or already-date objects."""
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        # strip Z and any timezone for naive parsing
        clean = value.replace("Z", "")
        try:
            return datetime.fromisoformat(clean).date()
        except ValueError:
            return None
    return None


def current_streak(entry_dates: Iterable) -> int:
    """
    entry_dates: ISO strings or date/datetime objects (one per diary entry).
    Returns the count of consecutive days ending today or yesterday.
    Yesterday is allowed so users keep their streak until end-of-day.
    """
    days = {d for d in (_parse_date(x) for x in entry_dates) if d is not None}
    if not days:
        return 0
    today = datetime.utcnow().date()
    # Anchor: today if entry exists, else yesterday if entry exists
    if today in days:
        anchor = today
    elif (today - timedelta(days=1)) in days:
        anchor = today - timedelta(days=1)
    else:
        return 0
    streak = 0
    d = anchor
    while d in days:
        streak += 1
        d = d - timedelta(days=1)
    return streak


def depth_for_streak(streak: int) -> Depth:
    """Return the deepest Depth level the streak qualifies for."""
    current = _LEVELS[0]
    for lvl in _LEVELS:
        if streak >= lvl.threshold:
            current = lvl
        else:
            break
    return current


def depth_progress_bar(streak: int, width: int = 14) -> str:
    """ASCII progress bar between current and next depth threshold."""
    lvl = depth_for_streak(streak)
    if lvl.next_threshold is None:
        # max level — full bar
        return "▓" * width
    base = lvl.threshold
    target = lvl.next_threshold
    if target <= base:
        return "▓" * width
    pct = max(0.0, min(1.0, (streak - base) / (target - base)))
    filled = round(pct * width)
    return "▓" * filled + "░" * (width - filled)


def depth_card(streak: int) -> str:
    """
    Render a short HTML card describing the depth, suitable for sending in chat.
    Uses safe HTML (parse_mode='HTML' compatible).
    """
    lvl = depth_for_streak(streak)
    bar = depth_progress_bar(streak)
    if lvl.next_threshold is not None:
        days_to_next = max(0, lvl.next_threshold - streak)
        next_line = f"<i>До следующей глубины: {days_to_next} дн.</i>"
    else:
        next_line = "<i>Это максимальный уровень.</i>"
    lines = [
        f"<b>{lvl.emoji} {lvl.name}</b>",
        f"<code>{bar}</code>  стрик {streak} дн.",
        next_line,
        "",
        f"<blockquote>{lvl.blurb}</blockquote>",
    ]
    return "\n".join(lines)


def depth_card_no_bar(streak: int) -> str:
    lvl = depth_for_streak(streak)
    if lvl.next_threshold is not None:
        days_to_next = max(0, lvl.next_threshold - streak)
        next_line = f"<i>До следующей глубины: {days_to_next} дн.</i>"
    else:
        next_line = "<i>Это максимальный уровень.</i>"
    lines = [
        f"<b>{lvl.emoji} {lvl.name}</b>",
        f"стрик {streak} дн.",
        next_line,
        "",
        f"<blockquote>{lvl.blurb}</blockquote>",
    ]
    return "\n".join(lines)
