import pytest

from Grid import Grid
from Ship import Ship


@pytest.mark.parametrize("size", [Grid.MIN_SIZE, 15, Grid.MAX_SIZE])
def test_valid_sizes_are_accepted(size):
    assert Grid(size).size == size


@pytest.mark.parametrize("size", [Grid.MIN_SIZE - 1, Grid.MAX_SIZE + 1])
def test_invalid_sizes_are_refused(size):
    with pytest.raises(ValueError, match="hors limites"):
        Grid(size)


def test_each_grid_has_its_own_cells():
    """Régression : à l'origine, les cases étaient un attribut de classe partagé par toutes les grilles."""
    first, second = Grid(), Grid()
    first[0, 0].shoot()
    assert not second[0, 0].hit


@pytest.mark.parametrize(("text", "expected"), [("B7", (6, 1)), (" b7 ", (6, 1)), ("A1", (0, 0)), ("J10", (9, 9))])
def test_parse_position_reads_player_coordinates(text, expected):
    assert Grid().parse_position(text) == expected


@pytest.mark.parametrize("text", ["K1", "A11", "A0", "7B", "BB", "10", ""])
def test_parse_position_refuses_invalid_text(text):
    with pytest.raises(ValueError):
        Grid().parse_position(text)


def test_parse_position_is_the_inverse_of_str():
    grid = Grid(12)
    for row in range(grid.size):
        for col in range(grid.size):
            assert grid.parse_position(str(grid[row, col])) == (row, col)


@pytest.mark.parametrize("position", [(-1, 0), (0, -1), (10, 0), (0, 10)])
def test_getitem_refuses_positions_outside_the_grid(position):
    """Régression : sans contrôle, une liste Python accepte les indices négatifs (-1 = dernière ligne)."""
    with pytest.raises(IndexError):
        Grid()[position]


def test_render_hides_ships_from_the_enemy():
    grid = Grid()
    grid.place(Ship("Torpilleur", 2), 0, 0, horizontal=True)
    assert grid.render(reveal=True)[1] == " 1 B B ~ ~ ~ ~ ~ ~ ~ ~"
    assert grid.render()[1] == " 1 . . . . . . . . . ."


def test_render_lets_the_interface_dress_each_symbol():
    lines = Grid().render(style=lambda cell, symbol: "*")
    assert lines[1] == " 1 * * * * * * * * * *"
