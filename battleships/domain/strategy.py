"""Les stratégies de tir de l'ordinateur : sa façon de choisir la prochaine case à viser."""

import random
from abc import abstractmethod
from typing import Protocol

from battleships.domain.grid import Grid


class TargetingStrategy(Protocol):
    """Le contrat d'une stratégie de tir : choisir une case jamais visée, sans jamais voir les bateaux adverses.

    Chaque niveau de difficulté sera une stratégie ; une stratégie qui le déclare doit implémenter choose_target.
    """

    @abstractmethod
    def choose_target(self, enemy_grid: Grid) -> tuple[int, int]:
        """Choisit une case jamais visée de la grille adverse ; seul cell.hit peut être consulté."""


class RandomStrategy(TargetingStrategy):
    """Niveau facile : tire au hasard parmi les cases jamais visées."""

    def choose_target(self, enemy_grid: Grid) -> tuple[int, int]:
        """Tire au hasard parmi les cases jamais visées."""
        # Seul cell.hit est consulté : la stratégie ne regarde jamais où sont les bateaux
        candidates = [(cell.row, cell.col) for row in enemy_grid.cells for cell in row if not cell.hit]
        return random.choice(candidates)
