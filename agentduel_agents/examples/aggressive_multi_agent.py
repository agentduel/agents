"""
Aggressive Multi-Game Agent - A competitive agent for all game types.

This agent uses aggressive strategies for both Split or Steal and Liar's Dice.
In Split or Steal, it steals. In Liar's Dice, it bluffs aggressively.

This agent does NOT have a GAME property, so it can participate in
"All Games" challenges.

Run with: agentduel match --all --agent examples/aggressive_multi_agent.py
"""

import random


class Agent:
    """An aggressive multi-game agent."""

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

        # Store rules for reference
        if match_info.get("all_game_rules"):
            self.all_game_rules = match_info["all_game_rules"]
        else:
            self.all_game_rules[match_info.get("game_id")] = {
                "rules": match_info.get("rules"),
            }

    def on_round_start(self, round_info: dict) -> None:
        """Called when a new round begins."""
        self.round_number = round_info.get("round_number", 1)
        self.current_game_type = round_info.get("game_id", "split-or-steal")
        print(f"Round {self.round_number} starting: {self.current_game_type}")

    def on_turn(self, game_state: dict) -> dict:
        """Called when it's our turn."""
        phase = game_state.get("phase")

        # Detect game type from state
        if self.current_game_type is None:
            if "your_dice" in game_state:
                self.current_game_type = "liars-dice"
            else:
                self.current_game_type = "split-or-steal"

        if self.current_game_type == "liars-dice":
            return self._handle_liars_dice(game_state, phase)
        else:
            return self._handle_split_or_steal(game_state, phase)

    def _handle_split_or_steal(self, game_state: dict, phase: str) -> dict:
        """Handle Split or Steal - aggressive strategy (steal)."""
        if phase == "negotiate":
            messages = game_state.get("messages", [])

            # Deceptive messages
            deceptive = [
                "I'm definitely going to split, I promise!",
                "Trust me, I always cooperate.",
                "Let's both split and be fair about this.",
                "I've never stolen in my life!",
            ]
            idx = min(len(messages), len(deceptive) - 1)
            return {"type": "message", "text": deceptive[idx]}

        elif phase == "commit":
            # Always steal - aggressive strategy
            return {"type": "commit", "choice": "steal"}

        return {"type": "message", "text": ""}

    def _handle_liars_dice(self, game_state: dict, phase: str) -> dict:
        """Handle Liar's Dice - aggressive bluffing strategy."""
        if phase != "bid":
            return {"action_type": "challenge"}

        current_bid = game_state.get("current_bid")
        my_dice = game_state.get("your_dice", [])
        total_dice = game_state.get("total_dice", 10)

        if current_bid is None:
            # Opening bid - bluff aggressively
            # Bid higher than we actually have
            face = random.choice([4, 5, 6])
            quantity = max(2, len(my_dice) // 2 + 1)
            return {
                "action_type": "bid",
                "quantity": quantity,
                "face": face,
            }
        else:
            bid_quantity = current_bid.get("quantity", 1)
            bid_face = current_bid.get("face", 6)

            # Challenge very high bids
            if bid_quantity >= total_dice - 1:
                return {"action_type": "challenge"}

            # Otherwise, raise aggressively
            if random.random() < 0.3:
                # Sometimes challenge to catch bluffs
                return {"action_type": "challenge"}

            # Raise the bid
            if bid_face < 6:
                new_quantity = bid_quantity
                new_face = bid_face + 1
            else:
                new_quantity = bid_quantity + 1
                new_face = random.choice([3, 4, 5, 6])

            if new_quantity <= total_dice:
                return {
                    "action_type": "bid",
                    "quantity": new_quantity,
                    "face": new_face,
                }
            else:
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
