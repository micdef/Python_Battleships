"""Un bateau : sa longueur, les cases qu’il occupe et son état « coulé »."""

from battleships.cell import Cell


class Ship:
    """Un bateau : connaît sa taille et ses cases, et sait s'il est coulé."""

    def __init__(self, name: str, length: int) -> None:
        """Crée un bateau pas encore placé ; sa longueur doit valoir au moins 1."""
        if length < 1:
            raise ValueError(f"Longueur {length} invalide pour {name}")
        self.name = name
        self.length = length
        self.cells: list[Cell] = []  # remplie par Grid.place()

    @property
    def is_placed(self) -> bool:
        """Indique si le bateau occupe toutes ses cases sur une grille."""
        return len(self.cells) == self.length

    @property
    def is_sunk(self) -> bool:
        """Coulé quand toutes ses cases ont reçu un tir (calculé, jamais stocké)."""
        return self.is_placed and all(cell.hit for cell in self.cells)

    def __str__(self) -> str:
        """Nom du bateau, utilisé dans les messages au joueur."""
        return self.name

    def __repr__(self) -> str:
        """Représentation pour le débogueur ; les cases sont données par leur coordonnée (pas de récursion avec Cell)"""
        positions = ", ".join(str(cell) for cell in self.cells)
        return f"Ship(name={self.name!r}, length={self.length}, cells=[{positions}], sunk={self.is_sunk})"
