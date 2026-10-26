"""Tests des joueurs : stratégies de tir, réception des tirs, ordinateur et humain au clavier."""

import pytest

from battleships.clients.console.human_player import HumanPlayer
from battleships.domain.fleet import ShipType
from battleships.domain.player import Player, ShotResult
from battleships.domain.rules import Rules
from battleships.domain.strategy import TargetingStrategy


def test_strategy_missing_choose_target_cannot_be_created():
    """Toute nouvelle stratégie (futur niveau de difficulté) doit savoir choisir une cible."""
    # Volontaire : cette stratégie n'implémente pas choose_target, et sa création doit être refusée à l'exécution

    class Incomplete(TargetingStrategy):
        """Stratégie volontairement incomplète : elle ne sait pas choisir de cible."""

    with pytest.raises(TypeError, match="choose_target"):
        Incomplete()


def test_player_without_strategy_does_not_choose_automatically(computer):
    """Un joueur humain n'a pas de stratégie : on ne peut pas lui demander de choisir seul ses tirs."""
    human = Player("Michael")
    assert not human.is_automatic
    with pytest.raises(ValueError, match="pas de stratégie"):
        human.choose_target(computer("Cible").grid)


def test_settings_are_passed_to_grid_and_fleet(computer):
    """Le joueur construit sa grille et sa flotte selon les règles reçues."""
    player = computer("Ordinateur", Rules(grid_size=12, ship_types=(ShipType("Mine", 1, count=4),)))
    assert player.grid.size == 12
    assert len(player.fleet) == 4


def test_receive_shot_announces_miss_hit_then_sunk(computer):
    """Un tir est annoncé « à l’eau », « touché » ou « coulé », et le dernier bateau coulé fait perdre."""
    player = computer("Cible", Rules(ship_types=(ShipType("Torpilleur", 2),)))
    player.grid.place(player.fleet.ships[0], 0, 0, horizontal=True)
    assert player.receive_shot(5, 5) is ShotResult.MISS
    assert player.receive_shot(0, 0) is ShotResult.HIT
    assert not player.is_defeated
    assert player.receive_shot(0, 1) is ShotResult.SUNK
    assert player.is_defeated


def test_computer_places_its_whole_fleet(computer):
    """L’ordinateur place toujours toute sa flotte."""
    player = computer("Ordinateur")
    assert player.is_automatic
    player.place_fleet()
    assert all(ship.is_placed for ship in player.fleet)


def test_computer_only_targets_cells_never_shot(computer):
    """L’ordinateur ne vise jamais deux fois la même case."""
    enemy = computer("Cible")
    cells = [cell for row in enemy.grid.cells for cell in row]
    for cell in cells[:-1]:
        cell.shoot()
    assert computer("Tireur").choose_target(enemy.grid) == (cells[-1].row, cells[-1].col)


def test_human_can_choose_automatic_placement_after_a_typo(console, capsys):
    """Une réponse invalide est refusée, puis le placement automatique est accepté."""
    human = HumanPlayer("Michaël", console("x", "A"))
    human.place_fleet()
    assert all(ship.is_placed for ship in human.fleet)
    assert "Refusé : répondez A ou M" in capsys.readouterr().out


def test_human_can_place_manually(console):
    """Le joueur peut placer ses bateaux lui-même au clavier."""
    human = HumanPlayer("Michael", console("M", "A1 V"), Rules(ship_types=(ShipType("Torpilleur", 2),)))
    human.place_fleet()
    assert [str(cell) for cell in human.fleet.ships[0].cells] == ["A1", "A2"]


def test_human_target_refuses_invalid_or_already_shot_cells(computer, console, capsys):
    """Le joueur ne peut viser ni une case hors grille, ni une case déjà visée."""
    enemy = computer("Cible")
    enemy.grid[6, 1].shoot()
    human = HumanPlayer("Michaël", console("B7", "Z9", "C3"))
    assert human.choose_target(enemy.grid) == (2, 2)
    output = capsys.readouterr().out
    assert "B7 a déjà été visée" in output
    assert "Z9 est hors de la grille" in output
