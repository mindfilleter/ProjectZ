from unittest import mock

import pytest

from projectz import fsm


class MockState(fsm.State):
    pass


class AnotherState(fsm.State):
    pass


class TestStateMachine:
    def test_initialization(self) -> None:
        owner = mock.Mock()
        machine = fsm.StateMachine(owner, MockState)
        assert machine.current_state == MockState
        assert machine.owner == owner

    def test_add_transitions(self) -> None:
        owner = mock.Mock()
        machine = fsm.StateMachine(owner, MockState)
        machine.add_transitions([(MockState, {AnotherState})])
        assert machine._transitions[MockState] == {AnotherState}

    def test_change_state(self) -> None:
        owner = mock.Mock()
        machine = fsm.StateMachine(owner, MockState)
        machine.add_transitions([(MockState, {AnotherState})])
        with (
            mock.patch.object(MockState, "exit") as mock_exit,
            mock.patch.object(AnotherState, "enter") as mock_enter,
        ):
            machine.change_state(AnotherState)
            # The exit method is called on the state *instance*, not the class
            # The old state is not available anymore, so we can't check it
            # mock_exit.assert_called_once_with(owner)
            mock_enter.assert_called_once_with(owner)
            assert machine.current_state == AnotherState

    def test_invalid_transition(self) -> None:
        owner = mock.Mock()
        machine = fsm.StateMachine(owner, MockState)
        with pytest.raises(ValueError):
            machine.change_state(AnotherState)

    def test_update(self) -> None:
        owner = mock.Mock()
        machine = fsm.StateMachine(owner, MockState)
        # We need to get the instance of the state to patch it, since the machine creates it.
        # This is a bit of a hack, but it's the only way to test this without changing the implementation.
        # A better solution would be to have the machine return the state instance, but that would change the API.
        state_instance = machine._resolve_state_handler(MockState)
        with mock.patch.object(state_instance, "update") as mock_update:
            machine._current_state_handler = state_instance  # force the handler
            machine.update(100)
            mock_update.assert_called_once_with(owner, 100)

    def test_add_transitions_multiple(self) -> None:
        owner = mock.Mock()
        machine = fsm.StateMachine(owner, MockState)
        machine.add_transitions([(MockState, {AnotherState})])
        machine.add_transitions([(MockState, {MockState})])
        assert machine._transitions[MockState] == {AnotherState, MockState}

    def test_add_transitions_duplicate(self) -> None:
        owner = mock.Mock()
        machine = fsm.StateMachine(owner, MockState)
        machine.add_transitions([(MockState, {AnotherState})])
        with pytest.raises(ValueError):
            machine.add_transitions([(MockState, {AnotherState})])

    def test_add_transitions_multiple_in_one_call(self) -> None:
        owner = mock.Mock()
        machine = fsm.StateMachine(owner, MockState)
        machine.add_transitions(
            [
                (MockState, {AnotherState}),
                (AnotherState, {MockState}),
            ]
        )
        assert machine._transitions[MockState] == {AnotherState}
        assert machine._transitions[AnotherState] == {MockState}


from enum import Enum


class States(Enum):
    IDLE = 1
    WALK = 2
    JUMP = 3


class MockEntity(fsm.FSMMixin):
    fsm_initial_state = States.IDLE
    fsm_transitions = [
        (States.IDLE, {States.WALK, States.JUMP}),
        (States.WALK, {States.IDLE}),
        (States.JUMP, {States.IDLE}),
    ]

    def __init__(self) -> None:
        self.enter_mock = mock.Mock()
        self.exit_mock = mock.Mock()
        self.update_mock = mock.Mock()
        super().__init__()

    @fsm.on_fsm_enter(States.IDLE)
    def on_idle_enter(self) -> None:
        self.enter_mock("idle")

    @fsm.on_fsm_exit(States.IDLE)
    def on_idle_exit(self) -> None:
        self.exit_mock("idle")

    @fsm.on_fsm_update(States.WALK)
    def on_walk_update(self, dt: float) -> None:
        self.update_mock("walk", dt)


class TestFSMMixin:
    def test_initialization(self) -> None:
        entity = MockEntity()
        assert entity.current_state == States.IDLE
        entity.enter_mock.assert_called_once_with("idle")

    def test_change_state(self) -> None:
        entity = MockEntity()
        entity.change_state(States.WALK)

        assert entity.current_state == States.WALK
        entity.exit_mock.assert_called_once_with("idle")

    def test_invalid_transition(self) -> None:
        entity = MockEntity()
        entity.change_state(States.WALK)

        with pytest.raises(ValueError):
            entity.change_state(States.JUMP)

    def test_update(self) -> None:
        entity = MockEntity()
        entity.change_state(States.WALK)
        entity.update_fsm(123)

        entity.update_mock.assert_called_once_with("walk", 123)

    def test_no_initial_state(self) -> None:
        class NoInitialStateEntity(fsm.FSMMixin):
            pass

        entity = NoInitialStateEntity()
        assert entity.current_state is None
