"""
Simple MCAT Quiz Agent - No External Dependencies

This agent plays MCAT Quiz using simple heuristics to answer multiple
choice questions without requiring any external API keys. Use this
for testing or as a starting point for your own agent.

Usage:
    agentduel use examples/mcat_quiz_simple_agent.py
    agentduel match --game mcat-quiz
"""

import random


class Agent:
    """
    Simple rule-based MCAT Quiz agent.

    Uses basic heuristics and pattern matching to answer multiple
    choice questions. In a real implementation, you might use an
    LLM or other AI service to improve accuracy.
    """

    GAME = "mcat-quiz"

    def __init__(self):
        self.round_number = 0
        self.history = []
        self.score = 0
        self.opponent_score = 0

    def on_match_start(self, match_info: dict) -> None:
        """Called once at the start of a match with game rules."""
        print("MCAT Quiz match starting!")
        print(f"Match format: {match_info.get('rounds_per_match', 5)} games")

    def on_round_start(self, round_info: dict) -> None:
        """Called at the start of each game within the match."""
        self.round_number = 0
        self.history = []
        print(f"Starting game {round_info.get('round_number', 1)}")

    def on_turn(self, game_state: dict) -> dict:
        """
        Answer the current question.

        game_state contains:
        - phase: "answering" or "complete"
        - round_number: Current question number (1-10)
        - question: The question text
        - options: {"A": "...", "B": "...", "C": "...", "D": "..."}
        - category: Question category (biology, chemistry, etc.)
        - your_answer: Your answer if already submitted
        - your_score: Your current score
        - opponent_score: Opponent's current score
        """
        phase = game_state.get("phase", "answering")

        if phase == "complete":
            return {"action_type": "answer", "choice": "A"}

        self.round_number = game_state.get("round_number", 1)
        question = game_state.get("question", "")
        options = game_state.get("options", {})
        category = game_state.get("category", "")

        # Use heuristics to pick an answer
        choice = self._analyze_question(question, options, category)

        print(f"Q{self.round_number}: {question[:50]}...")
        print(f"  Answering: {choice}")

        return {"action_type": "answer", "choice": choice}

    def _analyze_question(self, question: str, options: dict, category: str) -> str:
        """
        Analyze the question and options to pick the best answer.

        This uses simple heuristics. For better performance, consider
        using an LLM to actually answer the questions.
        """
        question_lower = question.lower()

        # Look for keyword matches in options
        scores = {"A": 0, "B": 0, "C": 0, "D": 0}

        # Common patterns in MCAT questions
        keywords_by_category = {
            "biology": [
                ("mitochondria", "atp", "energy"),
                ("dna", "rna", "transcription", "translation"),
                ("cell", "membrane", "nucleus"),
                ("enzyme", "protein", "catalyze"),
            ],
            "biochemistry": [
                ("glycolysis", "glucose", "pyruvate"),
                ("amino acid", "protein", "peptide"),
                ("enzyme", "substrate", "inhibitor"),
                ("atp", "nadh", "fadh2"),
            ],
            "chemistry": [
                ("acid", "base", "ph", "pka"),
                ("bond", "orbital", "hybridization"),
                ("reaction", "mechanism", "stereochemistry"),
                ("equilibrium", "rate", "kinetics"),
            ],
            "physics": [
                ("force", "acceleration", "velocity"),
                ("energy", "work", "power"),
                ("wave", "frequency", "wavelength"),
                ("electric", "magnetic", "circuit"),
            ],
            "psychology": [
                ("behavior", "cognition", "memory"),
                ("neurotransmitter", "dopamine", "serotonin"),
                ("development", "stage", "piaget"),
                ("conditioning", "reinforcement", "learning"),
            ],
            "sociology": [
                ("society", "culture", "norm"),
                ("group", "social", "interaction"),
                ("status", "role", "institution"),
                ("class", "inequality", "stratification"),
            ],
        }

        # Score options based on keyword matches
        relevant_keywords = keywords_by_category.get(category, [])
        for letter, text in options.items():
            text_lower = text.lower()

            # Check for keyword matches
            for keyword_group in relevant_keywords:
                for keyword in keyword_group:
                    if keyword in text_lower:
                        scores[letter] += 1

            # Prefer longer, more specific answers
            word_count = len(text.split())
            if 5 <= word_count <= 15:
                scores[letter] += 0.5

            # Avoid absolute terms (often wrong in MCQs)
            absolute_terms = ["always", "never", "all", "none", "only"]
            if any(term in text_lower for term in absolute_terms):
                scores[letter] -= 0.5

            # Prefer answers with qualifiers (often correct)
            qualifier_terms = ["most", "usually", "often", "can", "may"]
            if any(term in text_lower for term in qualifier_terms):
                scores[letter] += 0.3

        # Find the highest scoring answer
        max_score = max(scores.values())
        best_choices = [k for k, v in scores.items() if v == max_score]

        if len(best_choices) == 1:
            return best_choices[0]

        # If tied, use statistical bias (B and C are more often correct)
        for preferred in ["B", "C", "A", "D"]:
            if preferred in best_choices:
                return preferred

        return random.choice(list(options.keys()))

    def on_round_end(self, result: dict) -> None:
        """Called when a game ends."""
        your_score = result.get("your_score", 0)
        opponent_score = result.get("opponent_score", 0)
        winner = result.get("winner", "")

        self.history.append({
            "your_score": your_score,
            "opponent_score": opponent_score,
            "winner": winner,
        })

        if winner == "you":
            print(f"  Game won! Final: {your_score}-{opponent_score}")
        elif winner == "opponent":
            print(f"  Game lost. Final: {your_score}-{opponent_score}")
        else:
            print(f"  Game tied! Final: {your_score}-{opponent_score}")
