"""
Interventions: stage → intervention card

Each card has:
  title: short label
  body: explanation of why this helps
  action: one concrete thing to do RIGHT NOW
"""

INTERVENTIONS = {
    1: {
        "title": "Body Double Start",
        "body": "You know what to do — your brain just won't fire the starting signal. This is dopamine, not laziness. We're going to trick the activation system.",
        "action": "Set a 2-minute timer. Open the task. Do literally one sentence or one click. The timer is your permission to stop after 2 minutes.",
    },
    2: {
        "title": "Coin Flip Protocol",
        "body": "Too many options is the same as none. Your brain is spinning trying to optimize — but any start beats perfect paralysis.",
        "action": "Look at your top 2 tasks. Flip a coin or pick the one with the shorter name. Start that one. You can switch in 10 minutes if it's wrong.",
    },
    3: {
        "title": "Microscopic First Step",
        "body": "The task feels enormous because your brain is picturing the whole thing. We need to make it so small it feels embarrassing to not do.",
        "action": "Name the absolute smallest possible action — not 'write report', but 'open the doc'. Not 'clean kitchen', but 'put one dish in the sink'. Do only that.",
    },
    4: {
        "title": "Artificial Deadline",
        "body": "Your brain needs urgency to activate. Since there's no real deadline, we're manufacturing one — and making it public to add accountability pressure.",
        "action": "Text or message one person: 'I'm working on [task] for the next 25 minutes.' Set a 25-minute timer. Their awareness is now your deadline.",
    },
}

def get_intervention(stage: int) -> dict:
    if stage not in INTERVENTIONS:
        raise ValueError(f"Unknown stage: {stage}. Must be 1-4.")
    return INTERVENTIONS[stage]
