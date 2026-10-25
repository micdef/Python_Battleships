import pytest
from dataclasses import FrozenInstanceError

from ComputerPlayer import ComputerPlayer
from Game import Game
from HumanPlayer import HumanPlayer
from Player import ShotResult
from ShotRecord import ShotRecord


def test_players_must_have_grids_of_the_same_size():
    with pytest.raises(ValueError, match="même taille"):
        Game(ComputerPlayer("A"), ComputerPlayer("B", grid_size=12))


def test_draw_for_first_shooter_is_fair():
    firsts = sum(Game(ComputerPlayer("A"), ComputerPlayer("B")).players[0].name == "A" for _ in range(1000))
    assert 400 < firsts < 600


def test_game_ends_with_the_loser_fully_sunk(capsys):
    first, second = ComputerPlayer("A"), ComputerPlayer("B")
    winner = Game(first, second).play()
    loser = second if winner is first else first
    assert loser.is_defeated
    assert not winner.is_defeated
    assert "a gagné" in capsys.readouterr().out


def test_history_alternates_shooters_and_ends_with_the_winning_shot(capsys):
    game = Game(ComputerPlayer("A"), ComputerPlayer("B"))
    winner = game.play()
    shooters = [record.shooter for record in game.history]
    assert all(current != following for current, following in zip(shooters, shooters[1:]))
    assert game.history[-1].shooter == winner.name
    assert game.history[-1].result is ShotResult.SUNK


def test_history_cannot_be_modified(capsys):
    game = Game(ComputerPlayer("A"), ComputerPlayer("B"))
    game.play()
    with pytest.raises(AttributeError):
        game.history.append(game.history[0])
    with pytest.raises(FrozenInstanceError):
        game.history[0].result = ShotResult.SUNK


def test_observer_receives_every_shot_in_order(capsys):
    seen: list[ShotRecord] = []
    game = Game(ComputerPlayer("A"), ComputerPlayer("B"), on_shot=seen.append)
    game.play()
    assert seen == list(game.history)


def test_scripted_human_can_play_a_whole_game(keyboard, capsys):
    every_cell = [f"{chr(ord('A') + col)}{row + 1}" for row in range(10) for col in range(10)]
    human = HumanPlayer("Michaël", read=keyboard("A", *every_cell))
    game = Game(human, ComputerPlayer("Ordinateur"))
    winner = game.play()
    assert winner.name in ("Michaël", "Ordinateur")
    assert any(record.shooter == "Michaël" for record in game.history)
