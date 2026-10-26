"""Les règles d'une partie, réunies en un seul endroit (les règles d'origine de la bataille navale par défaut).

Règlement de référence : https://www.zpag.net/Jeux/battleship_reglement.html
"""

from dataclasses import dataclass

from battleships.domain.fleet import Fleet, ShipType
from battleships.domain.grid import Grid


@dataclass(frozen=True)
class Rules:
    """Les règles d'une partie : taille de la grille et composition de la flotte.

    Les autres règles d'origine sont fixes : bateaux posés horizontalement ou verticalement, sans dépasser
    de la grille ; un seul tir par tour, à tour de rôle ; le premier tireur est tiré au sort
    (l'équivalent, face à l'ordinateur, de « les joueurs décident ensemble qui commence »).
    """

    grid_size: int = Grid.DEFAULT_SIZE
    ship_types: tuple[ShipType, ...] = Fleet.CLASSIC

    def __post_init__(self) -> None:
        """Valide les règles dès leur création, avant toute partie : grille dans les limites, flotte qui y tient."""
        if not Grid.MIN_SIZE <= self.grid_size <= Grid.MAX_SIZE:
            raise ValueError(f"Taille {self.grid_size} est hors limites ({Grid.MIN_SIZE} à {Grid.MAX_SIZE})")
        fleet_cells = sum(ship_type.length * ship_type.count for ship_type in self.ship_types)
        if fleet_cells > self.grid_size**2:
            raise ValueError(f"La flotte ({fleet_cells} cases) ne tient pas dans la grille de {self.grid_size}")


CLASSIC_RULES = Rules()  # les règles d'origine : grille de 10 sur 10 et flotte classique
