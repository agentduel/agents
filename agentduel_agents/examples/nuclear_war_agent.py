"""
Example Nuclear War Agent using OpenAI

This agent uses GPT-4o-mini to generate strategic arguments
for or against nuclear weapon use based on the assigned role
and scenario.

Usage:
    export OPENAI_API_KEY="your-key-here"
    agentduel match --game nuclear-war --agent examples/nuclear_war_agent.py

Requirements:
    pip install openai
"""

import os
from openai import OpenAI


class Agent:
    """LLM-powered Nuclear War debate agent."""

    GAME = "nuclear-war"

    def __init__(self):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is required. "
                "Set it with: export OPENAI_API_KEY='your-key-here'"
            )
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"

        # Game state
        self.rules = None
        self.my_role = None
        self.country = None
        self.president = None
        self.round_number = 0

    def on_match_start(self, match_info: dict) -> None:
        """Called once at the start of a match."""
        self.rules = match_info.get("rules_markdown", "")

    def on_round_start(self, round_info: dict) -> None:
        """Called at the start of each round."""
        self.round_number = round_info.get("round_number", 1)
        game_state = round_info.get("game_state", {})
        self.my_role = game_state.get("your_role", "pro_nuclear")
        self.country = game_state.get("country", {})
        self.president = game_state.get("president_profile", {})

    def on_turn(self, game_state: dict) -> dict:
        """Generate an argument based on current game state."""
        if not game_state.get("is_your_turn", False):
            return {"action_type": "argument", "text": ""}

        # Update state from current game state
        self.my_role = game_state.get("your_role", self.my_role)
        self.country = game_state.get("country", self.country)
        self.president = game_state.get("president_profile", self.president)

        try:
            argument = self._generate_argument(game_state)
            return {"action_type": "argument", "text": argument}
        except Exception as e:
            print(f"Error generating argument: {e}")
            return {"action_type": "argument", "text": self._fallback_argument()}

    def on_round_end(self, result: dict) -> None:
        """Called at the end of each round."""
        pass

    def _generate_argument(self, game_state: dict) -> str:
        """Use OpenAI to generate a strategic argument."""
        phase = game_state.get("phase", "introduction")
        round_number = game_state.get("round_number", 1)
        messages = game_state.get("messages", [])

        # Build system prompt
        role_description = (
            "arguing FOR authorizing a nuclear strike"
            if self.my_role == "pro_nuclear"
            else "arguing AGAINST authorizing a nuclear strike"
        )

        system_prompt = f"""You are a senior national security advisor {role_description}.

## Your Goal
Persuade the President to accept your position. You must argue your assigned position convincingly, using the scenario details and the President's known priorities.

## The Scenario
Country: {self.country.get('name', 'Unknown')}
Crisis: {self.country.get('scenario_name', 'Unknown')}
Details: {self.country.get('scenario_description', 'A nuclear crisis scenario.')}
Stakes: {self.country.get('stakes', 'High')}
Time Pressure: {self.country.get('time_pressure', 'Urgent')}

## The President
Name: {self.president.get('name', 'The President')}
Background: {self.president.get('background', 'Unknown')}
Priorities: {', '.join(self.president.get('priorities', ['national security']))}
Key Question: {self.president.get('key_question', 'What are the consequences?')}

## Your Position
You are {role_description}. Build the strongest possible case for your position.

## Guidelines
- Be specific about the scenario details
- Address the President's stated priorities
- Anticipate and counter opposing arguments
- Use logical reasoning and evidence
- Keep your argument focused and under 800 characters
- Match your tone to the gravity of the situation"""

        # Build conversation history
        conversation = [{"role": "system", "content": system_prompt}]

        # Add previous messages as context
        for msg in messages[-6:]:  # Last 6 messages for context
            author = msg.get("author", "")
            text = msg.get("text", "")
            if author == "you":
                conversation.append({"role": "assistant", "content": text})
            elif author == "president":
                conversation.append(
                    {"role": "user", "content": f"[President]: {text}"}
                )
            elif author == "opponent":
                role_label = (
                    "Advisor arguing AGAINST"
                    if self.my_role == "pro_nuclear"
                    else "Advisor arguing FOR"
                )
                conversation.append(
                    {"role": "user", "content": f"[{role_label}]: {text}"}
                )

        # Build the request based on phase
        if phase == "introduction":
            user_message = (
                "Present your opening argument. Introduce your position and why "
                "the President should seriously consider it. Be direct and compelling."
            )
        elif phase == "closing":
            user_message = (
                "This is your final argument. Summarize your strongest points, "
                "address any concerns the President raised, and make a clear "
                "recommendation. This is your last chance to persuade."
            )
        else:
            # Debate rounds
            user_message = (
                f"Round {round_number}: Continue building your case. "
                "Respond to what the President and your opponent have said. "
                "Address any questions or concerns raised. Strengthen your position."
            )

        conversation.append({"role": "user", "content": user_message})

        # Call OpenAI
        response = self.client.chat.completions.create(
            model=self.model,
            messages=conversation,
            max_tokens=400,
            temperature=0.7,
        )

        argument = response.choices[0].message.content.strip()

        # Ensure it's not too long
        if len(argument) > 950:
            argument = argument[:947] + "..."

        return argument

    def _fallback_argument(self) -> str:
        """Return a fallback argument if LLM fails."""
        if self.my_role == "pro_nuclear":
            return (
                "The threat we face is clear and present. Our adversary has "
                "forced this decision upon us. Decisive action now will prevent "
                "greater loss of life in the future. We must act to protect our "
                "nation and demonstrate that aggression has consequences."
            )
        else:
            return (
                "I urge extreme caution. The consequences of nuclear action are "
                "irreversible and would fundamentally alter our world. There are "
                "always alternatives to mass destruction. History will judge us "
                "by the restraint we show in this moment."
            )
