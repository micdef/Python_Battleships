"""La grille de jeu : ses cases, la lecture des coordonnées, l’affichage et le placement des bateaux."""

import random
import re
from collections.abc import Callable

from battleships.domain.cell import Cell
from battleships.domain.fleet import Fleet
from battleships.domain.ship import Ship


class Grid:
    """Grille carrée de cases ; sait s'afficher pour son propriétaire ou pour l'adversaire."""

    MIN_SIZE = 10
    MAX_SIZE = 26  # Une lettre par colonne : A à Z
    DEFAULT_SIZE = 10  # Taille d'une bataille navale classique

    def __init__(self, size: int = DEFAULT_SIZE) -> None:
        """Crée une grille carrée de cases vides ; la taille doit rester entre MIN_SIZE et MAX_SIZE."""
        if not Grid.MIN_SIZE <= size <= Grid.MAX_SIZE:
            raise ValueError(f"Taille {size} hors limites ({Grid.MIN_SIZE} à {Grid.MAX_SIZE})")
        self.size = size
        # Liste de listes créée dans __init__ : chaque grille a ses propres cases
        self.cells = [[Cell(row, col) for col in range(size)] for row in range(size)]

    def contains(self, row: int, col: int) -> bool:
        """Indique si la position (row, col) est dans la grille."""
        return 0 <= row < self.size and 0 <= col < self.size

    def parse_position(self, text: str) -> tuple[int, int]:
        """Convertit une coordonnée saisie (ex. "B7") en (row, col) : l'inverse de str(cell)."""
        match = re.fullmatch(r"([A-Z])(\d{1,2})", text.strip().upper())
        if match is None:
            raise ValueError(f"« {text.strip()} » n'est pas une coordonnée (ex. B7)")
        row = int(match.group(2)) - 1
        col = ord(match.group(1)) - ord("A")
        if not self.contains(row, col):
            raise ValueError(f"{match.group(0)} est hors de la grille")
        return row, col

    def __getitem__(self, position: tuple[int, int]) -> Cell:
        """Accès par grid[row, col] (≈ indexeur this[int row, int col] en C#)."""
        row, col = position
        if not self.contains(row, col):
            raise IndexError(f"Position ({row}, {col}) hors de la grille")
        return self.cells[row][col]

    def render(self, *, reveal: bool = False, style: Callable[[Cell, str], str] | None = None) -> list[str]:
        """Renvoie les lignes de la grille ; reveal=True pour la vue du propriétaire.
        style, fourni par l'interface, peut habiller chaque symbole (couleurs...) sans que la grille le sache.
        """
        lines = ["   " + " ".join(chr(ord("A") + col) for col in range(self.size))]
        for number, row in enumerate(self.cells, start=1):
            symbols = []
            for cell in row:
                symbol = cell.own_symbol if reveal else cell.enemy_symbol
                symbols.append(style(cell, symbol) if style else symbol)
            lines.append(f"{number:>2} " + " ".join(symbols))
        return lines

    def place(self, ship: Ship, row: int, col: int, *, horizontal: bool) -> None:
        """Place un bateau à partir de (row, col), vers la droite ou vers le bas. Tout ou rien."""
        if ship.is_placed:
            raise ValueError(f"{ship} est déjà placé")
        d_row, d_col = (0, 1) if horizontal else (1, 0)
        end_row = row + d_row * (ship.length - 1)
        end_col = col + d_col * (ship.length - 1)
        if not (self.contains(row, col) and self.contains(end_row, end_col)):
            raise ValueError(f"{ship} déborderait de la grille")
        cells = [self[row + d_row * i, col + d_col * i] for i in range(ship.length)]
        if any(cell.has_ship for cell in cells):
            raise ValueError(f"{ship} chevaucherait un autre bateau")

        # Toutes les vérifications sont passées : on modifie seulement maintenant
        for cell in cells:
            cell.ship = ship
        ship.cells = cells

    def remove(self, ship: Ship) -> None:
        """Retire un bateau de la grille, tant qu'il n'a pas été touché (annulation d'un placement)."""
        if any(cell.hit for cell in ship.cells):
            raise ValueError(f"{ship} a déjà été touché : on ne peut plus le retirer")
        for cell in ship.cells:
            cell.ship = None
        ship.cells = []

    def place_randomly(self, fleet: Fleet, *, max_attempts: int = 100) -> None:
        """Place toute la flotte au hasard, des plus grands bateaux aux plus petits. Tout ou rien."""
        if any(ship.is_placed for ship in fleet):
            raise ValueError("La flotte est déjà (en partie) placée")
        if sum(ship.length for ship in fleet) > self.size**2:
            raise ValueError("La flotte ne tient pas dans la grille")
        ships = sorted(fleet, key=lambda ship: ship.length, reverse=True)
        for _ in range(max_attempts):
            placed: list[Ship] = []
            for ship in ships:
                if not self._place_at_random_position(ship):
                    break
                placed.append(ship)
            if len(placed) == len(ships):
                return
            # Impasse : on annule cette tentative et on recommence avec une grille vide
            for ship in placed:
                self.remove(ship)
        raise ValueError(f"Impossible de placer la flotte en {max_attempts} tentatives")

    def _place_at_random_position(self, ship: Ship) -> bool:
        """Essaie toutes les positions dans un ordre aléatoire ; False si aucune ne convient."""
        positions = [
            (row, col, horizontal)
            for row in range(self.size)
            for col in range(self.size)
            for horizontal in (True, False)
        ]
        random.shuffle(positions)
        for row, col, horizontal in positions:
            try:
                self.place(ship, row, col, horizontal=horizontal)
                return True
            except ValueError:
                continue  # position refusée par place() : on essaie la suivante
        return False

    def __repr__(self) -> str:
        """Représentation pour le débogueur : la taille de la grille."""
        return f"Grid(size={self.size})"
