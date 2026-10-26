"""Tests de la partie : tirage au sort, tours alternés, victoire, historique et observateur."""

from dataclasses import FrozenInstanceError
from itertools import pairwise

import pytest

from battleships.application.game import Game
from battleships.clients.console.human_player import HumanPlayer
from battleships.domain.fleet import ShipType
from battleships.domain.player import Player, ShotResult
from battleships.domain.rules import Rules
from battleships.domain.shot_record import ShotRecord


@pytest.mark.parametrize("other_rules", [Rules(grid_size=12), Rules(ship_types=(ShipType("Mine", 1),))])
def test_players_must_play_with_the_same_rules(computer, console, other_rules):
    """Les deux joueurs s'affrontent avec les mêmes règles : même taille de grille et même flotte."""
    with pytest.raises(ValueError, match="mêmes règles"):
        Game(computer("A"), computer("B", other_rules), view=console())


def test_draw_for_first_shooter_is_fair(computer, console):
    """Le tirage au sort du premier tireur est équitable."""
    firsts = sum(Game(computer("A"), computer("B"), view=console()).players[0].name == "A" for _ in range(1000))
    assert 400 < firsts < 600


def test_game_ends_with_the_loser_fully_sunk(computer, console, capsys):
    """La partie s’arrête quand toute la flotte d’un joueur est coulée, et annonce le vainqueur."""
    first, second = computer("A"), computer("B")
    winner = Game(first, second, view=console()).play()
    loser = second if winner is first else first
    assert loser.is_defeated
    assert not winner.is_defeated
    assert "a gagné" in capsys.readouterr().out


def test_history_alternates_shooters_and_ends_with_the_winning_shot(computer, console, capsys):
    """Les joueurs tirent chacun leur tour, et le dernier coup de l’historique est le coup gagnant."""
    game = Game(computer("A"), computer("B"), view=console())
    winner = game.play()
    shooters = [record.shooter for record in game.history]
    assert all(current != following for current, following in pairwise(shooters))
    assert game.history[-1].shooter == winner.name
    assert game.history[-1].result is ShotResult.SUNK


def test_every_hit_names_the_ship_and_every_miss_does_not(computer, console, capsys):
    """Règlement : le défenseur révèle le bateau dès qu'il est touché ; un tir à l'eau ne nomme rien."""
    game = Game(computer("A"), computer("B"), view=console())
    game.play()
    for record in game.history:
        if record.result is ShotResult.MISS:
            assert record.ship_name is None
        else:
            assert record.ship_name


def test_history_cannot_be_modified(computer, console, capsys):
    """L’historique est un journal en lecture seule : aucun coup ne peut être ajouté ni modifié."""
    game = Game(computer("A"), computer("B"), view=console())
    game.play()
    with pytest.raises(AttributeError):
        game.history.append(game.history[0])
    with pytest.raises(FrozenInstanceError):
        game.history[0].result = ShotResult.SUNK


def test_observer_receives_every_shot_in_order(computer, console, capsys):
    """L’observateur reçoit chaque tir, dans l’ordre, sans en manquer aucun."""
    seen: list[ShotRecord] = []
    game = Game(computer("A"), computer("B"), view=console(), on_shot=seen.append)
    game.play()
    assert seen == list(game.history)


def test_scripted_human_can_play_a_whole_game(computer, console, capsys):
    """Une partie complète contre l’ordinateur va jusqu’au bout avec un joueur au clavier."""
    every_cell = [f"{chr(ord('A') + col)}{row + 1}" for row in range(10) for col in range(10)]
    ui = console("A", *every_cell)
    game = Game(HumanPlayer("Michaël", ui), computer("Ordinateur"), view=ui)
    winner = game.play()
    assert winner.name in ("Michaël", "Ordinateur")
    assert any(record.shooter == "Michaël" for record in game.history)


class RecordingView:
    """Interface minimale qui retient les annonces : elle respecte GameView sans en hériter ni rien afficher."""

    def __init__(self) -> None:
        """Commence sans aucune annonce."""
        self.events: list[str] = []

    def announce_start(self, first: Player) -> None:
        """Retient le joueur qui commence."""
        self.events.append(f"début : {first}")

    def announce_shot(self, record: ShotRecord) -> None:
        """Retient chaque tir."""
        self.events.append(f"tir : {record.position}")

    def announce_winner(self, winner: Player, loser: Player, history: tuple[ShotRecord, ...]) -> None:
        """Retient le vainqueur."""
        self.events.append(f"vainqueur : {winner}")


def test_game_only_needs_a_view_following_the_contract(computer):
    """La partie ne dépend que du contrat GameView : une interface sans console suffit pour jouer."""
    view = RecordingView()
    game = Game(computer("A"), computer("B"), view=view)
    winner = game.play()
    assert view.events[0].startswith("début : ")
    assert view.events[-1] == f"vainqueur : {winner}"
    assert len(view.events) == len(game.history) + 2
