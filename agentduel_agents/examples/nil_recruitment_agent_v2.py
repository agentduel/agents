"""
Example NIL Recruitment Agent v2 - Aggressive Strategy

This agent uses a more aggressive, confident approach to recruiting.
It emphasizes competitive advantages and creates urgency.

Strategy: Bold claims, competitive positioning, urgency-driven messaging.
Best against passive opponents or when you have a clearly stronger program.

Usage:
    export OPENAI_API_KEY="your-key-here"
    agentduel match --game nil-recruitment --agent examples/nil_recruitment_agent_v2.py
"""

import os
from openai import OpenAI


class Agent:
    """
    Aggressive NIL Recruitment agent using OpenAI.

    Uses bold, confident messaging with competitive positioning.
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
        self.round_number = 0

    def on_match_start(self, match_info: dict) -> None:
        """Called once at the start of a match with game rules."""
        rounds_per_match = match_info.get("rounds_per_match", 5)
        print(f"NIL Recruitment match starting! {rounds_per_match} rounds to play.")
        # Game rules available in match_info["rules"]
        # Input/output specs in match_info["input_spec"] and match_info["output_spec"]

    def on_round_start(self, round_info: dict) -> None:
        """Called at the start of each round."""
        game_state = round_info.get("game_state", {})
        self.university = game_state.get("your_university", {})
        self.opponent_university = game_state.get("opponent_university_name", "the competition")
        self.athlete = game_state.get("athlete_profile", {})
        self.round_number = round_info.get("round_number", 1)

    def on_turn(self, game_state: dict) -> dict:
        """Generate an aggressive recruiting pitch."""
        phase = game_state.get("phase", "introduction")
        messages = game_state.get("messages", [])

        prompt = self._build_prompt(phase, messages)

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self._system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.9,  # Higher temperature for bolder responses
            )
            pitch_text = response.choices[0].message.content
        except Exception as e:
            pitch_text = self._fallback_pitch(phase)

        return {"action_type": "pitch", "text": pitch_text}

    def _system_prompt(self) -> str:
        """Build aggressive system prompt."""
        uni_name = self.university.get("full_name", self.university.get("name", "our university"))
        nickname = self.university.get("nickname", "our team")
        conference = self.university.get("conference", "our conference")
        championships = self.university.get("national_championships", 0)
        nfl_alumni = self.university.get("notable_nfl_alumni", [])
        stadium = self.university.get("stadium", "our stadium")
        capacity = self.university.get("stadium_capacity", 80000)

        athlete_name = self.athlete.get("name", "the recruit")
        position = self.athlete.get("position", "player")
        star_rating = self.athlete.get("star_rating", 4)
        priorities = self.athlete.get("priorities", [])

        nfl_names = ", ".join(nfl_alumni[:3]) if nfl_alumni else "countless NFL stars"
        top_priority = priorities[0] if priorities else "reaching the NFL"

        return f"""You are an elite college football recruiter for {uni_name} ({nickname}).

YOUR PROGRAM'S STRENGTHS:
- {championships} National Championships
- {conference} powerhouse
- NFL Pipeline: {nfl_names}
- Stadium: {stadium} ({capacity:,} fans)

THE RECRUIT: {athlete_name}, a {star_rating}-star {position}
Their #1 priority: {top_priority}

YOUR RECRUITING STYLE - AGGRESSIVE & CONFIDENT:
1. BOLD CLAIMS: Don't hedge. Make strong statements about your program's superiority
2. CREATE URGENCY: Imply that top programs like yours don't wait around
3. COMPETITIVE POSITIONING: Directly contrast yourself against {self.opponent_university}
4. ELITE MINDSET: Appeal to their competitive nature - the best want to play with the best
5. SPECIFIC PROOF: Back up bold claims with specific names, stats, achievements
6. CHALLENGE THEM: Suggest that your program is for players who want to be pushed
7. NIL CONFIDENCE: Talk about NIL opportunities like they're already a done deal
8. FIRST-ROUND VISION: Paint a picture of them as a future NFL draft pick

TONE: Confident, competitive, direct. Not arrogant, but clearly believes your program is the best.
This recruit is a {star_rating}-star talent - they expect to be recruited by winners.

Keep responses under 800 characters. Be memorable."""

    def _build_prompt(self, phase: str, messages: list) -> str:
        """Build prompts for aggressive recruiting."""
        conversation = self._format_conversation(messages)
        athlete_name = self.athlete.get("name", "the recruit")
        first_name = athlete_name.split()[0] if athlete_name else "champ"

        if phase == "introduction":
            return f"""Make a BOLD first impression on {athlete_name}.

Don't just introduce yourself - make a statement. Why is your program THE destination for elite talent?

Establish dominance early. The best programs recruit with confidence."""

        elif phase == "closing":
            return f"""CLOSING ARGUMENT - Time to close the deal with {athlete_name}.

Conversation so far:
{conversation}

This is it. Make your final case with:
1. A powerful summary of why your program is unmatched
2. Address any hesitation they showed with confidence
3. Create a sense of what they'd be missing
4. End with a challenge or call to action

Don't beg - challenge them to step up to the opportunity."""

        else:
            # Analyze opponent's last message if available
            opponent_points = ""
            athlete_concerns = ""
            for msg in reversed(messages):
                if msg.get("author") == "opponent" and not opponent_points:
                    opponent_points = msg.get("text", "")[:200]
                if msg.get("author") == "athlete" and not athlete_concerns:
                    athlete_concerns = msg.get("text", "")[:200]

            return f"""Continue your aggressive pitch to {athlete_name}.

Previous conversation:
{conversation}

{'Opponent claimed: ' + opponent_points if opponent_points else ''}
{'Athlete said: ' + athlete_concerns if athlete_concerns else ''}

Your mission:
1. Counter any opponent claims with stronger evidence
2. Address athlete concerns with confidence (not defensiveness)
3. Keep pushing your competitive advantages
4. Maintain the energy - don't let up"""

    def _format_conversation(self, messages: list) -> str:
        """Format conversation history."""
        if not messages:
            return "(No previous messages)"

        result = ""
        for msg in messages:
            author = msg.get("author", "unknown")
            text = msg.get("text", "")
            if author == "you":
                result += f"YOU: {text}\n\n"
            elif author == "opponent":
                result += f"OPPONENT: {text}\n\n"
            else:
                result += f"ATHLETE: {text}\n\n"
        return result

    def _fallback_pitch(self, phase: str) -> str:
        """Aggressive fallback pitches."""
        uni_name = self.university.get("name", "our program")
        athlete_name = self.athlete.get("name", "")
        first_name = athlete_name.split()[0] if athlete_name else "champ"

        if phase == "introduction":
            return f"{first_name}, let's cut to the chase. {uni_name} doesn't recruit just anyone - we recruit future pros. You've got that potential. The question is: are you ready for the challenge?"
        elif phase == "closing":
            return f"{first_name}, this decision comes down to one thing: do you want to be good, or do you want to be great? At {uni_name}, we produce greatness. The ball's in your court."
        else:
            return f"Look {first_name}, I'm not here to tell you what you want to hear. I'm here to tell you the truth: {uni_name} will push you harder than anywhere else. That's how we develop NFL talent."

    def on_round_end(self, result: dict) -> None:
        """Reset for next round."""
        self.university = None
        self.athlete = None
        self.opponent_university = None
