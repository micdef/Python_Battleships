"""Le joueur abstrait et le résultat d’un tir."""

from abc import ABC, abstractmethod
from enum import Enum

from battleships.fleet import Fleet, ShipType
from battleships.grid import Grid


class ShotResult(Enum):
    """Résultat d'un tir, tel qu'il est annoncé au tireur."""

    MISS = "À l'eau"
    HIT = "Touché"
    SUNK = "Coulé"


class Player(ABC):
    """Un joueur : possède sa grille et sa flotte ; sa façon de jouer est définie par les sous-classes."""

    def __init__(
        self, name: str, grid_size: int = Grid.DEFAULT_SIZE, ship_types: tuple[ShipType, ...] = Fleet.CLASSIC
    ) -> None:
        """Crée un joueur avec sa propre grille et sa propre flotte, selon les réglages de la partie."""
        self.name = name
        self.grid = Grid(grid_size)
        self.fleet = Fleet(ship_types)

    @property
    def is_defeated(self) -> bool:
        """Vaincu quand toute sa flotte est coulée."""
        return self.fleet.is_destroyed

    def receive_shot(self, row: int, col: int) -> ShotResult:
        """Encaisse un tir adverse sur sa propre grille et annonce le résultat."""
        cell = self.grid[row, col]
        if not cell.shoot():
            return ShotResult.MISS
        return ShotResult.SUNK if cell.ship.is_sunk else ShotResult.HIT

    @abstractmethod
    def place_fleet(self) -> None:
        """Place toute la flotte sur sa grille."""

    @abstractmethod
    def choose_target(self, enemy_grid: Grid) -> tuple[int, int]:
        """Choisit une case jamais visée ; seule la vue adverse de la grille doit servir."""

    def __str__(self) -> str:
        """Nom du joueur, utilisé dans les annonces."""
        return self.name

    def __repr__(self) -> str:
        """Représentation pour le débogueur, avec le vrai type du joueur (humain ou ordinateur)."""
        return f"{type(self).__name__}(name={self.name!r}, fleet={self.fleet!r})"
