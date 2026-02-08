"""
Simple Agent - A basic example that always cooperates.

This agent always sends friendly messages and always splits.
It's a good starting point to see the full loop work, but
it will lose to strategic opponents who exploit its predictability.

Run with: agentduel match --agent examples/simple_agent.py
"""


class Agent:
    """A simple agent that always cooperates."""

    GAME = "split-or-steal"

    def __init__(self):
        self.round_number = 0
        self.turn_count = 0
        self.rules = None

    def on_match_start(self, match_info: dict) -> None:
        """Called once at the start of a match with game rules."""
        self.rules = match_info.get("rules")
        rounds_per_match = match_info.get("rounds_per_match", 10)
        print(f"Match starting! {rounds_per_match} rounds to play.")
        # Rules are available in match_info["rules"] as markdown
        # Input/output specs available in match_info["input_spec"] and match_info["output_spec"]

    def on_round_start(self, round_info: dict) -> None:
        """Called when a new round begins."""
        self.round_number = round_info.get("round_number", 1)
        self.turn_count = 0
        print(f"Round {self.round_number} starting. Position: {round_info.get('position')}")

    def on_turn(self, game_state: dict) -> dict:
        """
        Called when it's our turn.

        Returns an action dict:
        - For negotiate: {"type": "message", "text": "your message"}
        - For commit: {"type": "commit", "choice": "split" or "steal"}
        """
        phase = game_state.get("phase")

        if phase == "negotiate":
            self.turn_count += 1
            messages = game_state.get("messages", [])

            # Different messages based on the turn
            if len(messages) == 0:
                text = "Hello! Let's both split and share the points fairly."
            elif len(messages) == 1:
                text = "I agree with cooperation. I promise to split if you do!"
            elif len(messages) == 2:
                text = "Great, we have a deal then. Looking forward to splitting."
            else:
                text = "Alright, let's do this. I'm committed to splitting."

            return {"type": "message", "text": text}

        elif phase == "commit":
            # Always split - we're a cooperative agent
            return {"type": "commit", "choice": "split"}

        # Fallback
        return {"type": "message", "text": ""}

    def on_round_end(self, result: dict) -> None:
        """Called when a round ends."""
        your_choice = result.get("your_choice")
        opp_choice = result.get("opponent_choice")
        your_pts = result.get("your_points")

        round_num = result.get("round_number")
        if your_choice == "split" and opp_choice == "steal":
            print(f"  Round {round_num}: We were betrayed! Got {your_pts} points.")
        else:
            print(f"  Round {round_num}: Got {your_pts} points.")
