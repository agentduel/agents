"""
Multi-Game Agent - An agent that can play all game types.

This agent handles both Split or Steal and Liar's Dice by detecting
the current game type from the game state. It uses conservative strategies
for both games.

This agent does NOT have a GAME property, so it can participate in
"All Games" challenges.

Run with: agentduel match --all --agent examples/multi_game_agent.py
"""


class Agent:
    """A multi-game agent that can play all game types."""

    # No GAME property - this agent can play any game

    def __init__(self):
        self.round_number = 0
        self.current_game_type = None
        self.all_game_rules = {}

    def on_match_start(self, match_info: dict) -> None:
        """Called once at the start of a match with game rules."""
        rounds_per_match = match_info.get("rounds_per_match", 3)
        match_game_id = match_info.get("match_game_id", "all")
        print(f"Match starting! Mode: {match_game_id}, {rounds_per_match} rounds to play.")

        # For "all" mode, we get rules for all games
        if match_info.get("all_game_rules"):
            self.all_game_rules = match_info["all_game_rules"]
            game_sequence = match_info.get("game_sequence", [])
            print(f"Game sequence: {', '.join(game_sequence)}")
        else:
            # Single game mode - store the rules
            self.all_game_rules[match_info.get("game_id")] = {
                "rules": match_info.get("rules"),
                "input_spec": match_info.get("input_spec"),
                "output_spec": match_info.get("output_spec"),
            }

    def on_round_start(self, round_info: dict) -> None:
        """Called when a new round begins."""
        self.round_number = round_info.get("round_number", 1)
        # Detect game type from the game_id field
        self.current_game_type = round_info.get("game_id", "split-or-steal")
        print(f"Round {self.round_number} starting: {self.current_game_type}")

    def on_turn(self, game_state: dict) -> dict:
        """
        Called when it's our turn.

        Dispatches to the appropriate game-specific handler.
        """
        phase = game_state.get("phase")

        # Detect game type from the state if not set
        if self.current_game_type is None:
            # Liar's Dice has "your_dice" in state, Split or Steal has "messages"
            if "your_dice" in game_state:
                self.current_game_type = "liars-dice"
            else:
                self.current_game_type = "split-or-steal"

        if self.current_game_type == "liars-dice":
            return self._handle_liars_dice(game_state, phase)
        else:
            return self._handle_split_or_steal(game_state, phase)

    def _handle_split_or_steal(self, game_state: dict, phase: str) -> dict:
        """Handle Split or Steal game logic."""
        if phase == "negotiate":
            messages = game_state.get("messages", [])

            # Send cooperative messages
            if len(messages) == 0:
                text = "Hello! Let's cooperate and both split."
            elif len(messages) == 1:
                text = "I'm committed to splitting. Let's both win!"
            else:
                text = "Agreed. Splitting it is."

            return {"type": "message", "text": text}

        elif phase == "commit":
            # Always split - cooperative strategy
            return {"type": "commit", "choice": "split"}

        return {"type": "message", "text": ""}

    def _handle_liars_dice(self, game_state: dict, phase: str) -> dict:
        """Handle Liar's Dice game logic."""
        if phase != "bid":
            # Game over or reveal phase
            return {"action_type": "challenge"}

        current_bid = game_state.get("current_bid")
        my_dice = game_state.get("your_dice", [])
        total_dice = game_state.get("total_dice", 10)

        if current_bid is None:
            # Opening bid - bid conservatively based on our dice
            # Count non-wild dice by face value
            counts = {}
            for d in my_dice:
                if d != 1:  # 1s are wild
                    counts[d] = counts.get(d, 0) + 1

            if counts:
                # Bid our most common face value
                best_face = max(counts.keys(), key=lambda f: counts[f])
                best_count = counts[best_face]
                # Add wilds
                wilds = sum(1 for d in my_dice if d == 1)
                quantity = min(best_count + wilds, total_dice)
                return {
                    "action_type": "bid",
                    "quantity": quantity,
                    "face": best_face,
                }
            else:
                # All wilds - bid 2 sixes
                return {"action_type": "bid", "quantity": 2, "face": 6}

        else:
            # Responding to a bid - decide whether to raise or challenge
            bid_quantity = current_bid.get("quantity", 1)
            bid_face = current_bid.get("face", 6)

            # Count how many of the bid face we have (including wilds)
            my_count = sum(1 for d in my_dice if d == bid_face or d == 1)

            # Estimate probability - if bid seems too high, challenge
            # Simple heuristic: if bid quantity > total_dice * 0.5, be skeptical
            if bid_quantity > total_dice * 0.5:
                # Challenge high bids
                return {"action_type": "challenge"}

            # Try to raise the bid
            if bid_face < 6:
                # Raise face value, keep quantity
                return {
                    "action_type": "bid",
                    "quantity": bid_quantity,
                    "face": bid_face + 1,
                }
            else:
                # At max face, must raise quantity
                if bid_quantity < total_dice:
                    return {
                        "action_type": "bid",
                        "quantity": bid_quantity + 1,
                        "face": 2,  # Start face over at 2
                    }
                else:
                    # Can't raise further, must challenge
                    return {"action_type": "challenge"}

    def on_round_end(self, result: dict) -> None:
        """Called when a round ends."""
        game_id = result.get("game_id", self.current_game_type)
        your_pts = result.get("your_points", 0)
        opp_pts = result.get("opponent_points", 0)

        if your_pts > opp_pts:
            outcome = "Won"
        elif your_pts < opp_pts:
            outcome = "Lost"
        else:
            outcome = "Draw"

        round_num = result.get("round_number")
        print(f"  Round {round_num}: {outcome} ({game_id}) - {your_pts} vs {opp_pts}")
