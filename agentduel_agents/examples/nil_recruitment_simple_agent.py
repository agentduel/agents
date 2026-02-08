"""
Simple NIL Recruitment Agent - No External Dependencies

This agent generates pitches using simple rules and templates without
requiring any external API keys. Use this for testing or as a starting
point for your own agent.

Usage:
    agentduel use examples/nil_recruitment_simple_agent.py
    agentduel match --game nil-recruitment
"""


class Agent:
    """
    Simple rule-based NIL Recruitment agent.

    Uses templates and athlete profile info to generate pitches
    without requiring external APIs.
    """

    GAME = "nil-recruitment"

    def __init__(self):
        self.university = None
        self.athlete = None
        self.opponent_university = None
        self.pitch_count = 0

    def on_match_start(self, match_info: dict) -> None:
        """Called once at the start of a match with game rules."""
        rounds_per_match = match_info.get("rounds_per_match", 5)
        print(f"NIL Recruitment match starting! {rounds_per_match} rounds to play.")
        # Game rules available in match_info["rules"]

    def on_round_start(self, round_info: dict) -> None:
        """Called at the start of each round with round info."""
        game_state = round_info.get("game_state", {})
        self.university = game_state.get("your_university", {})
        self.opponent_university = game_state.get("opponent_university_name", "the other school")
        self.athlete = game_state.get("athlete_profile", {})
        self.pitch_count = 0

    def on_turn(self, game_state: dict) -> dict:
        """Generate a recruiting pitch for the current turn."""
        self.pitch_count += 1
        phase = game_state.get("phase", "introduction")
        messages = game_state.get("messages", [])

        # Get athlete and university info
        athlete_name = self.athlete.get("name", "friend")
        first_name = athlete_name.split()[0] if athlete_name else "friend"
        position = self.athlete.get("position", "player")
        priorities = self.athlete.get("priorities", [])
        concerns = self.athlete.get("concerns", [])

        uni_name = self.university.get("full_name", self.university.get("name", "our university"))
        nickname = self.university.get("nickname", "our team")
        conference = self.university.get("conference", "our conference")
        championships = self.university.get("national_championships", 0)
        nfl_alumni = self.university.get("notable_nfl_alumni", [])

        # Generate pitch based on phase
        if phase == "introduction":
            pitch = self._intro_pitch(first_name, position, uni_name, nickname, conference)
        elif phase == "closing":
            pitch = self._closing_pitch(first_name, uni_name, nickname, priorities)
        else:
            pitch = self._persuasion_pitch(
                first_name, position, uni_name, nickname,
                championships, nfl_alumni, priorities, concerns, messages
            )

        return {"action_type": "pitch", "text": pitch}

    def _intro_pitch(self, name, position, uni_name, nickname, conference):
        """Generate an introduction pitch."""
        return (
            f"{name}, I'm honored to be here representing {uni_name}. "
            f"The {nickname} have been tracking your development and we're impressed "
            f"with what you've accomplished. As a {position} prospect, you'd be joining "
            f"one of the most competitive programs in the {conference}. "
            f"Let me tell you why this is the place where your dreams become reality."
        )

    def _closing_pitch(self, name, uni_name, nickname, priorities):
        """Generate a closing argument."""
        priority_text = ""
        if priorities:
            top_priority = priorities[0]
            if "nfl" in top_priority.lower():
                priority_text = "We've sent countless players to the NFL, and you could be next. "
            elif "academic" in top_priority.lower():
                priority_text = "Our academic programs will set you up for life beyond football. "
            elif "nil" in top_priority.lower() or "money" in top_priority.lower():
                priority_text = "Our NIL program is among the best in the nation. "

        return (
            f"{name}, at the end of the day, this decision shapes your future. "
            f"{priority_text}"
            f"At {uni_name}, you're not just another recruit - you're family. "
            f"The {nickname} are ready to invest in your success, both on and off the field. "
            f"We want you. We believe in you. Come be a champion with us."
        )

    def _persuasion_pitch(self, name, position, uni_name, nickname,
                         championships, nfl_alumni, priorities, concerns, messages):
        """Generate a persuasion round pitch."""
        parts = [f"{name}, let me address what matters most to you."]

        # Address top priority
        if priorities:
            top = priorities[0].lower()
            if "nfl" in top or "draft" in top:
                if nfl_alumni:
                    alumni_names = ", ".join(nfl_alumni[:2])
                    parts.append(
                        f"You want to reach the NFL? Look at {alumni_names} - "
                        f"they walked these same halls. Our development program is elite."
                    )
                else:
                    parts.append(
                        "Our track record of developing NFL talent speaks for itself. "
                        "We know how to prepare players for the next level."
                    )
            elif "academic" in top:
                parts.append(
                    "Our academic support is world-class. You'll graduate "
                    "with a degree that matters, while competing at the highest level."
                )
            elif "nil" in top or "money" in top:
                parts.append(
                    "Our NIL collective is one of the strongest in college football. "
                    "We'll make sure you're taken care of financially."
                )
            elif "championship" in top or "win" in top:
                if championships > 0:
                    parts.append(
                        f"We've won {championships} national championships. "
                        f"We compete for titles every year. That's the standard here."
                    )
                else:
                    parts.append(
                        "We're building something special here. "
                        "You could be part of our championship run."
                    )

        # Address a concern
        if concerns:
            concern = concerns[0].lower()
            if "playing time" in concern:
                parts.append(
                    "I know you're thinking about playing time. "
                    "With your talent, you'll compete immediately."
                )
            elif "distance" in concern or "home" in concern:
                parts.append(
                    "Being away from home is tough, but our program is like family. "
                    "You'll never feel alone here."
                )
            elif "coaching" in concern or "scheme" in concern:
                parts.append(
                    "Our coaching staff is dedicated to maximizing your potential. "
                    "They've developed countless stars."
                )

        return " ".join(parts)

    def on_round_end(self, result: dict) -> None:
        """Called when a round ends."""
        self.university = None
        self.athlete = None
        self.opponent_university = None
        self.pitch_count = 0
