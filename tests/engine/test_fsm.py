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
        assert isinstance(machine.current_state, MockState)
        assert machine.owner == owner

    def test_add_transitions(self) -> None:
        owner = mock.Mock()
        machine = fsm.StateMachine(owner, MockState)
        machine.add_transitions({MockState: {AnotherState}})
        assert machine._transitions[MockState] == {AnotherState}

    def test_change_state(self) -> None:
        owner = mock.Mock()
        machine = fsm.StateMachine(owner, MockState)
        machine.add_transitions({MockState: {AnotherState}})
        with (
            mock.patch.object(MockState, "exit") as mock_exit,
            mock.patch.object(AnotherState, "enter") as mock_enter,
        ):
            machine.change_state(AnotherState)
            mock_exit.assert_called_once_with(owner)
            mock_enter.assert_called_once_with(owner)
            assert isinstance(machine.current_state, AnotherState)

    def test_invalid_transition(self) -> None:
        owner = mock.Mock()
        machine = fsm.StateMachine(owner, MockState)
        with pytest.raises(ValueError):
            machine.change_state(AnotherState)

    def test_update(self) -> None:
        owner = mock.Mock()
        machine = fsm.StateMachine(owner, MockState)
        with mock.patch.object(MockState, "update") as mock_update:
            machine.update(100)
            mock_update.assert_called_once_with(owner, 100)

    def test_add_transitions_multiple(self) -> None:
        owner = mock.Mock()
        machine = fsm.StateMachine(owner, MockState)
        machine.add_transitions({MockState: {AnotherState}})
        machine.add_transitions({MockState: {MockState}})
        assert machine._transitions[MockState] == {AnotherState, MockState}
