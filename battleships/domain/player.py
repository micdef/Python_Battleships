"""Le joueur et le résultat d'un tir."""

from enum import Enum

from battleships.domain.fleet import Fleet
from battleships.domain.grid import Grid
from battleships.domain.rules import CLASSIC_RULES, Rules
from battleships.domain.strategy import TargetingStrategy


class ShotResult(Enum):
    """Résultat d'un tir, tel qu'il est annoncé au tireur."""

    MISS = "À l'eau"
    HIT = "Touché"
    SUNK = "Coulé"


class Player:
    """Un joueur : sa grille et sa flotte ; l'ordinateur a en plus une stratégie de tir, l'humain n'en a pas."""

    def __init__(self, name: str, rules: Rules = CLASSIC_RULES, strategy: TargetingStrategy | None = None) -> None:
        """Crée un joueur avec sa propre grille et sa propre flotte, selon les règles de la partie.

        strategy est la façon dont l'ordinateur choisit ses tirs ; None pour un joueur humain.
        """
        self.name = name
        self.rules = rules
        self.grid = Grid(rules.grid_size)
        self.fleet = Fleet(rules.ship_types)
        self.strategy = strategy

    @property
    def is_automatic(self) -> bool:
        """Indique si le joueur choisit seul ses tirs (l'ordinateur), sans qu'on le lui demande."""
        return self.strategy is not None

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

    def place_fleet(self) -> None:
        """Place toute la flotte au hasard (le joueur humain en console redéfinit ce choix)."""
        self.grid.place_randomly(self.fleet)

    def choose_target(self, enemy_grid: Grid) -> tuple[int, int]:
        """Confie le choix du tir à la stratégie ; refusé pour un joueur qui n'en a pas."""
        if self.strategy is None:
            raise ValueError(f"{self} n'a pas de stratégie : il choisit ses tirs lui-même")
        return self.strategy.choose_target(enemy_grid)

    def __str__(self) -> str:
        """Nom du joueur, utilisé dans les annonces."""
        return self.name

    def __repr__(self) -> str:
        """Représentation pour le débogueur, avec la stratégie de tir (None pour un humain)."""
        strategy = type(self.strategy).__name__ if self.strategy else None
        return f"{type(self).__name__}(name={self.name!r}, strategy={strategy}, fleet={self.fleet!r})"
