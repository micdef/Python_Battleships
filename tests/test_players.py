import pytest

from ComputerPlayer import ComputerPlayer
from Fleet import ShipType
from HumanPlayer import HumanPlayer
from Player import Player, ShotResult


def test_abstract_player_cannot_be_created():
    # Volontaire : on vérifie que l'instanciation d'une classe abstraite est bien refusée à l'exécution
    with pytest.raises(TypeError, match="abstract"):
        Player("Personne")


def test_subclass_missing_a_method_cannot_be_created():
    # Volontaire : cette sous-classe n'implémente pas choose_target, et sa création doit être refusée à l'exécution
    class Incomplete(Player):
        def place_fleet(self) -> None:
            pass

    with pytest.raises(TypeError, match="choose_target"):
        Incomplete("Incomplet")


def test_settings_are_passed_to_grid_and_fleet():
    player = ComputerPlayer("Ordinateur", grid_size=12, ship_types=(ShipType("Mine", 1, count=4),))
    assert player.grid.size == 12
    assert len(player.fleet) == 4


def test_receive_shot_announces_miss_hit_then_sunk():
    player = ComputerPlayer("Cible", ship_types=(ShipType("Torpilleur", 2),))
    player.grid.place(player.fleet.ships[0], 0, 0, horizontal=True)
    assert player.receive_shot(5, 5) is ShotResult.MISS
    assert player.receive_shot(0, 0) is ShotResult.HIT
    assert not player.is_defeated
    assert player.receive_shot(0, 1) is ShotResult.SUNK
    assert player.is_defeated


def test_computer_places_its_whole_fleet():
    computer = ComputerPlayer("Ordinateur")
    computer.place_fleet()
    assert all(ship.is_placed for ship in computer.fleet)


def test_computer_only_targets_cells_never_shot():
    enemy = ComputerPlayer("Cible")
    cells = [cell for row in enemy.grid.cells for cell in row]
    for cell in cells[:-1]:
        cell.shoot()
    assert ComputerPlayer("Tireur").choose_target(enemy.grid) == (cells[-1].row, cells[-1].col)


def test_human_can_choose_automatic_placement_after_a_typo(keyboard, capsys):
    human = HumanPlayer("Michaël", read=keyboard("x", "A"))
    human.place_fleet()
    assert all(ship.is_placed for ship in human.fleet)
    assert "Refusé : répondez A ou M" in capsys.readouterr().out


def test_human_can_place_manually(keyboard):
    human = HumanPlayer("Michael", ship_types=(ShipType("Torpilleur", 2),), read=keyboard("M", "A1 V"))
    human.place_fleet()
    assert [str(cell) for cell in human.fleet.ships[0].cells] == ["A1", "A2"]


def test_human_target_refuses_invalid_or_already_shot_cells(keyboard, capsys):
    enemy = ComputerPlayer("Cible")
    enemy.grid[6, 1].shoot()
    human = HumanPlayer("Michaël", read=keyboard("B7", "Z9", "C3"))
    assert human.choose_target(enemy.grid) == (2, 2)
    output = capsys.readouterr().out
    assert "B7 a déjà été visée" in output
    assert "Z9 est hors de la grille" in output
