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


# --- Partie tour par tour : ce sont les clients qui la font avancer ---


@pytest.fixture
def ready_game(computer, console):
    """Fabrique une partie entre deux ordinateurs, flottes placées, prête à commencer."""

    def make(**options) -> Game:
        """Crée la partie ; options est transmis à Game (ex. on_shot=...)."""
        first, second = computer("A"), computer("B")
        first.place_fleet()
        second.place_fleet()
        return Game(first, second, view=console(), **options)

    return make


def test_game_cannot_start_before_both_fleets_are_placed(computer, console):
    """Pas de premier tir tant qu'une flotte n'est pas entièrement placée."""
    game = Game(computer("A"), computer("B"), view=console())
    with pytest.raises(RuntimeError, match="placées"):
        game.start()


def test_game_cannot_start_twice(ready_game):
    """Le tirage au sort n'est annoncé qu'une fois : une partie ne commence pas deux fois."""
    game = ready_game()
    game.start()
    with pytest.raises(RuntimeError, match="déjà commencé"):
        game.start()


def test_no_shot_before_the_start(ready_game):
    """Un tir avant le début de la partie est refusé."""
    with pytest.raises(RuntimeError, match="pas commencé"):
        ready_game().play_turn(0, 0)


def test_a_turn_passes_the_hand_to_the_other_player(ready_game):
    """Après un tir qui ne termine pas la partie, les rôles de tireur et de cible s'inversent."""
    game = ready_game()
    game.start()
    shooter, target = game.current_shooter, game.current_target
    record = game.play_turn(0, 0)
    assert record.shooter == shooter.name
    assert (game.current_shooter, game.current_target) == (target, shooter)


def test_a_refused_shot_does_not_use_the_turn(ready_game):
    """Une case déjà visée est refusée par le domaine : rien n'est joué, le même joueur garde la main."""
    game = ready_game()
    game.start()
    game.play_turn(0, 0)
    shooter = game.current_shooter
    game.play_turn(0, 0)  # l'autre joueur vise la même case : c'est sa grille à lui qui la reçoit
    game.play_turn(5, 5)
    with pytest.raises(ValueError, match="déjà été visée"):
        game.play_turn(0, 0)
    assert game.current_shooter is shooter
    assert len(game.history) == 3


def test_automatic_turn_is_refused_for_a_human(computer, console):
    """Seul l'ordinateur joue « tout seul » : pour un humain, c'est le client qui fournit la case."""
    human, machine = Player("Michaël"), computer("Ordinateur")
    human.place_fleet()
    machine.place_fleet()
    game = Game(human, machine, view=console())
    game.start()
    if game.current_shooter is machine:
        game.play_automatic_turn()
    with pytest.raises(RuntimeError, match="lui-même"):
        game.play_automatic_turn()


def test_turns_driven_from_outside_reach_a_winner(ready_game):
    """Une partie menée tour par tour par un client finit par un vainqueur, puis refuse tout tir."""
    game = ready_game()
    game.start()
    assert not game.is_over and game.winner is None
    while not game.is_over:
        game.play_automatic_turn()
    assert game.current_target.is_defeated
    assert game.winner is game.current_shooter
    with pytest.raises(RuntimeError, match="finie"):
        game.play_automatic_turn()
