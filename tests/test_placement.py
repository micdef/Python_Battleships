"""Tests des placements : manuel (tout ou rien), retrait, et placement automatique de la flotte."""

import random

import pytest

from battleships.domain.fleet import Fleet, ShipType
from battleships.domain.grid import Grid
from battleships.domain.ship import Ship


def occupied(grid: Grid) -> list[str]:
    """Coordonnées de toutes les cases occupées par un bateau."""
    return [str(cell) for row in grid.cells for cell in row if cell.has_ship]


@pytest.mark.parametrize(("horizontal", "expected"), ((True, ["B3", "C3", "D3"]), (False, ["B3", "B4", "B5"])))
def test_ship_is_placed_to_the_right_or_downwards(horizontal, expected):
    """Un bateau part de sa case de départ, vers la droite ou vers le bas."""
    grid = Grid()
    ship = Ship("Sous-Marin", 3)
    grid.place(ship, 2, 1, horizontal=horizontal)
    assert [str(cell) for cell in ship.cells] == expected
    assert set(occupied(grid)) == set(expected)


@pytest.mark.parametrize(
    ("row", "col", "horizontal", "message"),
    [
        (0, 8, True, "déborderait"),
        (8, 0, False, "déborderait"),
        (-1, 0, True, "déborderait"),
        (0, 1, False, "chevaucherait"),
    ],
)
def test_refused_placement_leaves_the_grid_unchanged(row, col, horizontal, message):
    """Tout ou rien : un placement refusé ne doit occuper aucune case."""
    grid = Grid()
    grid.place(Ship("Torpilleur", 2), 0, 0, horizontal=True)
    before = occupied(grid)
    with pytest.raises(ValueError, match=message):
        grid.place(Ship("Croiseur", 4), row, col, horizontal=horizontal)
    assert occupied(grid) == before


def test_ship_cannot_be_placed_twice():
    """Un bateau déjà posé ne peut pas être posé une seconde fois."""
    grid = Grid()
    ship = Ship("Torpilleur", 2)
    grid.place(ship, 0, 0, horizontal=True)
    with pytest.raises(ValueError, match="déjà placé"):
        grid.place(ship, 5, 5, horizontal=True)


def test_remove_free_the_cells():
    """Retirer un bateau libère toutes ses cases."""
    grid = Grid()
    ship = Ship("Torpilleur", 2)
    grid.place(ship, 0, 0, horizontal=True)
    grid.remove(ship)
    assert occupied(grid) == []
    assert not ship.is_placed


def test_hit_ship_cannot_be_removed():
    """Un bateau touché ne peut plus être retiré : la partie en cours est protégée."""
    grid = Grid()
    ship = Ship("Torpilleur", 2)
    grid.place(ship, 0, 0, horizontal=True)
    grid[0, 0].shoot()
    with pytest.raises(ValueError, match="déjà été touché"):
        grid.remove(ship)


def test_random_placement_always_places_the_whole_classic_fleet():
    """Le placement automatique pose toujours toute la flotte classique."""
    for _ in range(100):
        grid, fleet = Grid(), Fleet()
        grid.place_randomly(fleet)
        assert all(ship.is_placed for ship in fleet)
        assert len(occupied(grid)) == 17


def test_random_placement_can_fill_the_whole_grid():
    """Le placement automatique sait remplir la grille jusqu’à la dernière case."""
    grid = Grid()
    grid.place_randomly(Fleet((ShipType("Mine", 1, count=100),)))
    assert len(occupied(grid)) == 100


def test_fleet_largen_than_the_grid_is_refused():
    """Une flotte trop grande pour la grille est refusée d’emblée."""
    with pytest.raises(ValueError, match="ne tient pas"):
        Grid().place_randomly(Fleet((ShipType("Mine", 1, count=101),)))


def test_fleet_already_placed_is_refused():
    """Une flotte déjà placée ne peut pas être replacée automatiquement."""
    grid, fleet = Grid(), Fleet()
    grid.place_randomly(fleet)
    with pytest.raises(ValueError, match="déjà"):
        grid.place_randomly(fleet)


def test_impossible_random_placement_leaves_the_grid_empty():
    """20 bateaux de 5 cases remplissent exactement la grille : le hasard ne trouve pas, et rien ne doit rester."""
    random.seed(0)  # hasard figé : le test donne toujours le même résultat
    grid = Grid()
    with pytest.raises(ValueError, match="Impossible"):
        grid.place_randomly(Fleet((ShipType("Long", 5, count=20),)))
    assert occupied(grid) == []
