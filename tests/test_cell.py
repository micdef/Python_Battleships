"""Tests d'une case : son état (eau, bateau, tir reçu) et ses deux affichages."""

import pytest

from Cell import Cell


def test_new_cell_is_untouched_water():
    """Une case neuve est de l’eau, jamais visé"""
    cell = Cell(0, 0)
    assert not cell.has_ship
    assert not cell.hit
    assert cell.own_symbol == Cell.WATER
    assert cell.enemy_symbol == Cell.UNKNOWN


def test_shot_in_water():
    """Un tir dans l’eau est un échec, visible des deux côtés."""
    cell = Cell(0, 0)
    assert cell.shoot() is False
    assert cell.own_symbol == cell.enemy_symbol == Cell.MISS


def test_shot_on_ship_is_a_hit():
    """Un tir sur un bateau le touche, et la touche est visible des deux côtés."""
    cell = Cell(0, 0)
    cell.ship = object()  # n'importe quel objet suffit : la case ne regarde que la présence d'un bateau
    assert cell.shoot() is True
    assert cell.own_symbol == cell.enemy_symbol == cell.HIT


def test_untouched_ship_is_hidden_from_enemy():
    """Un bateau non touché reste invisible pour l’adversaire."""
    cell = Cell(0, 0)
    cell.ship = object()
    assert cell.own_symbol == Cell.SHIP
    assert cell.enemy_symbol == Cell.UNKNOWN


def test_same_cell_cannot_be_shot_twice():
    """Une case ne peut être visée qu’une fois."""
    cell = Cell(0, 0)
    cell.shoot()
    with pytest.raises(ValueError, match="déjà été visée"):
        cell.shoot()


@pytest.mark.parametrize(("row", "col", "expected"), [(0, 0, "A1"), (6, 1, "B7"), (9, 9, "J10"), (25, 25, "Z26")])
def test_str_gives_player_coordinates(row, col, expected):
    """Une case se nomme comme le joueur la tape : lettre de colonne, puis numéro de ligne."""
    assert str(Cell(row, col)) == expected
