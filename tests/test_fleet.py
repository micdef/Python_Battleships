"""Tests de la flotte : règle classique, variantes, numérotation et état « détruite »."""

from dataclasses import FrozenInstanceError

import pytest

from battleships.domain.fleet import Fleet, ShipType
from battleships.domain.grid import Grid


def test_default_fleet_is_the_classic_one():
    """Sans règle donnée, la flotte est la flotte classique."""
    fleet = Fleet()
    assert [(ship.name, ship.length) for ship in fleet] == [
        ("Porte-Avions", 5),
        ("Croiseur", 4),
        ("Contre-Torpilleur", 3),
        ("Sous-Marin", 3),
        ("Torpilleur", 2),
    ]


def test_fleet_is_iterable_and_has_a_length():
    """Régression : avec __iter au lieu de __iter__, « for ship in fleet » levait une TypeError."""
    fleet = Fleet()
    assert len(fleet) == 5
    assert len(list(fleet)) == 5


def test_several_copies_are_numbered():
    """Les exemplaires multiples d’un même type sont numérotés pour rester distincts."""
    fleet = Fleet((ShipType("Croiseur", 4), ShipType("Mine", 3, count=3)))
    assert [ship.name for ship in fleet] == ["Croiseur", "Mine-1", "Mine-2", "Mine-3"]


def test_each_fleet_has_its_own_ships():
    """Deux flottes ne partagent jamais leurs bateaux."""
    assert Fleet().ships[0] is not Fleet().ships[0]


@pytest.mark.parametrize(("length", "count"), [(0, 1), (2, 0)])
def test_invalid_ship_type_is_refused(length, count):
    """Un type de bateau a au moins une case et au moins un exemplaire."""
    with pytest.raises(ValueError, match="au moins 1"):
        ShipType("Fantôme", length, count)


def test_empty_fleet_is_refused():
    """Une flotte contient au moins un type de bateau."""
    with pytest.raises(ValueError, match="au moins un type"):
        Fleet(())


def test_duplicate_names_are_refused():
    """Deux types de bateaux ne peuvent pas porter le même nom."""
    with pytest.raises(ValueError, match="même nom"):
        Fleet((ShipType("Mine", 1), ShipType("Mine", 2)))


def test_classic_rule_cannot_be_modified():
    """La règle classique est figée : personne ne peut la modifier par accident."""
    with pytest.raises(FrozenInstanceError):
        Fleet.CLASSIC[0].length = 9


def test_fleet_is_destroyed_only_when_every_ship_is_sunk():
    """Une flotte n’est détruite qu’une fois tous ses bateaux coulés."""
    grid = Grid()
    fleet = Fleet((ShipType("Mine", 1, count=2),))
    grid.place(fleet.ships[0], 0, 0, horizontal=True)
    grid.place(fleet.ships[1], 0, 2, horizontal=True)
    grid[0, 0].shoot()
    assert not fleet.is_destroyed
    grid[0, 2].shoot()
    assert fleet.is_destroyed


def test_fleet_is_placed_only_when_every_ship_is():
    """La flotte n'est prête qu'une fois tous ses bateaux sur la grille."""
    grid, fleet = Grid(), Fleet((ShipType("Torpilleur", 2), ShipType("Sous-Marin", 3)))
    assert not fleet.is_placed
    grid.place(fleet.ships[0], 0, 0, horizontal=True)
    assert not fleet.is_placed
    grid.place(fleet.ships[1], 2, 0, horizontal=True)
    assert fleet.is_placed
