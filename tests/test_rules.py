"""Tests des règles : règles d'origine par défaut, validation dès la création et comparaison par valeur."""

from dataclasses import FrozenInstanceError

import pytest

from battleships.domain.fleet import Fleet, ShipType
from battleships.domain.grid import Grid
from battleships.domain.rules import CLASSIC_RULES, Rules


def test_default_rules_are_the_original_ones():
    """Sans précision, une partie suit les règles d'origine : grille de 10 sur 10 et flotte classique."""
    assert CLASSIC_RULES.grid_size == 10
    assert CLASSIC_RULES.ship_types == Fleet.CLASSIC


def test_rules_are_compared_by_values():
    """Deux règles identiques sont égales, même créées séparément : c'est ce qui permet de les comparer en partie."""
    assert Rules() == CLASSIC_RULES
    assert Rules(grid_size=12) != CLASSIC_RULES


def test_rules_cannot_be_modified():
    """Les règles sont figées : personne ne peut les changer en cours de partie."""
    with pytest.raises(FrozenInstanceError):
        CLASSIC_RULES.grid_size = 12


@pytest.mark.parametrize("size", [Grid.MIN_SIZE, Grid.MAX_SIZE])
def test_grid_size_limits_are_accepted(size):
    """Les tailles limites elles-mêmes sont valides : une grille de 10 comme de 26 est acceptée."""
    assert Rules(grid_size=size).grid_size == size


@pytest.mark.parametrize("size", [Grid.MIN_SIZE - 1, Grid.MAX_SIZE + 1])
def test_grid_size_outside_the_limits_is_refused(size):
    """Une taille de grille hors limites est refusée dès la création des règles, avant toute partie."""
    with pytest.raises(ValueError, match="hors limites"):
        Rules(grid_size=size)


def test_fleet_larger_than_the_grid_is_refused():
    """Une flotte qui ne tient pas dans la grille est refusée dès la création des règles."""
    with pytest.raises(ValueError, match="ne tient pas"):
        Rules(ship_types=(ShipType("Mine", 1, count=101),))
