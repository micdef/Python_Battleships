"""Tests d'un bateau : sa longueur, son placement et son état « coulé »."""

import pytest

from battleships.domain.grid import Grid
from battleships.domain.ship import Ship


@pytest.mark.parametrize("length", [0, -1])
def test_length_below_one_is_refused(length):
    """Un bateau occupe au moins une case."""
    with pytest.raises(ValueError, match="invalide"):
        Ship("Fantôme", length)


def test_new_ship_is_not_placed():
    """Un bateau neuf n’est sur aucune grille."""
    assert not Ship("Croiseur", 4).is_placed


def test_unplaced_ship_is_never_sunk():
    """all() sur une liste vide vaut True : sans le contrôle is_placed, un bateau hors grille serait « coulé »."""
    assert not Ship("Croiseur", 4).is_sunk


def test_ship_is_sunk_when_every_cell_is_hit():
    """Un bateau n’est coulé qu’une fois toutes ses cases touchées."""
    grid = Grid()
    ship = Ship("Sous-Marin", 3)
    grid.place(ship, 0, 0, horizontal=True)
    for cell in ship.cells[:-1]:
        cell.shoot()
        assert not ship.is_sunk
    ship.cells[-1].shoot()
    assert ship.is_sunk


def test_repr_of_ship_and_cell_do_not_call_each_other_endlessly():
    """Régression évitée dès la conception : Cell affiche le nom du bateau, Ship affiche les coordonnées."""
    grid = Grid()
    ship = Ship("Torpilleur", 2)
    grid.place(ship, 0, 0, horizontal=True)
    assert repr(ship) == "Ship(name='Torpilleur', length=2, cells=[A1, B1], sunk=False)"
    assert repr(grid[0, 0]) == "Cell(row=0, col=0, ship='Torpilleur', hit=False)"
