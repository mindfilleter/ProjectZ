"""
Finite State Machine (FSM) Module.

This module provides a flexible FSM implementation that supports two usage patterns:
1. Object-Oriented: Using concrete ``State`` classes and a ``StateMachine`` engine.
2. Declarative Mixin: Using the ``FSMMixin`` and decorators to define state logic
   directly within the consuming class.

:author: Gemini
:license: MIT
"""

import inspect
import logging
from enum import Enum
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple
from typing import Type
from typing import Union

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format="[%(levelname)s] %(message)s")

StateID = Union[Enum, Type[Any], str]


class State:
    """
    Base class for FSM states in the Object-Oriented style.

    Subclasses should override the lifecycle methods to implement behavior.
    """

    def enter(self, owner: Any) -> None:
        """
        Called once when the state machine enters this state.

        :param owner: The object (actor/entity) that owns this FSM.
        :type owner: Any
        """
        pass

    def update(self, owner: Any, dt: float) -> None:
        """
        Called every frame or tick while this state is active.

        :param owner: The object (actor/entity) that owns this FSM.
        :type owner: Any
        :param dt: Delta time since the last frame.
        :type dt: float
        """
        pass

    def exit(self, owner: Any) -> None:
        """
        Called once when the state machine exits this state.

        :param owner: The object (actor/entity) that owns this FSM.
        :type owner: Any
        """
        pass


class StateMachine:
    """
    A concrete StateMachine engine that manages state transitions and updates.

    This class can be used standalone by creating ``State`` subclasses, or
    via the ``FSMMixin`` which wraps this engine.
    """

    def __init__(self, owner: Any, initial_state: Optional[StateID] = None):
        """
        Initialize the StateMachine.

        :param owner: The object that this state machine controls.
        :type owner: Any
        :param initial_state: The optional starting state. If provided,
                              ``change_state`` is called immediately.
        :type initial_state: StateID, optional
        """
        self.owner = owner
        self._transitions: Dict[StateID, Set[StateID]] = {}

        self._current_state_id: Optional[StateID] = None
        self._current_state_handler: Optional[State] = None

        self._state_registry: Dict[StateID, State] = {}

        if initial_state:
            self.change_state(initial_state)

    def add_transitions(self, transitions: List[Tuple[StateID, Set[StateID]]]) -> None:
        """
        Register valid transitions between states.

        :param transitions: A list of tuples, where each tuple contains a source
                            state and a set of allowed destination states.
        :type transitions: List[Tuple[StateID, Set[StateID]]]
        :raises ValueError: If a duplicate transition definition is detected.
        """
        for from_state, to_states in transitions:
            if from_state in self._transitions:
                existing = self._transitions[from_state]
                duplicates = existing.intersection(to_states)
                if duplicates:
                    raise ValueError(f"Duplicate FSM transitions for {from_state}: {duplicates}")
                existing.update(to_states)
            else:
                self._transitions[from_state] = set(to_states)

    def register_state(self, state_id: StateID, state_instance: State) -> None:
        """
        Register a pre-instantiated state object for a specific ID.

        This is primarily used by the ``FSMMixin`` to register adapter states,
        or for singleton state management.

        :param state_id: The identifier for the state.
        :type state_id: StateID
        :param state_instance: The concrete State object instance.
        :type state_instance: State
        """
        self._state_registry[state_id] = state_instance

    def change_state(self, new_state_id: StateID) -> None:
        """
        Transition from the current state to a new state.

        Performs validation against the registered transition graph.
        Triggers ``exit()`` on the old state and ``enter()`` on the new state.

        :param new_state_id: The target state identifier.
        :type new_state_id: StateID
        :raises ValueError: If the transition is not allowed defined in ``add_transitions``.
        """
        if self._current_state_id is not None:
            allowed = self._transitions.get(self._current_state_id, set())
            if new_state_id not in allowed:
                raise ValueError(
                    f"Invalid FSM transition for {self.owner}: "
                    f"{self._get_name(self._current_state_id)} -> {self._get_name(new_state_id)}"
                )

            if self._current_state_handler:
                self._current_state_handler.exit(self.owner)

        logger.info(
            "FSM Transition: %s -> %s",
            self._get_name(self._current_state_id),
            self._get_name(new_state_id),
        )

        handler = self._resolve_state_handler(new_state_id)

        self._current_state_id = new_state_id
        self._current_state_handler = handler

        if self._current_state_handler:
            self._current_state_handler.enter(self.owner)

    def update(self, dt: float) -> None:
        """
        Trigger the update loop for the current state.

        :param dt: Delta time.
        :type dt: float
        """
        if self._current_state_handler:
            self._current_state_handler.update(self.owner, dt)

    def _resolve_state_handler(self, state_id: StateID) -> State:
        if state_id in self._state_registry:
            return self._state_registry[state_id]

        if isinstance(state_id, type) and issubclass(state_id, State):
            return state_id()

        raise ValueError(f"Could not resolve a State Handler for state ID: {state_id}")

    def _get_name(self, state_id: Optional[StateID]) -> str:
        if state_id is None:
            return "None"
        if isinstance(state_id, Enum):
            return state_id.name
        if hasattr(state_id, "__name__"):
            return state_id.__name__
        return str(state_id)

    @property
    def current_state(self) -> Optional[StateID]:
        """
        Get the identifier of the currently active state.

        :return: The current state identifier.
        :rtype: StateID
        """
        return self._current_state_id


def on_fsm_enter(state: StateID) -> Callable[..., Any]:
    """
    Decorator to register a method as the ENTER handler for a specific state.

    :param state: The state identifier associated with this handler.
    :type state: StateID
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        if not hasattr(func, "_fsm_meta"):
            setattr(func, "_fsm_meta", [])
        getattr(func, "_fsm_meta").append(("enter", state))
        return func

    return decorator


def on_fsm_exit(state: StateID) -> Callable[..., Any]:
    """
    Decorator to register a method as the EXIT handler for a specific state.

    :param state: The state identifier associated with this handler.
    :type state: StateID
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        if not hasattr(func, "_fsm_meta"):
            setattr(func, "_fsm_meta", [])
        getattr(func, "_fsm_meta").append(("exit", state))
        return func

    return decorator


def on_fsm_update(state: StateID) -> Callable[..., Any]:
    """
    Decorator to register a method as the UPDATE handler for a specific state.

    :param state: The state identifier associated with this handler.
    :type state: StateID
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        if not hasattr(func, "_fsm_meta"):
            setattr(func, "_fsm_meta", [])
        getattr(func, "_fsm_meta").append(("update", state))
        return func

    return decorator


class _MethodAdapterState(State):
    """
    Internal Adapter to wrap method callbacks into a State object.
    """

    def __init__(self) -> None:
        self.enter_fn: Optional[Callable[[], None]] = None
        self.exit_fn: Optional[Callable[[], None]] = None
        self.update_fn: Optional[Callable[[float], None]] = None

    def enter(self, owner: Any) -> None:
        if self.enter_fn:
            self.enter_fn()

    def exit(self, owner: Any) -> None:
        if self.exit_fn:
            self.exit_fn()

    def update(self, owner: Any, dt: float) -> None:
        if self.update_fn:
            self.update_fn(dt)


class FSMMixin:
    """
    A Mixin that adds declarative FSM capabilities to a class.

    It automatically inspects methods decorated with ``@on_fsm_...`` and
    builds the underlying ``StateMachine``.

    **Usage:**
    1. Inherit from ``FSMMixin``.
    2. Define ``fsm_transitions`` and ``fsm_initial_state``.
    3. Decorate methods to handle state logic.
    """

    fsm_transitions: List[Tuple[StateID, Set[StateID]]] = []
    fsm_initial_state: Optional[StateID] = None

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.fsm = StateMachine(self)

        self._fsm_build_graph()

        if self.fsm_initial_state:
            self.fsm.change_state(self.fsm_initial_state)
        else:
            logger.warning(f"No initial state defined for {self.__class__.__name__}")

    def _fsm_build_graph(self) -> None:
        self.fsm.add_transitions(self.fsm_transitions)

        handlers: Dict[StateID, _MethodAdapterState] = {}

        for _, method in inspect.getmembers(self.__class__, predicate=inspect.isfunction):
            if hasattr(method, "_fsm_meta"):
                bound_method = method.__get__(self)
                for event_type, state_id in method._fsm_meta:
                    if state_id not in handlers:
                        handlers[state_id] = _MethodAdapterState()

                    adapter = handlers[state_id]
                    if event_type == "enter":
                        adapter.enter_fn = bound_method
                    elif event_type == "exit":
                        adapter.exit_fn = bound_method
                    elif event_type == "update":
                        adapter.update_fn = bound_method

        for state_id, adapter in handlers.items():
            self.fsm.register_state(state_id, adapter)

    def change_state(self, new_state: StateID) -> None:
        """
        Change the current state of the FSM.

        :param new_state: The target state identifier.
        :type new_state: StateID
        """
        self.fsm.change_state(new_state)

    def update_fsm(self, dt: float) -> None:
        """
        Update the FSM. Should be called every frame.

        :param dt: Delta time.
        :type dt: float
        """
        self.fsm.update(dt)

    @property
    def current_state(self) -> Optional[StateID]:
        """
        Get the current active state.

        :return: The current state identifier.
        :rtype: StateID
        """
        return self.fsm.current_state
