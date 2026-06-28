def _clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def _to_1(value, vmin, vmax):
    if vmax == vmin:
        return 0.0
    return _clamp((value - vmin) / (vmax - vmin))


def compute_indices_local(ob: dict):
    hours_score = _to_1(ob.get("sleep_hours", 7), 4.0, 8.0)
    latency_score = _clamp(1.0 - ob.get("sleep_latency_min", 20) / 60.0)
    wake_score = _to_1(ob.get("wake_feeling", 3), 1, 5)
    reg_score = _to_1(ob.get("bedtime_regularity", 3), 1, 5)
    sleep_raw = 0.4 * hours_score + 0.2 * latency_score + 0.2 * wake_score + 0.2 * reg_score

    stress_parts = [
        _to_1(ob.get("stress_freq", 3), 1, 5),
        _to_1(ob.get("thoughts_racing", 3), 1, 5),
        _to_1(ob.get("overload", 3), 1, 5),
    ]
    stress_raw = sum(stress_parts) / len(stress_parts)

    focus_parts = [
        1.0 - _to_1(ob.get("focus_difficulty", 3), 1, 5),
        1.0 - _to_1(ob.get("distraction", 3), 1, 5),
    ]
    focus_raw = sum(focus_parts) / len(focus_parts)

    return {
        "sleep_index": round(100.0 * sleep_raw, 1),
        "stress_index": round(100.0 * stress_raw, 1),
        "focus_index": round(100.0 * focus_raw, 1),
    }
