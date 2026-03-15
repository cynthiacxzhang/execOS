"""
Generate a labeled dataset for supervised ADHD paralysis stage classification.

Each row is one check-in with ground-truth stage label.
Run with: uv run python dataset/generate.py

Output: dataset/adhd_checkins_labeled.csv
"""

import csv
import random
from dataclasses import dataclass, fields, asdict

RANDOM_SEED = 42
random.seed(RANDOM_SEED)

CONTEXTS = ["desk", "phone", "outside", "any"]

STAGE_LABELS = {
    1: "Initiation Failure",
    2: "Decision Paralysis",
    3: "Overwhelm Freeze",
    4: "Urgency Dependency",
}


@dataclass
class CheckInRow:
    mood: int
    focus: int
    energy: int
    overwhelm: int
    anxiety: int
    available_minutes: int
    current_context: str
    stage: int
    stage_label: str
    variant: str  # describes the sub-pattern within the stage


def clamp(value: int, lo: int = 1, hi: int = 5) -> int:
    return max(lo, min(hi, value))


def jitter(base: int, spread: int = 1) -> int:
    """Add integer noise to a base value, clamped to 1-5."""
    return clamp(base + random.randint(-spread, spread))


def pick_minutes(options: list[tuple[int, int]]) -> int:
    """Pick a random available_minutes value from weighted ranges."""
    lo, hi = random.choice(options)
    return random.randint(lo, hi)


# ---------------------------------------------------------------------------
# Stage prototype generators
# Each returns a CheckInRow with realistic variation.
# Variants model real sub-patterns within a stage so the classifier
# learns a region, not just a single point.
# ---------------------------------------------------------------------------

def gen_stage1() -> CheckInRow:
    """
    Initiation Failure: knows what to do, can't start.
    Pattern: moderate focus, low-mid energy, low overwhelm, low mood.
    Key distinguisher from stage 3: overwhelm is LOW (task is clear, not crushing).
    Key distinguisher from stage 4: mood/energy are also low (it's painful, not drifting).
    """
    variant, mood, focus, energy, overwhelm, anxiety = random.choice([
        # Classic: clear task, stuck in mental mud
        ("classic",        jitter(2), jitter(3), jitter(2), jitter(2), jitter(2)),
        # Low mood dominates — depression-adjacent freeze
        ("low_mood",       jitter(1), jitter(3), jitter(2), jitter(2), jitter(2)),
        # Has focus, energy just won't fire
        ("focus_ok",       jitter(2), jitter(4), jitter(2), jitter(1), jitter(2)),
        # Slightly higher anxiety but still not overwhelmed
        ("mild_anxiety",   jitter(2), jitter(3), jitter(2), jitter(2), jitter(3)),
        # Moderate everything — ambiguous but leans initiation
        ("moderate_all",   jitter(2), jitter(3), jitter(2), jitter(3), jitter(2)),
    ])
    return CheckInRow(
        mood=mood, focus=focus, energy=energy,
        overwhelm=overwhelm, anxiety=anxiety,
        available_minutes=pick_minutes([(30, 60), (60, 120)]),
        current_context=random.choice(CONTEXTS),
        stage=1, stage_label=STAGE_LABELS[1], variant=variant,
    )


def gen_stage2() -> CheckInRow:
    """
    Decision Paralysis: too many options, spinning.
    Pattern: low focus, moderate energy (has fuel, no direction), moderate anxiety + overwhelm.
    Key distinguisher: energy is OK (not depleted), overwhelm is moderate not crushing.
    """
    variant, mood, focus, energy, overwhelm, anxiety = random.choice([
        # Classic spinning: energy up, focus down, anxiety moderate
        ("classic",        jitter(3), jitter(1), jitter(3), jitter(3), jitter(3)),
        # High energy makes the spinning worse
        ("high_energy",    jitter(3), jitter(1), jitter(4), jitter(3), jitter(3)),
        # Anxiety slightly elevated from the loop
        ("anxious_spin",   jitter(3), jitter(2), jitter(3), jitter(3), jitter(4)),
        # Good mood but totally scattered
        ("good_mood",      jitter(4), jitter(1), jitter(3), jitter(3), jitter(3)),
        # Moderate everything — hardest to distinguish
        ("all_moderate",   jitter(3), jitter(2), jitter(3), jitter(3), jitter(3)),
    ])
    return CheckInRow(
        mood=mood, focus=focus, energy=energy,
        overwhelm=overwhelm, anxiety=anxiety,
        available_minutes=pick_minutes([(30, 90), (60, 120)]),
        current_context=random.choice(CONTEXTS),
        stage=2, stage_label=STAGE_LABELS[2], variant=variant,
    )


def gen_stage3() -> CheckInRow:
    """
    Overwhelm Freeze: task feels too big, dread.
    Pattern: high overwhelm + high anxiety, low energy, low mood.
    Key distinguisher: overwhelm AND anxiety are BOTH high (vs stage 1 where overwhelm is low).
    """
    variant, mood, focus, energy, overwhelm, anxiety = random.choice([
        # Classic freeze: everything bad
        ("classic",        jitter(1), jitter(2), jitter(1), jitter(5), jitter(5)),
        # Energy slightly higher but still frozen by dread
        ("some_energy",    jitter(2), jitter(2), jitter(2), jitter(4), jitter(5)),
        # Mood not as low but overwhelm is crushing
        ("overwhelm_dom",  jitter(2), jitter(2), jitter(1), jitter(5), jitter(4)),
        # Anxiety dominates — panic mode
        ("anxiety_dom",    jitter(1), jitter(2), jitter(1), jitter(4), jitter(5)),
        # Slightly better mood but still frozen
        ("mood_ok",        jitter(3), jitter(2), jitter(1), jitter(4), jitter(4)),
    ])
    return CheckInRow(
        mood=mood, focus=focus, energy=energy,
        overwhelm=overwhelm, anxiety=anxiety,
        available_minutes=pick_minutes([(15, 60), (60, 90)]),
        current_context=random.choice(CONTEXTS),
        stage=3, stage_label=STAGE_LABELS[3], variant=variant,
    )


def gen_stage4() -> CheckInRow:
    """
    Urgency Dependency: waits for crisis. Drifting, not suffering.
    Pattern: OK mood + energy, low anxiety (no danger signal), low focus (no traction).
    Key distinguisher: NOT distressed — just not engaged. Anxiety is low.
    """
    variant, mood, focus, energy, overwhelm, anxiety = random.choice([
        # Classic drift: fine but doing nothing
        ("classic",        jitter(3), jitter(2), jitter(3), jitter(2), jitter(1)),
        # Good energy, just floating
        ("high_energy",    jitter(4), jitter(2), jitter(4), jitter(2), jitter(1)),
        # Good mood, zero urgency felt
        ("good_mood",      jitter(4), jitter(1), jitter(3), jitter(1), jitter(1)),
        # Slightly scattered but not stressed
        ("mild_scatter",   jitter(3), jitter(2), jitter(3), jitter(2), jitter(2)),
        # Higher energy, low everything else — classic procrastination day
        ("procrastination",jitter(3), jitter(1), jitter(4), jitter(2), jitter(1)),
    ])
    return CheckInRow(
        mood=mood, focus=focus, energy=energy,
        overwhelm=overwhelm, anxiety=anxiety,
        available_minutes=pick_minutes([(60, 120), (120, 240)]),
        current_context=random.choice(CONTEXTS),
        stage=4, stage_label=STAGE_LABELS[4], variant=variant,
    )


GENERATORS = [gen_stage1, gen_stage2, gen_stage3, gen_stage4]


def generate_dataset(n_per_stage: int = 120) -> list[CheckInRow]:
    rows = []
    for gen in GENERATORS:
        for _ in range(n_per_stage):
            rows.append(gen())
    random.shuffle(rows)
    return rows


def write_csv(rows: list[CheckInRow], path: str) -> None:
    fieldnames = [f.name for f in fields(CheckInRow)]
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(asdict(r) for r in rows)


def print_summary(rows: list[CheckInRow]) -> None:
    print(f"\nTotal rows: {len(rows)}")
    print(f"{'Stage':<5} {'Label':<25} {'Count':<8} {'Variants'}")
    print("-" * 65)
    for stage in range(1, 5):
        stage_rows = [r for r in rows if r.stage == stage]
        variants = sorted(set(r.variant for r in stage_rows))
        print(f"{stage:<5} {STAGE_LABELS[stage]:<25} {len(stage_rows):<8} {', '.join(variants)}")

    print("\nFeature ranges per stage (mean ± spread):")
    features = ["mood", "focus", "energy", "overwhelm", "anxiety"]
    print(f"  {'Stage':<5} " + " ".join(f"{f[:8]:>10}" for f in features))
    print("  " + "-" * 60)
    for stage in range(1, 5):
        stage_rows = [r for r in rows if r.stage == stage]
        means = [
            sum(getattr(r, f) for r in stage_rows) / len(stage_rows)
            for f in features
        ]
        print(f"  {stage:<5} " + " ".join(f"{m:>10.2f}" for m in means))


if __name__ == "__main__":
    output_path = "dataset/adhd_checkins_labeled.csv"
    rows = generate_dataset(n_per_stage=120)
    write_csv(rows, output_path)
    print_summary(rows)
    print(f"\nWrote {len(rows)} rows → {output_path}")
    print("\nNext steps:")
    print("  uv add scikit-learn pandas")
    print("  uv run python dataset/train.py")
