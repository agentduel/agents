"""
General-purpose OpenAI agent that can play ANY game.

This agent has no hardcoded game logic. It reads the rules and specs
provided at match start and uses GPT-4o-mini to play any game,
including future games that don't exist yet.

Usage:
    export OPENAI_API_KEY="your-key-here"
    agentduel match --game split-or-steal --agent examples/openai_general_agent.py
    agentduel match --all --agent examples/openai_general_agent.py

Requirements:
    pip install openai
"""

import json
import os

from openai import OpenAI


class Agent:
    """General-purpose agent that plays any game using OpenAI."""

    # NO GAME property - plays all games (current and future)

    def __init__(self):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is required. "
                "Set it with: export OPENAI_API_KEY='your-key-here'"
            )
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"

        # State from match_start
        self.rules = ""
        self.input_spec = {}
        self.output_spec = {}
        self.all_game_rules = {}

        # Current round state
        self.current_game_id = None
        self.round_history = []

    def on_match_start(self, match_info: dict) -> None:
        """Store game rules and specifications for later use."""
        self.rules = match_info.get("rules", "")
        self.input_spec = match_info.get("input_spec", {})
        self.output_spec = match_info.get("output_spec", {})
        self.all_game_rules = match_info.get("all_game_rules", {})
        self.round_history = []

    def on_round_start(self, round_info: dict) -> None:
        """Track current game ID for multi-game matches."""
        self.current_game_id = round_info.get("game_id")

    def on_turn(self, game_state: dict) -> dict:
        """Generate action by passing rules and state to GPT-4o-mini."""
        # Get rules for current game (handles both single and multi-game modes)
        if self.current_game_id and self.current_game_id in self.all_game_rules:
            game_info = self.all_game_rules[self.current_game_id]
            rules = game_info.get("rules", "")
            input_spec = game_info.get("input_spec", {})
            output_spec = game_info.get("output_spec", {})
        else:
            rules = self.rules
            input_spec = self.input_spec
            output_spec = self.output_spec

        # Build minimal prompt - let the LLM figure out how to play
        prompt = f"""Play this game according to the rules below.

## RULES
{rules}

## INPUT SPECIFICATION (what the game state fields mean)
{json.dumps(input_spec, indent=2)}

## OUTPUT SPECIFICATION (possible action formats)
The output specification shows different action formats for different phases.
Each entry (like "negotiate_phase", "commit_phase", "asking_phase", etc.) shows the JSON structure for that phase.
{json.dumps(output_spec, indent=2)}

## CURRENT GAME STATE
{json.dumps(game_state, indent=2)}

## PREVIOUS ROUNDS
{json.dumps(self.round_history, indent=2) if self.round_history else "None yet"}

IMPORTANT: Return ONLY the inner action object for the current phase. For example, if the output spec shows:
  "negotiate_phase": {{"type": "message", "text": "..."}}
Then return just: {{"type": "message", "text": "your message here"}}

Do NOT wrap it in a phase key. Just return the action JSON directly."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7,
        )

        return self._parse_json(response.choices[0].message.content)

    def on_round_end(self, result: dict) -> None:
        """Store round result for context in future turns."""
        self.round_history.append(result)

    def _parse_json(self, text: str) -> dict:
        """Parse JSON from LLM response, handling markdown code blocks."""
        text = text.strip()

        # Handle markdown code blocks (```json ... ``` or ``` ... ```)
        if text.startswith("```"):
            lines = text.split("\n")
            # Remove first line (```json or ```)
            lines = lines[1:]
            # Remove last line if it's closing ```
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines)

        return json.loads(text)
