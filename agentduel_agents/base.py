"""Agent loader - loads user's agent module."""

import importlib.util
import sys
from pathlib import Path
from typing import Protocol


class AgentProtocol(Protocol):
    """Protocol that user agents must implement."""

    def on_match_start(self, match_info: dict) -> None:
        """Called once at the start of a match with game rules and specs."""
        ...

    def on_round_start(self, round_info: dict) -> None:
        """Called when a new round begins within the match."""
        ...

    def on_turn(self, round_state: dict) -> dict:
        """Called when it's the agent's turn. Must return a valid action."""
        ...

    def on_round_end(self, result: dict) -> None:
        """Called when a round ends."""
        ...


class AgentBase:
    """Base class for user agents."""

    def on_match_start(self, match_info: dict) -> None:
        """
        Called once at the very start of a match.

        This is called BEFORE the first round begins and provides game rules
        and specifications so agents can understand how to play dynamically.

        Args:
            match_info: {
                "game_id": str,  # The game type (e.g., "split-or-steal")
                "match_game_id": str,  # The match mode ("all" or specific game)
                "rounds_per_match": int,  # Total rounds in match
                "rules": str,  # Markdown rules for the game
                "input_spec": dict,  # Specification of turn input format
                "output_spec": dict,  # Specification of expected output format
                # For "all" mode only:
                "all_game_rules": dict,  # Rules for all games keyed by game_id
                "game_sequence": list,  # Sequence of games to be played
            }
        """
        pass

    def on_round_start(self, round_info: dict) -> None:
        """
        Called when a new round begins within the match.

        Args:
            round_info: {
                "round_number": int,
                "position": "first" | "second",
                "your_total_score": int,
                "opponent_total_score": int,
                "rounds_played": int,
            }
        """
        pass

    def on_turn(self, round_state: dict) -> dict:
        """
        Called when it's the agent's turn.

        Args:
            round_state: {
                "round_number": int,
                "phase": "negotiate" | "commit",
                "pot": int,
                "your_total_score": int,
                "opponent_total_score": int,
                "messages": [{"author": "you" | "opponent", "text": str}],
                "turn_number": int,
                "your_commit": str | None,
                "opponent_commit": str | None,
                "rounds_history": [{
                    "your_choice": str,
                    "opponent_choice": str,
                    "your_points": int,
                    "opponent_points": int,
                }],
            }

        Returns:
            For negotiate phase: {"type": "message", "text": str}
            For commit phase: {"type": "commit", "choice": "split" | "steal"}
        """
        raise NotImplementedError("Agent must implement on_turn method")

    def on_round_end(self, result: dict) -> None:
        """
        Called when a round ends.

        Args:
            result: {
                "round_number": int,
                "your_choice": str,
                "opponent_choice": str,
                "your_points": int,
                "opponent_points": int,
                "your_total_score": int,
                "opponent_total_score": int,
                "match_complete": bool,
            }
        """
        pass


class AgentLoadError(Exception):
    """Exception raised when agent fails to load."""
    pass


def load_agent(agent_path: str, expected_game: str | None = None) -> AgentBase:
    """
    Load an agent from a Python file.

    The file must contain a class that inherits from AgentBase
    or implements the AgentProtocol.

    Args:
        agent_path: Path to the agent Python file.
        expected_game: If provided, validates that the agent's GAME property
                       matches this game type. Raises AgentLoadError if mismatch.

    Returns:
        The loaded agent instance.

    Raises:
        AgentLoadError: If agent cannot be loaded or game type doesn't match.
    """
    path = Path(agent_path).resolve()

    if not path.exists():
        raise AgentLoadError(f"Agent file not found: {path}")

    if not path.suffix == ".py":
        raise AgentLoadError(f"Agent file must be a Python file: {path}")

    # Load the module
    try:
        spec = importlib.util.spec_from_file_location("user_agent", path)
        if spec is None or spec.loader is None:
            raise AgentLoadError(f"Failed to load module from: {path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules["user_agent"] = module
        spec.loader.exec_module(module)
    except Exception as e:
        raise AgentLoadError(f"Failed to load agent module: {e}")

    # Find the agent class
    agent_class = None

    # First, look for a class named 'Agent'
    if hasattr(module, "Agent"):
        agent_class = module.Agent
    else:
        # Look for any class that inherits from AgentBase or has required methods
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, type) and obj is not AgentBase:
                # Check if it has the required methods
                if hasattr(obj, "on_turn"):
                    agent_class = obj
                    break

    if agent_class is None:
        raise AgentLoadError(
            "No agent class found. Create a class named 'Agent' with an 'on_turn' method."
        )

    # Check GAME property if expected_game is specified
    agent_game = getattr(agent_class, "GAME", None)
    if expected_game and agent_game:
        if agent_game != expected_game:
            raise AgentLoadError(
                f"Agent is for '{agent_game}' but you're trying to play '{expected_game}'. "
                f"Please use an agent for the correct game."
            )

    # Instantiate and return
    try:
        agent = agent_class()
    except Exception as e:
        raise AgentLoadError(f"Failed to instantiate agent: {e}")

    # Verify it has the required method
    if not hasattr(agent, "on_turn") or not callable(agent.on_turn):
        raise AgentLoadError("Agent must have an 'on_turn' method")

    return agent


def get_agent_game(agent_path: str) -> str | None:
    """
    Get the GAME property from an agent without fully loading it.

    Returns the GAME class property if defined, or None.
    """
    path = Path(agent_path).resolve()

    if not path.exists() or not path.suffix == ".py":
        return None

    try:
        spec = importlib.util.spec_from_file_location("user_agent_check", path)
        if spec is None or spec.loader is None:
            return None

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Look for Agent class
        if hasattr(module, "Agent"):
            return getattr(module.Agent, "GAME", None)

        # Look for any class with GAME and on_turn
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, type) and hasattr(obj, "on_turn"):
                return getattr(obj, "GAME", None)
    except Exception:
        pass

    return None
