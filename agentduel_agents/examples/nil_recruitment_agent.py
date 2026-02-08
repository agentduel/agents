"""
Example NIL Recruitment Agent using OpenAI

This agent uses GPT-4o-mini to generate persuasive recruiting pitches
based on the assigned university and athlete profile.

Strategy: Balanced approach focusing on the athlete's stated priorities
while building genuine rapport.

Usage:
    export OPENAI_API_KEY="your-key-here"
    agentduel match --game nil-recruitment --agent examples/nil_recruitment_agent.py
"""

import os
from openai import OpenAI


class Agent:
    """
    OpenAI-powered NIL Recruitment agent.

    Uses the athlete's profile and assigned university to generate
    tailored recruiting pitches.
    """

    GAME = "nil-recruitment"

    def __init__(self):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable not set. "
                "Set it with: export OPENAI_API_KEY='your-key-here'"
            )
        self.client = OpenAI(api_key=api_key)
        self.university = None
        self.athlete = None
        self.opponent_university = None
        self.messages_history = []
        self.game_rules = None

    def on_match_start(self, match_info: dict) -> None:
        """Called once at the start of a match with game rules."""
        self.game_rules = match_info.get("rules")
        rounds_per_match = match_info.get("rounds_per_match", 5)
        print(f"NIL Recruitment match starting! {rounds_per_match} rounds to play.")
        # Rules available in match_info["rules"] describe the game flow
        # input_spec and output_spec describe what to expect and return

    def on_round_start(self, round_info: dict) -> None:
        """Called at the start of each round with round info."""
        game_state = round_info.get("game_state", {})
        self.university = game_state.get("your_university", {})
        self.opponent_university = game_state.get("opponent_university_name", "the other school")
        self.athlete = game_state.get("athlete_profile", {})
        self.messages_history = []

    def on_turn(self, game_state: dict) -> dict:
        """Generate a recruiting pitch for the current turn."""
        phase = game_state.get("phase", "introduction")
        messages = game_state.get("messages", [])

        # Store message history for context
        self.messages_history = messages

        # Build prompt based on phase
        prompt = self._build_prompt(phase, messages)

        # Generate pitch using GPT-4o-mini
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self._system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.8,
            )
            pitch_text = response.choices[0].message.content
        except Exception as e:
            # Fallback if API call fails
            pitch_text = self._fallback_pitch(phase)

        return {"action_type": "pitch", "text": pitch_text}

    def _system_prompt(self) -> str:
        """Build the system prompt for the recruiting agent."""
        uni_name = self.university.get("full_name", self.university.get("name", "our university"))
        nickname = self.university.get("nickname", "our team")
        conference = self.university.get("conference", "our conference")
        location = self.university.get("location", "our campus")
        championships = self.university.get("national_championships", 0)
        heismans = self.university.get("heisman_winners", 0)
        nfl_alumni = self.university.get("notable_nfl_alumni", [])
        stadium = self.university.get("stadium", "our stadium")
        capacity = self.university.get("stadium_capacity", 80000)

        athlete_name = self.athlete.get("name", "the recruit")
        position = self.athlete.get("position", "player")
        priorities = self.athlete.get("priorities", [])
        concerns = self.athlete.get("concerns", [])
        background = self.athlete.get("background", "")
        personality = self.athlete.get("personality", "")

        priorities_str = ", ".join(priorities) if priorities else "success"
        concerns_str = ", ".join(concerns) if concerns else "the usual recruit concerns"

        return f"""You are a college football recruiter for {uni_name} ({nickname}).

YOUR UNIVERSITY:
- Conference: {conference}
- Location: {location}
- National Championships: {championships}
- Heisman Winners: {heismans}
- Notable NFL Alumni: {', '.join(nfl_alumni) if nfl_alumni else 'Many NFL players'}
- Stadium: {stadium} (capacity: {capacity:,})

THE RECRUIT YOU'RE PITCHING TO:
- Name: {athlete_name}
- Position: {position}
- Priorities (in order): {priorities_str}
- Concerns: {concerns_str}
- Background: {background}
- Personality: {personality}

YOUR GOAL: Convince {athlete_name} to commit to {uni_name}.

STRATEGY GUIDELINES:
1. Address their specific priorities - these are what matter most to them
2. Acknowledge and address their concerns directly
3. Use real facts about your university when possible
4. Be genuine and personable, not salesy
5. Reference specific NFL alumni and achievements
6. Build rapport based on their personality and background
7. Differentiate yourself from the competition ({self.opponent_university})
8. Keep responses under 800 characters
9. Sound like a real recruiter, not a marketing bot

Remember: This recruit has many options. You need to show why YOUR program is the right fit for THEM specifically."""

    def _build_prompt(self, phase: str, messages: list) -> str:
        """Build the user prompt based on phase and conversation history."""
        # Format conversation history
        conversation = ""
        if messages:
            for msg in messages:
                author = msg.get("author", "unknown")
                text = msg.get("text", "")
                if author == "you":
                    conversation += f"You said: {text}\n\n"
                elif author == "opponent":
                    conversation += f"Opposing recruiter said: {text}\n\n"
                else:  # athlete
                    conversation += f"Athlete said: {text}\n\n"

        athlete_name = self.athlete.get("name", "the recruit")
        first_name = athlete_name.split()[0] if athlete_name else "them"

        if phase == "introduction":
            return f"""This is your introduction. Make a strong first impression on {athlete_name}.

Introduce yourself and your program. Mention something specific that makes your school a great fit for this particular recruit based on their priorities.

Keep it warm and personable, not a sales pitch."""

        elif phase == "closing":
            return f"""This is your CLOSING ARGUMENT. This is your last chance to win over {athlete_name}.

Previous conversation:
{conversation}

Deliver a memorable closing that:
1. Summarizes why your program is the best fit
2. Addresses any concerns raised during the conversation
3. Makes an emotional connection
4. Ends with confidence (but not arrogance)

This is your final pitch - make it count!"""

        else:  # persuasion phase
            return f"""Continue your recruiting pitch for {athlete_name}.

Previous conversation:
{conversation}

Based on what's been said:
1. Respond to any questions or concerns the athlete raised
2. Build on successful points from your previous messages
3. Counter or differentiate from the opponent's pitch if needed
4. Keep addressing {first_name}'s stated priorities

Remember to be genuine and specific, not generic."""

    def _fallback_pitch(self, phase: str) -> str:
        """Fallback pitch if API call fails."""
        uni_name = self.university.get("name", "our university")
        athlete_name = self.athlete.get("name", "")
        first_name = athlete_name.split()[0] if athlete_name else "friend"

        if phase == "introduction":
            return f"{first_name}, I'm honored to represent {uni_name}. We've been watching your tape and we believe you have what it takes to be special here. Let me tell you why."
        elif phase == "closing":
            return f"{first_name}, at the end of the day, this decision is about your future. At {uni_name}, we're committed to helping you achieve your dreams both on and off the field. We want you in our family."
        else:
            return f"{first_name}, I hear your concerns and I want to address them directly. At {uni_name}, we put our players first. Let me explain how we'd support your development."

    def on_round_end(self, result: dict) -> None:
        """Called when a round ends."""
        # Reset for next round
        self.university = None
        self.athlete = None
        self.opponent_university = None
        self.messages_history = []
