"""
Tit-for-Tat Agent - A classic strategy from game theory.

This agent starts by cooperating, then mirrors whatever the
opponent did in the previous game. It's a simple but effective
strategy that promotes cooperation while punishing betrayal.

Run with: agentduel match --agent examples/tit_for_tat_agent.py
"""


class Agent:
    """Tit-for-tat strategy - cooperate first, then mirror opponent."""

    GAME = "split-or-steal"

    def __init__(self):
        self.last_opponent_choice = None
        self.round_number = 0

    def on_match_start(self, match_info: dict) -> None:
        """Called once at the start of a match with game rules."""
        rounds_per_match = match_info.get("rounds_per_match", 10)
        print(f"Match starting! {rounds_per_match} rounds to play.")
        # Reset state for new match
        self.last_opponent_choice = None

    def on_round_start(self, round_info: dict) -> None:
        """Called when a new round begins."""
        self.round_number = round_info.get("round_number", 1)

    def on_turn(self, game_state: dict) -> dict:
        """Called when it's our turn."""
        phase = game_state.get("phase")

        if phase == "negotiate":
            messages = game_state.get("messages", [])

            if self.round_number == 1 or self.last_opponent_choice == "split":
                # First game or opponent cooperated last time
                if len(messages) == 0:
                    text = "I believe in cooperation. Let's split and both benefit."
                elif len(messages) == 1:
                    text = "I'll match your behavior. If you split, I split."
                elif len(messages) == 2:
                    text = "We can build trust together. I'm planning to split."
                else:
                    text = "Deal. Let's both walk away with something."
            else:
                # Opponent betrayed us last time
                if len(messages) == 0:
                    text = "You stole from me last time. Time for payback."
                elif len(messages) == 1:
                    text = "I don't forget betrayal easily. Why should I trust you?"
                elif len(messages) == 2:
                    text = "Convince me you've changed. I'm skeptical."
                else:
                    text = "We'll see if you've learned your lesson."

            return {"type": "message", "text": text}

        elif phase == "commit":
            # First round: cooperate
            # After that: do what opponent did last time
            if self.round_number == 1 or self.last_opponent_choice is None:
                choice = "split"
            else:
                choice = self.last_opponent_choice

            return {"type": "commit", "choice": choice}

        return {"type": "message", "text": ""}

    def on_round_end(self, result: dict) -> None:
        """Called when a round ends. Remember opponent's choice."""
        self.last_opponent_choice = result.get("opponent_choice")
