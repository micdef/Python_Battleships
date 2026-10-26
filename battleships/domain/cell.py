"""Une case de la grille : son contenu (eau ou bateau), les tirs reçus et ses deux affichages."""


class Cell:
    """Une case de la grille : sait si elle porte un bateau et si elle a reçu un tir."""

    # Attributs de classe : partagés par toutes les instances (≈ static readonly en C#)
    WATER = "~"
    SHIP = "B"
    HIT = "X"
    MISS = "o"
    UNKNOWN = "."

    def __init__(self, row: int, col: int) -> None:
        """Crée une case vide (de l’eau), jamais visée, à la position (row, col)."""
        # Attributs d'instance : propres à chaque case
        self.row = row
        self.col = col
        self.ship = None  # Le bateau qui occupe la case ; None = de l'eau
        self.hit = False  # True dès que la case a reçu un tir

    @property
    def has_ship(self) -> bool:
        """Indique si un bateau occupe la case."""
        return self.ship is not None

    def shoot(self) -> bool:
        """Reçoit un tir. Renvoie True si un bateau est touché."""
        if self.hit:
            raise ValueError(f"La case {self} a déjà été visée.")
        self.hit = True
        return self.has_ship

    @property
    def own_symbol(self) -> str:
        """Vue du propriétaire (ma grille de bateaux) : tout est visible."""
        if self.hit:
            return Cell.HIT if self.has_ship else Cell.MISS
        return Cell.SHIP if self.has_ship else Cell.WATER

    @property
    def enemy_symbol(self) -> str:
        """Vue de l'adversaire (ma grille de tirs) : les bateaux non touchés restent cachés."""
        if self.hit:
            return Cell.HIT if self.has_ship else Cell.MISS
        return Cell.UNKNOWN

    def __str__(self) -> str:
        """Coordonnée lisible par le joueur, ex. « B7 » (colonne en lettre, ligne à partir de 1)."""
        return f"{chr(ord('A') + self.col)}{self.row + 1}"

    def __repr__(self) -> str:
        """Représentation pour le débogueur ; le bateau est nommé, pas développé (pas de récursion avec Ship)."""
        ship_name = self.ship.name if self.has_ship else None
        return f"Cell(row={self.row}, col={self.col}, ship={ship_name!r}, hit={self.hit})"
