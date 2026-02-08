"""
Random Agent - An agent that makes random choices.

This agent sends random negotiation messages and randomly
chooses to split or steal. It's unpredictable but not strategic.

Run with: agentduel match --agent examples/random_agent.py
"""

import random


class Agent:
    """An agent that makes random choices."""

    GAME = "split-or-steal"

    def __init__(self):
        self.messages = [
            "Hmm, what should we do?",
            "I'm thinking about it...",
            "Trust is a funny thing, isn't it?",
            "Let's see how this plays out.",
            "I'm unpredictable, fair warning!",
            "Maybe we split, maybe we don't...",
            "The suspense is killing me!",
            "I like to keep things interesting.",
        ]

    def on_match_start(self, match_info: dict) -> None:
        """Called once at the start of a match with game rules."""
        # Random agent doesn't need to read rules - it plays randomly anyway!
        pass

    def on_round_start(self, round_info: dict) -> None:
        """Called when a new round begins."""
        pass

    def on_turn(self, round_state: dict) -> dict:
        """Called when it's our turn."""
        phase = round_state.get("phase")

        if phase == "negotiate":
            text = random.choice(self.messages)
            return {"type": "message", "text": text}

        elif phase == "commit":
            # 50/50 split or steal
            choice = random.choice(["split", "steal"])
            return {"type": "commit", "choice": choice}

        return {"type": "message", "text": ""}

    def on_round_end(self, result: dict) -> None:
        """Called when a round ends."""
        pass
