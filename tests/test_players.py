"""Tests des joueurs : classe abstraite, réception des tirs, ordinateur et humain au clavier."""

import pytest

from battleships.computer_player import ComputerPlayer
from battleships.fleet import ShipType
from battleships.human_player import HumanPlayer
from battleships.player import Player, ShotResult


def test_abstract_player_cannot_be_created():
    """Un joueur est toujours un humain ou un ordinateur, jamais un joueur abstrait."""
    # Volontaire : on vérifie que l'instanciation d'une classe abstraite est bien refusée à l'exécution
    with pytest.raises(TypeError, match="abstract"):
        Player("Personne")


def test_subclass_missing_a_method_cannot_be_created():
    """Tout nouveau type de joueur doit savoir placer sa flotte et choisir sa cible."""
    # Volontaire : cette sous-classe n'implémente pas choose_target, et sa création doit être refusée à l'exécution

    class Incomplete(Player):
        """Joueur volontairement incomplet : il sait placer sa flotte, mais pas choisir sa cible."""

        def place_fleet(self) -> None:
            """Implémentée uniquement pour que choose_target soit la seule méthode manquante."""

    with pytest.raises(TypeError, match="choose_target"):
        Incomplete("Incomplet")


def test_settings_are_passed_to_grid_and_fleet():
    """La taille de grille et la flotte choisies sont bien transmises au joueur."""
    player = ComputerPlayer("Ordinateur", grid_size=12, ship_types=(ShipType("Mine", 1, count=4),))
    assert player.grid.size == 12
    assert len(player.fleet) == 4


def test_receive_shot_announces_miss_hit_then_sunk():
    """Un tir est annoncé « à l’eau », « touché » ou « coulé », et le dernier bateau coulé fait perdre."""
    player = ComputerPlayer("Cible", ship_types=(ShipType("Torpilleur", 2),))
    player.grid.place(player.fleet.ships[0], 0, 0, horizontal=True)
    assert player.receive_shot(5, 5) is ShotResult.MISS
    assert player.receive_shot(0, 0) is ShotResult.HIT
    assert not player.is_defeated
    assert player.receive_shot(0, 1) is ShotResult.SUNK
    assert player.is_defeated


def test_computer_places_its_whole_fleet():
    """L’ordinateur place toujours toute sa flotte."""
    computer = ComputerPlayer("Ordinateur")
    computer.place_fleet()
    assert all(ship.is_placed for ship in computer.fleet)


def test_computer_only_targets_cells_never_shot():
    """L’ordinateur ne vise jamais deux fois la même case."""
    enemy = ComputerPlayer("Cible")
    cells = [cell for row in enemy.grid.cells for cell in row]
    for cell in cells[:-1]:
        cell.shoot()
    assert ComputerPlayer("Tireur").choose_target(enemy.grid) == (cells[-1].row, cells[-1].col)


def test_human_can_choose_automatic_placement_after_a_typo(keyboard, capsys):
    """Une réponse invalide est refusée, puis le placement automatique est accepté."""
    human = HumanPlayer("Michaël", read=keyboard("x", "A"))
    human.place_fleet()
    assert all(ship.is_placed for ship in human.fleet)
    assert "Refusé : répondez A ou M" in capsys.readouterr().out


def test_human_can_place_manually(keyboard):
    """Le joueur peut placer ses bateaux lui-même au clavier."""
    human = HumanPlayer("Michael", ship_types=(ShipType("Torpilleur", 2),), read=keyboard("M", "A1 V"))
    human.place_fleet()
    assert [str(cell) for cell in human.fleet.ships[0].cells] == ["A1", "A2"]


def test_human_target_refuses_invalid_or_already_shot_cells(keyboard, capsys):
    """Le joueur ne peut viser ni une case hors grille, ni une case déjà visée."""
    enemy = ComputerPlayer("Cible")
    enemy.grid[6, 1].shoot()
    human = HumanPlayer("Michaël", read=keyboard("B7", "Z9", "C3"))
    assert human.choose_target(enemy.grid) == (2, 2)
    output = capsys.readouterr().out
    assert "B7 a déjà été visée" in output
    assert "Z9 est hors de la grille" in output
