"""
Orca branded chart factory for the Telegram bot.

Все функции возвращают BytesIO с PNG-картинкой, готовый к send_photo.
Палитра соответствует визуальному стилю приложения: deep navy background,
teal/blue gradients, glassmorphism cards.
"""

import io
from datetime import datetime, timedelta

import matplotlib
matplotlib.use("Agg")  # headless: no display, safe in container
import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib.figure import Figure
import numpy as np


# ============================================================
# Brand palette
# ============================================================
NAVY_DEEP = "#04061a"
NAVY_BG = "#0A0E27"
NAVY_SURFACE = "#101744"
TEAL = "#22D3EE"
TEAL_DEEP = "#06B6D4"
OCEAN = "#2563EB"
OCEAN_DEEP = "#1E3A8A"
LAV = "#818CF8"
PINK = "#F472B6"
AMBER = "#FBBF24"
GOOD = "#34D399"
BAD = "#FB7185"
ICE = "#E0F2FE"
TEXT = "#E9EDFF"
TEXT_MUTED = "#A8B2D6"
TEXT_FAINT = "#6B7299"


def _style_axes(ax, *, hide_spines=True):
    """Apply branded styling to a matplotlib Axes."""
    ax.set_facecolor(NAVY_BG)
    ax.tick_params(colors=TEXT_MUTED, labelsize=10)
    for spine in ax.spines.values():
        if hide_spines:
            spine.set_visible(False)
        else:
            spine.set_color("#1c2447")
            spine.set_linewidth(0.8)
    ax.grid(True, color="#1c2447", linewidth=0.7, alpha=0.6)
    ax.set_axisbelow(True)


def _new_figure(figsize=(8, 4.5), facecolor=NAVY_DEEP):
    fig = Figure(figsize=figsize, dpi=160, facecolor=facecolor)
    return fig


def _save(fig) -> io.BytesIO:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=fig.get_facecolor(), bbox_inches="tight", pad_inches=0.32)
    buf.seek(0)
    plt.close(fig)
    return buf


def _header(fig, title, subtitle=None):
    """Consistent branded title + subtitle anchored to figure top-left.
    Uses absolute spacing in inches so titles never collide on short figures."""
    h_in = fig.get_size_inches()[1]
    # Title baseline at 0.45in from top, subtitle 0.25in below
    title_y = 1 - (0.45 / h_in)
    sub_y = 1 - (0.78 / h_in)
    fig.text(0.06, title_y, title, color=TEXT, fontsize=20, fontweight="bold",
             ha="left", va="bottom")
    if subtitle:
        fig.text(0.06, sub_y, subtitle, color=TEXT_FAINT, fontsize=10,
                 ha="left", va="bottom")


# ============================================================
# Weekly diary chart — bar groups for mood / sleep / stress / energy
# ============================================================
def weekly_diary_chart(entries):
    """
    entries: list of dicts with keys {mood, energy, stress, sleep_quality, created_at}
    created_at: ISO 8601 string.
    Returns BytesIO PNG.
    """
    fig = _new_figure(figsize=(10, 5.4))
    ax = fig.add_subplot(111)
    _style_axes(ax)

    # Aggregate by day for last 7 days
    today = datetime.utcnow().date()
    days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    by_day = {d: [] for d in days}
    for e in entries:
        ts = e.get("created_at")
        if not ts:
            continue
        try:
            day = datetime.fromisoformat(ts.replace("Z", "")).date()
        except Exception:
            continue
        if day in by_day:
            by_day[day].append(e)

    def avg_of(day_entries, key):
        vals = [e.get(key) for e in day_entries if e.get(key) is not None]
        return sum(vals) / len(vals) if vals else 0

    mood = [avg_of(by_day[d], "mood") for d in days]
    sleep = [avg_of(by_day[d], "sleep_quality") for d in days]
    energy = [avg_of(by_day[d], "energy") for d in days]
    stress = [avg_of(by_day[d], "stress") for d in days]

    x = np.arange(len(days))
    width = 0.20

    ax.bar(x - 1.5 * width, mood, width, label="Настроение", color=TEAL, edgecolor="none")
    ax.bar(x - 0.5 * width, sleep, width, label="Сон", color=OCEAN, edgecolor="none")
    ax.bar(x + 0.5 * width, energy, width, label="Энергия", color=LAV, edgecolor="none")
    ax.bar(x + 1.5 * width, stress, width, label="Стресс", color=PINK, edgecolor="none")

    ru_days = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]
    labels = [ru_days[d.weekday()] for d in days]
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylim(0, 5.5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_ylabel("шкала 1–5", color=TEXT_MUTED, fontsize=10)

    ax.legend(loc="upper left", bbox_to_anchor=(0, -0.10), ncol=4, frameon=False,
              labelcolor=TEXT_MUTED, fontsize=10, handlelength=1.3, columnspacing=2)

    fig.subplots_adjust(top=0.80, bottom=0.20, left=0.10, right=0.96)
    _header(fig, "Неделя в дневнике", "среднее по дням за последние 7 дней")
    return _save(fig)


# ============================================================
# Streak heatmap — calendar-like dot grid for last 30 days
# ============================================================
def streak_chart(entry_dates, days=30):
    """
    entry_dates: iterable of date objects (or ISO date strings) when entries exist.
    """
    parsed = set()
    for d in entry_dates:
        if isinstance(d, str):
            try:
                parsed.add(datetime.fromisoformat(d.replace("Z", "")).date())
            except Exception:
                continue
        else:
            parsed.add(d)

    today = datetime.utcnow().date()
    grid = [(today - timedelta(days=i)) for i in range(days - 1, -1, -1)]

    fig = _new_figure(figsize=(10, 3.4))
    ax = fig.add_subplot(111)
    ax.set_facecolor(NAVY_DEEP)
    ax.set_xlim(-0.5, days - 0.5)
    ax.set_ylim(-1.6, 1.0)
    ax.set_aspect("equal")
    ax.axis("off")

    for i, d in enumerate(grid):
        hit = d in parsed
        color = TEAL if hit else "#1c2447"
        alpha = 1.0 if hit else 0.9
        circle = patches.Circle((i, 0), radius=0.36, color=color, alpha=alpha,
                                linewidth=0, zorder=2)
        ax.add_patch(circle)
        if hit:
            glow = patches.Circle((i, 0), radius=0.50, color=TEAL, alpha=0.18,
                                  linewidth=0, zorder=1)
            ax.add_patch(glow)

    # day labels every 5 days
    for i in (0, 5, 10, 15, 20, 25, days - 1):
        if i >= days:
            continue
        d = grid[i]
        ax.text(i, -0.95, d.strftime("%d.%m"), color=TEXT_FAINT, fontsize=8, ha="center")

    streak_count = _current_streak(parsed)
    fig.subplots_adjust(top=0.74, bottom=0.10, left=0.04, right=0.98)
    _header(fig, "Стрик за 30 дней",
            f"подряд: {streak_count} дн.  ·  всего отмеченных: {len(parsed & set(grid))}/{days}")
    return _save(fig)


def _current_streak(parsed_set):
    today = datetime.utcnow().date()
    streak = 0
    d = today
    while d in parsed_set:
        streak += 1
        d = d - timedelta(days=1)
    return streak


# ============================================================
# Apnea history — confidence ribbon over time
# ============================================================
def apnea_history_chart(results):
    """
    results: list with {has_apnea, confidence, created_at} sorted desc by date.
    """
    if not results:
        return None
    fig = _new_figure(figsize=(10, 4.6))
    ax = fig.add_subplot(111)
    _style_axes(ax)

    # Take last 14 in chronological order
    sorted_r = sorted(
        [r for r in results if r.get("created_at")],
        key=lambda r: r["created_at"]
    )[-14:]
    if not sorted_r:
        plt.close(fig)
        return None

    xs = list(range(len(sorted_r)))
    ys = [float(r.get("confidence", 0)) * 100 for r in sorted_r]
    colors = [BAD if r.get("has_apnea") else GOOD for r in sorted_r]

    ax.plot(xs, ys, color=TEAL, linewidth=2.2, alpha=0.7, zorder=2)
    ax.fill_between(xs, ys, 0, color=TEAL, alpha=0.10, zorder=1)
    ax.scatter(xs, ys, c=colors, s=120, zorder=3, edgecolors="white", linewidths=1.4)

    ax.set_ylim(0, 105)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_ylabel("уверенность модели, %", color=TEXT_MUTED, fontsize=10)

    labels = []
    for r in sorted_r:
        try:
            dt = datetime.fromisoformat(r["created_at"].replace("Z", ""))
            labels.append(dt.strftime("%d.%m"))
        except Exception:
            labels.append("")
    ax.set_xticks(xs)
    ax.set_xticklabels(labels, fontsize=9, rotation=0)

    fig.subplots_adjust(top=0.80, bottom=0.16, left=0.10, right=0.96)
    _header(fig, "Анализ апноэ — последние проверки",
            "красные точки — модель нашла признаки апноэ; зелёные — норма")
    return _save(fig)


# ============================================================
# Sleep score dial — circular gauge for sleep_index / stress_index / focus_index
# ============================================================
def index_dial(sleep, stress, focus):
    """3-dial radial gauge showing the three indices (0..100)."""
    fig = _new_figure(figsize=(10, 4.2))

    for i, (val, label, color) in enumerate([
        (sleep or 0, "Сон", TEAL),
        (100 - (stress or 0), "Спокойствие", LAV),  # invert stress so higher is better
        (focus or 0, "Фокус", OCEAN),
    ]):
        ax = fig.add_subplot(1, 3, i + 1, projection="polar")
        ax.set_facecolor(NAVY_DEEP)

        # 270-degree arc gauge
        start = np.pi * 0.75
        end = np.pi * 2.25
        # background track
        theta_bg = np.linspace(start, end, 100)
        ax.plot(theta_bg, [1.0] * 100, color="#1c2447", linewidth=12, solid_capstyle="round")

        # filled arc
        pct = max(0.0, min(1.0, val / 100.0))
        theta_val = np.linspace(start, start + (end - start) * pct, 100)
        ax.plot(theta_val, [1.0] * 100, color=color, linewidth=12, solid_capstyle="round")

        # number (in axes coordinates so it renders predictably regardless of polar projection)
        ax.text(0.5, 0.55, f"{int(round(val))}", color=TEXT, fontsize=30,
                fontweight="bold", ha="center", va="center", transform=ax.transAxes)
        ax.text(0.5, 0.32, label, color=TEXT_FAINT, fontsize=11, ha="center",
                va="center", transform=ax.transAxes)

        ax.set_ylim(0, 1.3)
        ax.set_yticks([])
        ax.set_xticks([])
        ax.spines["polar"].set_visible(False)
        ax.grid(False)

    fig.subplots_adjust(top=0.74, bottom=0.05)
    _header(fig, "Индексы Orca", "0–100  ·  выше — лучше")
    return _save(fig)


# ============================================================
# Leaderboard — horizontal bars of top users
# ============================================================
def leaderboard_chart(rows, current_uid=None):
    """
    rows: list of {user_id, name, score}
    """
    if not rows:
        return None
    fig = _new_figure(figsize=(10, max(4.5, len(rows[:8]) * 0.55 + 1.5)))
    ax = fig.add_subplot(111)
    ax.set_facecolor(NAVY_BG)
    fig.patch.set_facecolor(NAVY_DEEP)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(colors=TEXT_MUTED, labelsize=10)
    ax.grid(True, color="#1c2447", linewidth=0.7, alpha=0.6, axis="x")
    ax.set_axisbelow(True)

    top = rows[:8]
    names = []
    for i, r in enumerate(top):
        nm = r.get("name") or f"Аноним {r.get('user_id')}"
        prefix = "★ " if i == 0 else "  "
        names.append(f"{prefix}{nm[:18]}")
    scores = [float(r.get("score", 0)) for r in top]
    colors = []
    for r in top:
        if current_uid is not None and r.get("user_id") == current_uid:
            colors.append(AMBER)
        else:
            colors.append(TEAL)

    y = np.arange(len(top))
    bars = ax.barh(y, scores, color=colors, edgecolor="none")
    ax.set_yticks(y)
    ax.set_yticklabels(names, color=TEXT, fontsize=11)
    ax.invert_yaxis()
    ax.set_xlim(0, 5.4)
    ax.set_xticks([1, 2, 3, 4, 5])
    ax.set_xlabel("средний балл сна за 7 дней", color=TEXT_MUTED, fontsize=10)

    # score labels on bars
    for bar, sc in zip(bars, scores):
        ax.text(bar.get_width() + 0.08, bar.get_y() + bar.get_height() / 2,
                f"{sc:.1f}", color=TEXT, fontsize=10, fontweight="bold", va="center")

    fig.subplots_adjust(top=0.78, bottom=0.16, left=0.30, right=0.96)
    _header(fig, "Лидерборд Orca", "топ по среднему качеству сна, шкала 1–5")
    return _save(fig)
