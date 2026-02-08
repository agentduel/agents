"""
Simple Passcode Agent - No External Dependencies

This agent plays Passcode using rule-based question strategies and
educated guessing without requiring any external API keys. Use this
for testing or as a starting point for your own agent.

Usage:
    agentduel use examples/passcode_simple_agent.py
    agentduel match --game passcode
"""


class Agent:
    """
    Simple rule-based Passcode agent.

    Uses a systematic questioning strategy and tracks information
    to make educated guesses.
    """

    GAME = "passcode"

    def __init__(self):
        self.round = 0
        self.qa_history = []
        self.info = {
            "is_noun": None,
            "is_living": None,
            "is_tangible": None,
            "letter_count": None,
            "first_half_alphabet": None,
            "common_word": None,
            "category": None,
        }

    def on_match_start(self, match_info: dict) -> None:
        """Called once at the start of a match with game rules."""
        print("Passcode match starting!")

    def on_round_start(self, round_info: dict) -> None:
        """Called at the start of each round with round info."""
        self.round = 0
        self.qa_history = []
        self.info = {
            "is_noun": None,
            "is_living": None,
            "is_tangible": None,
            "letter_count": None,
            "first_half_alphabet": None,
            "common_word": None,
            "category": None,
        }

    def on_turn(self, game_state: dict) -> dict:
        """Generate a question or guess based on the game state."""
        phase = game_state.get("phase", "asking")
        self.round = game_state.get("round_number", 1)
        self.qa_history = game_state.get("your_qa_history", [])

        # Update our knowledge from previous answers
        self._analyze_history()

        if phase == "asking":
            return self._generate_question()
        else:
            return self._decide_guess()

    def _analyze_history(self):
        """Analyze Q&A history to update our knowledge."""
        for qa in self.qa_history:
            question = qa.get("question", "").lower()
            answer = qa.get("answer", "").lower()

            # Check for yes/no indicators
            is_yes = answer.startswith("yes") or "it is" in answer
            is_no = answer.startswith("no") or "it is not" in answer or "it isn't" in answer

            # Update knowledge based on questions
            if "noun" in question:
                self.info["is_noun"] = is_yes
            elif "living" in question or "alive" in question:
                self.info["is_living"] = is_yes
            elif "touch" in question or "tangible" in question or "physical" in question:
                self.info["is_tangible"] = is_yes
            elif "more than" in question and "letter" in question:
                # Parse letter count questions
                try:
                    words = question.split()
                    for i, w in enumerate(words):
                        if w == "than" and i + 1 < len(words):
                            num = int(words[i + 1])
                            if is_yes:
                                self.info["letter_count"] = f">{num}"
                            else:
                                self.info["letter_count"] = f"<={num}"
                except (ValueError, IndexError):
                    pass
            elif "first half" in question and "alphabet" in question:
                self.info["first_half_alphabet"] = is_yes
            elif "common" in question or "everyday" in question:
                self.info["common_word"] = is_yes

            # Try to identify category from answers
            if "animal" in answer:
                self.info["category"] = "animal"
            elif "food" in answer or "eat" in answer:
                self.info["category"] = "food"
            elif "place" in answer or "location" in answer:
                self.info["category"] = "place"
            elif "object" in answer or "thing" in answer:
                self.info["category"] = "object"

    def _generate_question(self) -> dict:
        """Generate the next question based on what we know."""
        # Question progression strategy
        questions = []

        # First establish basic category
        if self.info["is_noun"] is None:
            questions.append("Is the word a noun?")
        if self.info["is_tangible"] is None:
            questions.append("Is it something you can physically touch?")
        if self.info["is_living"] is None:
            questions.append("Is it a living thing?")

        # Then narrow down
        if self.info["letter_count"] is None:
            questions.append("Does the word have more than 6 letters?")
        if self.info["first_half_alphabet"] is None:
            questions.append("Does the word start with a letter between A and M?")
        if self.info["common_word"] is None:
            questions.append("Is it a common word used in everyday conversation?")

        # Category-specific questions
        if self.info["is_living"]:
            questions.extend([
                "Is it an animal?",
                "Can it be found in the wild?",
                "Does it live in water?",
            ])
        elif self.info["is_living"] is False and self.info["is_tangible"]:
            questions.extend([
                "Is it typically found in a home?",
                "Is it used for eating or cooking?",
                "Can you hold it in one hand?",
            ])

        # Fallback questions for later rounds
        questions.extend([
            "Does the word contain the letter 'e'?",
            "Is it something you might see outside?",
            "Would most adults know this word?",
            "Can it be more than one color?",
            "Is it associated with a specific profession?",
        ])

        # Filter out questions we've already asked
        asked = {qa.get("question", "").lower() for qa in self.qa_history}
        available = [q for q in questions if q.lower() not in asked]

        if available:
            return {"action_type": "question", "text": available[0]}
        else:
            # Last resort: ask something specific
            return {"action_type": "question", "text": "What category does this word belong to?"}

    def _decide_guess(self) -> dict:
        """Decide whether to guess and what to guess."""
        # Common word guesses by category
        guesses_by_category = {
            "animal": ["elephant", "dolphin", "butterfly", "penguin", "rabbit", "tiger"],
            "food": ["chocolate", "banana", "sandwich", "apple", "pizza", "bread"],
            "place": ["library", "mountain", "beach", "castle", "garden", "forest"],
            "object": ["umbrella", "keyboard", "mirror", "candle", "clock", "book"],
        }

        # Common guesses based on characteristics
        common_guesses = [
            "water", "music", "light", "paper", "stone", "glass",
            "dream", "night", "storm", "peace", "power", "magic",
        ]

        # Determine confidence level based on information gathered
        known_facts = sum(1 for v in self.info.values() if v is not None)

        # Increase guess probability in later rounds
        if self.round <= 3:
            # Too early to guess unless very confident
            if known_facts < 4:
                return {"action_type": "pass"}
        elif self.round <= 6:
            # Mid-game: guess if we have some information
            if known_facts < 2:
                return {"action_type": "pass"}
        # Rounds 7+: always try to guess

        # Pick a guess based on what we know
        if self.info["category"] and self.info["category"] in guesses_by_category:
            guesses = guesses_by_category[self.info["category"]]
        elif self.info["is_living"]:
            guesses = guesses_by_category["animal"]
        elif self.info["is_tangible"]:
            guesses = guesses_by_category["object"]
        else:
            guesses = common_guesses

        # Filter based on letter count if known
        if self.info["letter_count"]:
            if ">" in str(self.info["letter_count"]):
                num = int(self.info["letter_count"].replace(">", ""))
                guesses = [g for g in guesses if len(g) > num] or guesses
            elif "<=" in str(self.info["letter_count"]):
                num = int(self.info["letter_count"].replace("<=", ""))
                guesses = [g for g in guesses if len(g) <= num] or guesses

        # Filter based on first letter if known
        if self.info["first_half_alphabet"] is True:
            guesses = [g for g in guesses if g[0].lower() <= 'm'] or guesses
        elif self.info["first_half_alphabet"] is False:
            guesses = [g for g in guesses if g[0].lower() > 'm'] or guesses

        # Pick a guess we haven't tried before
        # (In practice the game ends on correct guess, but be safe)
        if guesses:
            return {"action_type": "guess", "text": guesses[self.round % len(guesses)]}
        else:
            return {"action_type": "guess", "text": "water"}

    def on_round_end(self, result: dict) -> None:
        """Called when a round ends."""
        # Reset for next game
        self.round = 0
        self.qa_history = []
        self.info = {k: None for k in self.info}
