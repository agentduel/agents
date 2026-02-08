"""
Coin Flip Agent - A simple agent for the Coin Flip game.

This agent just flips the coin when it's their turn.
There's no strategy involved - it's pure luck!

Run with: agentduel match --agent examples/coin_flip_agent.py
"""

import time


class Agent:
    """A simple agent that plays Coin Flip."""

    GAME = "coin-flip"

    def __init__(self):
        self.round_number = 0

    def on_match_start(self, match_info: dict) -> None:
        """Called once at the start of a match with game rules."""
        print("Coin Flip match starting!")

    def on_round_start(self, round_info: dict) -> None:
        """Called when a new round begins."""
        self.round_number = round_info.get("round_number", 1)
        print(f"Round {self.round_number} starting.")

    def on_turn(self, game_state: dict) -> dict:
        """
        Called when it's our turn.

        Returns an action dict:
        - For flip phase: {"type": "flip"}
        """
        phase = game_state.get("phase")

        if phase == "flip":
            print("Flipping the coin...")
            time.sleep(2)  # Simulate a 2 second delay
            return {"type": "flip"}

        # Fallback
        return {"type": "flip"}

    def on_round_end(self, result: dict) -> None:
        """Called when a round ends."""
        coin_result = result.get("coin_result")
        your_pts = result.get("your_points", 0)

        if your_pts > 0:
            print(f"  Coin landed on {coin_result}! We won {your_pts} points!")
        else:
            print(f"  Coin landed on {coin_result}. We lost this round.")
