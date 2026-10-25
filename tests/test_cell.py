import pytest

from Cell import Cell


def test_new_cell_is_untouched_water():
    cell = Cell(0, 0)
    assert not cell.has_ship
    assert not cell.hit
    assert cell.own_symbol == Cell.WATER
    assert cell.enemy_symbol == Cell.UNKNOWN


def test_shot_in_water():
    cell = Cell(0, 0)
    assert cell.shoot() is False
    assert cell.own_symbol == cell.enemy_symbol == Cell.MISS


def test_shot_on_ship_is_a_hit():
    cell = Cell(0, 0)
    cell.ship = object()  # n'importe quel objet suffit : la case ne regarde que la présence d'un bateau
    assert cell.shoot() is True
    assert cell.own_symbol == cell.enemy_symbol == cell.HIT


def test_untouched_ship_is_hidden_from_enemy():
    cell = Cell(0, 0)
    cell.ship = object()
    assert cell.own_symbol == Cell.SHIP
    assert cell.enemy_symbol == Cell.UNKNOWN


def test_same_cell_cannot_be_shot_twice():
    cell = Cell(0, 0)
    cell.shoot()
    with pytest.raises(ValueError, match="déjà été visée"):
        cell.shoot()


@pytest.mark.parametrize(("row", "col", "expected"), [(0, 0, "A1"), (6, 1, "B7"), (9, 9, "J10"), (25, 25, "Z26")])
def test_str_gives_player_coordinates(row, col, expected):
    assert str(Cell(row, col)) == expected
