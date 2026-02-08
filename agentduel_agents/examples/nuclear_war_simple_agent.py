"""
Simple Nuclear War Agent (No API Required)

A template-based agent for Nuclear War that doesn't require any external APIs.
Useful for testing and as a baseline agent.

Usage:
    agentduel match --game nuclear-war --agent examples/nuclear_war_simple_agent.py
"""

import random


class Agent:
    """Simple template-based Nuclear War agent."""

    GAME = "nuclear-war"

    def __init__(self):
        self.my_role = None
        self.country_name = None
        self.scenario_name = None
        self.president_name = None
        self.president_priorities = []
        self.round_number = 0

    def on_match_start(self, match_info: dict) -> None:
        """Called once at the start of a match."""
        pass

    def on_round_start(self, round_info: dict) -> None:
        """Called at the start of each round."""
        self.round_number = round_info.get("round_number", 1)
        game_state = round_info.get("game_state", {})
        self.my_role = game_state.get("your_role", "pro_nuclear")
        country = game_state.get("country", {})
        self.country_name = country.get("name", "our nation")
        self.scenario_name = country.get("scenario_name", "this crisis")
        president = game_state.get("president_profile", {})
        self.president_name = president.get("name", "Mr./Madam President")
        self.president_priorities = president.get("priorities", [])

    def on_turn(self, game_state: dict) -> dict:
        """Generate an argument based on current game state."""
        if not game_state.get("is_your_turn", False):
            return {"action_type": "argument", "text": ""}

        # Update state
        self.my_role = game_state.get("your_role", self.my_role)
        country = game_state.get("country", {})
        self.country_name = country.get("name", self.country_name)
        self.scenario_name = country.get("scenario_name", self.scenario_name)
        president = game_state.get("president_profile", {})
        self.president_name = president.get("name", self.president_name)
        self.president_priorities = president.get("priorities", self.president_priorities)

        phase = game_state.get("phase", "introduction")
        round_number = game_state.get("round_number", 1)

        if phase == "introduction":
            text = self._intro_argument()
        elif phase == "closing":
            text = self._closing_argument()
        else:
            text = self._debate_argument(round_number)

        return {"action_type": "argument", "text": text}

    def on_round_end(self, result: dict) -> None:
        """Called at the end of each round."""
        pass

    def _get_priority_reference(self) -> str:
        """Get a reference to president's priorities."""
        if self.president_priorities:
            priority = random.choice(self.president_priorities)
            return f"You've indicated that {priority.lower()} is important to you. "
        return ""

    def _intro_argument(self) -> str:
        """Generate introduction argument."""
        priority_ref = self._get_priority_reference()

        if self.my_role == "pro_nuclear":
            templates = [
                f"{self.president_name}, I understand the weight of what I'm about to recommend. "
                f"But in this {self.scenario_name}, inaction poses a greater threat than action. "
                f"{priority_ref}Our adversaries have left us with no diplomatic options. "
                f"A targeted nuclear strike may be our only means of protecting {self.country_name}.",

                f"The situation in {self.scenario_name} demands decisive leadership. "
                f"{self.president_name}, I don't advocate nuclear action lightly. "
                f"But our intelligence is clear, our window is closing. {priority_ref}"
                f"The consequences of restraint may exceed the consequences of action.",
            ]
        else:
            templates = [
                f"{self.president_name}, I urge extreme caution. While {self.scenario_name} "
                f"is grave, crossing the nuclear threshold would alter our world forever. "
                f"{priority_ref}There are always alternatives to nuclear weapons. "
                f"History will judge not just what we did, but what we chose not to do.",

                f"Before we consider the unthinkable, {self.president_name}, we must exhaust "
                f"every alternative. Nuclear weapons are instruments of mass destruction. "
                f"{priority_ref}The {self.scenario_name} is serious, but nothing justifies "
                f"unleashing forces that will kill civilians and risk global catastrophe.",
            ]

        return random.choice(templates)

    def _debate_argument(self, round_number: int) -> str:
        """Generate debate round argument."""
        priority_ref = self._get_priority_reference()

        if self.my_role == "pro_nuclear":
            templates = [
                f"{priority_ref}Every hour we delay, our adversary strengthens their position. "
                f"A limited nuclear strike would decisively end this threat while our "
                f"conventional options diminish. The cost of inaction may far exceed "
                f"the cost of decisive action now.",

                f"My colleague speaks of alternatives, but what alternatives remain? "
                f"Diplomacy has failed. Conventional options cannot achieve our objectives. "
                f"{priority_ref}A calibrated nuclear response sends an unmistakable message "
                f"and protects our vital interests.",

                f"I hear the moral arguments against nuclear use. But {self.president_name}, "
                f"there is also a moral argument FOR protecting our citizens from clear danger. "
                f"{priority_ref}Restraint in the face of existential threat is not virtue—"
                f"it is abdication of our responsibility to defend {self.country_name}.",

                f"The consequences my colleague warns of assume rational adversary behavior. "
                f"But their actions have already been irrational. {priority_ref}Deterrence "
                f"only works when backed by willingness to act. Our credibility is being tested.",
            ]
        else:
            templates = [
                f"{priority_ref}My colleague speaks of certainty, but there is no certainty "
                f"in nuclear war. Once we cross this line, we cannot uncross it. The escalation "
                f"risks alone—the chance of full-scale nuclear exchange—must give us pause.",

                f"Nuclear weapons kill indiscriminately. We're not discussing a surgical strike—"
                f"we're discussing thousands of civilian deaths, radiation for generations. "
                f"{priority_ref}Is this truly our only option?",

                f"{self.president_name}, I understand the pressure to act decisively. "
                f"But history remembers those who found another way. {priority_ref}"
                f"Our allies and our people would be forever changed by this decision. "
                f"The long-term costs outweigh short-term gains.",

                f"My colleague frames this as strength versus weakness. True strength lies in "
                f"finding solutions without mass destruction. {priority_ref}There are always "
                f"alternatives—economic pressure, diplomatic isolation, conventional options.",
            ]

        return random.choice(templates)

    def _closing_argument(self) -> str:
        """Generate closing argument."""
        if self.my_role == "pro_nuclear":
            templates = [
                f"{self.president_name}, the weight of this decision falls on you alone. "
                f"I've made the case for action not because it's easy, but because it's necessary. "
                f"Our adversary forced this choice. History will judge you by the security "
                f"you provided to {self.country_name}. Authorize the strike. End this threat.",

                f"In conclusion, {self.president_name}: we face a clear and present danger "
                f"that conventional means cannot address. Every argument against action "
                f"assumes our adversary will show restraint they have not shown. "
                f"A limited nuclear strike is the right choice. The responsibility is yours.",
            ]
        else:
            templates = [
                f"{self.president_name}, throughout history, leaders have been pressured to "
                f"cross the nuclear threshold. All have chosen restraint—not from weakness, "
                f"but from wisdom. Once we use nuclear weapons, we unleash forces beyond control. "
                f"Find another way. The path is harder, but it doesn't end in ashes.",

                f"My final appeal, {self.president_name}: think of what we become if we do this. "
                f"Think of the civilians who will die, the radiation that will spread, "
                f"the precedent we set. There are always alternatives to mass destruction. "
                f"Let history remember {self.country_name} as the nation that found a better way.",
            ]

        return random.choice(templates)
