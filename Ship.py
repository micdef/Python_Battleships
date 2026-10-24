from Cell import Cell


class Ship:
    """Un bateau : connaît sa taille et ses cases, et sait s'il est coulé."""

    def __init__(self, name: str, length: int) -> None:
        if length < 1:
            raise ValueError(f"Longueur {length} invalide pour {name}")
        self.name = name
        self.length = length
        self.cells: list[Cell] = []  # remplie par Grid.place()

    @property
    def is_placed(self) -> bool:
        return len(self.cells) == self.length

    @property
    def is_sunk(self) -> bool:
        """Coulé quand toutes ses cases ont reçu un tir (calculé, jamais stocké)."""
        return self.is_placed and all(cell.hit for cell in self.cells)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        # Les cases sont affichées par leur coordonnée (__str__) : pas de récursion Ship <-> Cell
        positions = ", ".join(str(cell) for cell in self.cells)
        return f"Ship(name={self.name!r}, length={self.length}, cells=[{positions}], sunk={self.is_sunk})"
