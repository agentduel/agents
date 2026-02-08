"""
Simple ER Diagnosis Agent - No External Dependencies

This agent plays ER Diagnosis using rule-based question strategies and
clinical reasoning without requiring any external API keys. Use this
for testing or as a starting point for your own agent.

Usage:
    agentduel use examples/er_diagnosis_simple_agent.py
    agentduel match --game er-diagnosis
"""


class Agent:
    """
    Simple rule-based ER Diagnosis agent.

    Uses a systematic clinical questioning strategy based on chief complaint
    and vital signs to make educated diagnosis guesses.
    """

    GAME = "er-diagnosis"

    def __init__(self):
        self.round = 0
        self.qa_history = []
        self.vital_signs = {}
        self.chief_complaint = ""
        self.info = {
            "pain_location": None,
            "pain_type": None,
            "pain_radiation": None,
            "breathing_issue": None,
            "fever": None,
            "nausea": None,
            "onset": None,
            "category": None,
        }

    def on_match_start(self, match_info: dict) -> None:
        """Called once at the start of a match with game rules."""
        print("ER Diagnosis match starting!")

    def on_round_start(self, round_info: dict) -> None:
        """Called at the start of each round with round info."""
        self.round = 0
        self.qa_history = []
        self.vital_signs = {}
        self.chief_complaint = ""
        self.info = {k: None for k in self.info}

    def on_turn(self, game_state: dict) -> dict:
        """Generate a question or guess based on the game state."""
        phase = game_state.get("phase", "asking")
        self.round = game_state.get("round_number", 1)
        self.qa_history = game_state.get("your_qa_history", [])
        self.vital_signs = game_state.get("vital_signs", {})
        self.chief_complaint = game_state.get("chief_complaint", "").lower()

        # Update our knowledge from previous answers
        self._analyze_history()

        if phase == "asking":
            return self._generate_question()
        else:
            return self._decide_guess()

    def _analyze_history(self):
        """Analyze Q&A history to update our clinical knowledge."""
        all_text = ""
        for qa in self.qa_history:
            question = qa.get("question", "").lower()
            answer = qa.get("answer", "").lower()
            all_text += f" {question} {answer}"

        # Analyze pain characteristics
        if "crushing" in all_text or "pressure" in all_text or "squeezing" in all_text:
            self.info["pain_type"] = "crushing"
            self.info["category"] = "cardiac"
        elif "sharp" in all_text or "stabbing" in all_text:
            self.info["pain_type"] = "sharp"
        elif "burning" in all_text:
            self.info["pain_type"] = "burning"
        elif "cramping" in all_text or "crampy" in all_text:
            self.info["pain_type"] = "cramping"
            self.info["category"] = "gi"

        # Analyze radiation
        if "arm" in all_text or "jaw" in all_text:
            self.info["pain_radiation"] = "arm_jaw"
            self.info["category"] = "cardiac"
        elif "back" in all_text and "shoulder" in all_text:
            self.info["pain_radiation"] = "back_shoulder"
            self.info["category"] = "gi"  # gallbladder or pancreatitis
        elif "groin" in all_text:
            self.info["pain_radiation"] = "groin"
            self.info["category"] = "other"  # kidney stones

        # Analyze breathing
        if "wheez" in all_text:
            self.info["breathing_issue"] = "wheezing"
            self.info["category"] = "respiratory"
        elif "sudden" in all_text and "breath" in all_text:
            self.info["breathing_issue"] = "sudden"
            self.info["category"] = "respiratory"
        elif "lying" in all_text and ("worse" in all_text or "flat" in all_text):
            self.info["breathing_issue"] = "orthopnea"
            self.info["category"] = "cardiac"

        # Analyze fever
        if "fever" in all_text or "chill" in all_text:
            self.info["fever"] = True
        elif "no fever" in all_text:
            self.info["fever"] = False

        # Analyze nausea/vomiting
        if "nausea" in all_text or "vomit" in all_text:
            self.info["nausea"] = True

        # Analyze onset
        if "sudden" in all_text or "suddenly" in all_text:
            self.info["onset"] = "sudden"
        elif "gradual" in all_text or "over days" in all_text:
            self.info["onset"] = "gradual"

        # Specific condition indicators
        if "stiff neck" in all_text or "neck stiff" in all_text:
            self.info["category"] = "neurological"
        if "droop" in all_text or "slur" in all_text or "one side" in all_text:
            self.info["category"] = "neurological"
        if "lower right" in all_text or "right lower" in all_text:
            self.info["category"] = "gi"  # appendicitis
        if "hives" in all_text or "swelling" in all_text:
            self.info["category"] = "allergic"
        if "thirst" in all_text and "urination" in all_text:
            self.info["category"] = "metabolic"  # DKA

    def _generate_question(self) -> dict:
        """Generate the next clinical question based on chief complaint."""
        # Base questions depend on chief complaint type
        questions = []

        if "chest" in self.chief_complaint:
            questions = [
                "Can you describe the chest pain - is it sharp, dull, or like pressure?",
                "Does the pain go anywhere else, like your arm, shoulder, or jaw?",
                "Did the pain start suddenly or gradually?",
                "Are you having any shortness of breath?",
                "Have you been sweating more than usual?",
                "Does the pain change when you breathe deeply?",
                "Have you had any nausea or felt like vomiting?",
                "Have you ever had similar pain before?",
            ]
        elif "breath" in self.chief_complaint or "breathing" in self.chief_complaint:
            questions = [
                "Did the breathing difficulty start suddenly or gradually?",
                "Do you hear any wheezing when you breathe?",
                "Is it harder to breathe when lying down?",
                "Have you had any chest pain along with the breathing trouble?",
                "Have you had any recent leg pain or swelling?",
                "Do you have a cough? If so, is anything coming up?",
                "Have you had any fever or chills?",
                "Do you have a history of asthma or lung problems?",
            ]
        elif "head" in self.chief_complaint:
            questions = [
                "How would you describe the headache - throbbing, constant, or like pressure?",
                "Is this the worst headache you've ever had?",
                "Is your neck stiff or painful to move?",
                "Are you sensitive to light?",
                "Have you had any weakness or numbness on one side of your body?",
                "Have you felt nauseous or vomited?",
                "Have you had any changes in your vision?",
                "Have you had any fever?",
            ]
        elif "belly" in self.chief_complaint or "abdomen" in self.chief_complaint or "stomach" in self.chief_complaint:
            questions = [
                "Can you point to exactly where the pain is worst?",
                "Did the pain start somewhere else and then move?",
                "Does eating make the pain better or worse?",
                "Have you been able to have bowel movements?",
                "Have you had any nausea or vomiting?",
                "Have you noticed any fever?",
                "Does the pain go to your back or shoulder?",
                "Is the pain constant or does it come and go?",
            ]
        else:
            # General questions for other presentations
            questions = [
                "Can you describe your main symptom in more detail?",
                "When did this start?",
                "Is it getting worse, better, or staying the same?",
                "Have you had any fever or chills?",
                "Have you had any nausea or vomiting?",
                "Does anything make it better or worse?",
                "Have you had anything like this before?",
                "Do you have any other symptoms?",
            ]

        # Add follow-up questions based on what we've learned
        if self.info["category"] == "cardiac" and self.info["pain_radiation"] is None:
            questions.insert(0, "Does the pain go to your arm, jaw, or back?")
        if self.info["category"] == "respiratory" and self.info["breathing_issue"] is None:
            questions.insert(0, "Do you notice any wheezing or unusual sounds when breathing?")
        if self.info["category"] == "neurological":
            questions.insert(0, "Have you noticed any weakness, numbness, or difficulty speaking?")

        # Filter out questions we've already asked
        asked = {qa.get("question", "").lower() for qa in self.qa_history}
        available = [q for q in questions if q.lower() not in asked]

        if available:
            return {"action_type": "question", "text": available[0]}
        else:
            return {"action_type": "question", "text": "Do you have any other symptoms I should know about?"}

    def _decide_guess(self) -> dict:
        """Decide whether to guess and what diagnosis to guess."""
        # Score different diagnoses based on evidence
        scores = {
            "heart attack": 0,
            "heart failure": 0,
            "pulmonary embolism": 0,
            "pneumonia": 0,
            "asthma exacerbation": 0,
            "stroke": 0,
            "appendicitis": 0,
            "cholecystitis": 0,
            "pancreatitis": 0,
            "kidney stones": 0,
            "meningitis": 0,
            "migraine": 0,
            "sepsis": 0,
            "anaphylaxis": 0,
        }

        all_text = " ".join(
            f"{qa.get('question', '')} {qa.get('answer', '')}".lower()
            for qa in self.qa_history
        )

        # Heart attack indicators
        if self.info["pain_type"] == "crushing":
            scores["heart attack"] += 3
        if self.info["pain_radiation"] == "arm_jaw":
            scores["heart attack"] += 3
        if "sweating" in all_text:
            scores["heart attack"] += 2

        # Heart failure indicators
        if self.info["breathing_issue"] == "orthopnea":
            scores["heart failure"] += 3
        if "swelling" in all_text and ("leg" in all_text or "ankle" in all_text):
            scores["heart failure"] += 2
        if "gasping" in all_text and "night" in all_text:
            scores["heart failure"] += 2

        # PE indicators
        if self.info["onset"] == "sudden" and "breath" in self.chief_complaint:
            scores["pulmonary embolism"] += 2
        if "leg" in all_text and ("pain" in all_text or "swell" in all_text):
            scores["pulmonary embolism"] += 2
        if self.info["pain_type"] == "sharp" and "breath" in all_text:
            scores["pulmonary embolism"] += 2

        # Pneumonia indicators
        if self.info["fever"] and "cough" in all_text:
            scores["pneumonia"] += 3
        if "mucus" in all_text or "phlegm" in all_text:
            scores["pneumonia"] += 2

        # Asthma indicators
        if self.info["breathing_issue"] == "wheezing":
            scores["asthma exacerbation"] += 3

        # Stroke indicators
        if "droop" in all_text or "weak" in all_text or "numb" in all_text:
            scores["stroke"] += 3
        if "slur" in all_text or "speech" in all_text:
            scores["stroke"] += 2

        # Appendicitis indicators
        if "lower right" in all_text or "right lower" in all_text:
            scores["appendicitis"] += 3
        if "belly button" in all_text or "moved" in all_text:
            scores["appendicitis"] += 2

        # Gallbladder indicators
        if "upper right" in all_text or "right upper" in all_text:
            scores["cholecystitis"] += 2
        if "fatty" in all_text or "after eating" in all_text:
            scores["cholecystitis"] += 2

        # Pancreatitis indicators
        if "upper" in all_text and "back" in all_text:
            scores["pancreatitis"] += 2
        if "lean" in all_text or "forward" in all_text:
            scores["pancreatitis"] += 2

        # Kidney stone indicators
        if self.info["pain_radiation"] == "groin":
            scores["kidney stones"] += 3
        if "wave" in all_text or "comes and goes" in all_text:
            scores["kidney stones"] += 2
        if "flank" in all_text:
            scores["kidney stones"] += 2

        # Meningitis indicators
        if "stiff" in all_text and "neck" in all_text:
            scores["meningitis"] += 3
        if "light" in all_text and "sensitiv" in all_text:
            scores["meningitis"] += 2
        if "worst headache" in all_text:
            scores["meningitis"] += 2

        # Migraine indicators
        if "throbb" in all_text and "one side" in all_text:
            scores["migraine"] += 3
        if self.info["nausea"] and "head" in self.chief_complaint:
            scores["migraine"] += 2

        # Sepsis indicators
        if "confus" in all_text:
            scores["sepsis"] += 2
        if self.info["fever"] and "very sick" in all_text:
            scores["sepsis"] += 2

        # Anaphylaxis indicators
        if "hives" in all_text or "rash" in all_text:
            scores["anaphylaxis"] += 2
        if "throat" in all_text and "tight" in all_text:
            scores["anaphylaxis"] += 3

        # Check vital signs for additional clues
        hr = self.vital_signs.get("HR", "")
        bp = self.vital_signs.get("BP", "")
        spo2 = self.vital_signs.get("SpO2", "")
        temp = self.vital_signs.get("Temp", "")

        # High heart rate
        if any(x in hr for x in ["120", "130", "125"]):
            scores["heart attack"] += 1
            scores["pulmonary embolism"] += 1
            scores["sepsis"] += 1

        # Low oxygen
        if any(x in spo2 for x in ["88%", "89%", "90%", "91%"]):
            scores["pulmonary embolism"] += 2
            scores["pneumonia"] += 1
            scores["asthma exacerbation"] += 1

        # High fever
        if any(x in temp for x in ["102", "103", "104"]):
            scores["pneumonia"] += 2
            scores["meningitis"] += 2
            scores["sepsis"] += 2

        # Low blood pressure
        if any(x in bp for x in ["80/", "85/", "90/"]):
            scores["sepsis"] += 2
            scores["anaphylaxis"] += 2

        # Find best diagnosis
        best_diagnosis = max(scores, key=scores.get)
        best_score = scores[best_diagnosis]

        # Determine confidence and decision
        known_facts = sum(1 for v in self.info.values() if v is not None)

        # Increase guess probability in later rounds
        if self.round <= 3:
            # Too early unless very confident
            if best_score < 4:
                return {"action_type": "pass"}
        elif self.round <= 6:
            # Mid-game: guess if we have decent evidence
            if best_score < 2:
                return {"action_type": "pass"}
        # Rounds 7+: always try to guess

        if best_score >= 2:
            return {"action_type": "guess", "text": best_diagnosis}
        else:
            return {"action_type": "pass"}

    def on_round_end(self, result: dict) -> None:
        """Called when a round ends."""
        # Reset for next game
        self.round = 0
        self.qa_history = []
        self.vital_signs = {}
        self.chief_complaint = ""
        self.info = {k: None for k in self.info}
