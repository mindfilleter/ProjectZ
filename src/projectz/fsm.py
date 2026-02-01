import logging
from typing import Any
from typing import Dict
from typing import Set
from typing import Tuple
from typing import Type

logger = logging.getLogger(__name__)


class State:
    """Base class for FSM states."""

    def enter(self, obj: Any) -> None:
        """Called when entering the state."""
        pass

    def update(self, obj: Any, dt: float) -> None:
        """Called every frame/tick."""
        pass

    def exit(self, obj: Any) -> None:
        """Called when exiting the state."""
        pass


class StateMachine:
    def __init__(self, owner: Any, initial_state: Type[State]):
        self.owner = owner
        # Internal map: { FromStateClass: {ToStateClass, ...} }
        self._transitions: Dict[Type[State], Set[Type[State]]] = {}

        self.current_state = initial_state()
        logger.debug("FSM Initialized for %s in state %s", self.owner, initial_state.__name__)
        self.current_state.enter(self.owner)

    def add_transitions(self, *transitions: Tuple[Type[State], Set[Type[State]]]) -> None:
        """
        Accepts any number of (from_state, {to_states}) tuples.
        Raises ValueError if a transition from->to is already defined.

        Example:
            fsm.add_transitions(
                (Idle, {Walk, Jump}),
                (Walk, {Idle})
            )
        """
        for from_state, to_states in transitions:
            existing = self._transitions.get(from_state, set())
            # Check for overlapping transitions
            duplicates = existing.intersection(to_states)

            if duplicates:
                dup_names = ", ".join(s.__name__ for s in duplicates)
                raise ValueError(
                    f"Duplicate transitions detected for {from_state.__name__}: "
                    f"Already allowed to transition to: {{{dup_names}}}"
                )

            # If valid, update the mapping
            self._transitions.setdefault(from_state, set()).update(to_states)

    def change_state(self, new_state_class: Type[State]) -> None:
        """Performs a transition to a new state class if allowed."""
        current_class = self.current_state.__class__
        allowed = self._transitions.get(current_class, set())

        if new_state_class not in allowed:
            raise ValueError(
                f"Invalid transition for {self.owner}: "
                f"{current_class.__name__} -> {new_state_class.__name__}"
            )

        logger.debug(
            "%s transition: %s -> %s", self.owner, current_class.__name__, new_state_class.__name__
        )

        self.current_state.exit(self.owner)
        self.current_state = new_state_class()
        self.current_state.enter(self.owner)

    def update(self, dt: float) -> None:
        """Updates the current active state."""
        self.current_state.update(self.owner, dt)
