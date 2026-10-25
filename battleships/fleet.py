"""Règles de composition d’une flotte (types de bateaux) et flotte d’un joueur."""

from dataclasses import dataclass

from battleships.ship import Ship


@dataclass(frozen=True)
class ShipType:
    """Une ligne de règle du jeu : un type de bateau, sa longueur et son nombre d'exemplaires."""

    name: str
    length: int
    count: int = 1

    def __post_init__(self) -> None:
        """Valide la règle dès sa création : longueur et nombre d’exemplaires au moins égaux à 1."""
        if self.length < 1 or self.count < 1:
            raise ValueError(f"{self.name} la longueur et le nombre doivent valoir au moins 1")


class Fleet:
    """La flotte d'un joueur, construite à partir d'une règle (la flotte classique par défaut)."""

    CLASSIC = (
        ShipType("Porte-Avions", 5),
        ShipType("Croiseur", 4),
        ShipType("Contre-Torpilleur", 3),
        ShipType("Sous-Marin", 3),
        ShipType("Torpilleur", 2),
    )

    def __init__(self, ship_types: tuple[ShipType, ...] = CLASSIC) -> None:
        """Construit les bateaux décrits par la règle ; les exemplaires multiples sont numérotés (ex. « Mine-1 »)."""
        if not ship_types:
            raise ValueError("Une flotte doit contenir au moins un type de bateau.")
        names = [ship_type.name for ship_type in ship_types]
        if len(set(names)) != len(names):
            raise ValueError("Deux types de bateaux portent le même nom")
        self.ships: list[Ship] = []
        for ship_type in ship_types:
            # Numérotation seulement s'il y a plusieurs exemplaires : "Mine-1", "Mine-2"...
            for number in range(1, ship_type.count + 1):
                name = ship_type.name if ship_type.count == 1 else f"{ship_type.name}-{number}"
                self.ships.append(Ship(name, ship_type.length))

    @property
    def is_destroyed(self) -> bool:
        """Flotte détruite quand tous ses bateaux sont coulés (calculé, jamais stocké)."""
        return all(ship.is_sunk for ship in self.ships)

    def __iter__(self):
        """Permet de parcourir les bateaux : for ship in fleet."""
        return iter(self.ships)

    def __len__(self) -> int:
        """Nombre de bateaux de la flotte : len(fleet)."""
        return len(self.ships)

    def __repr__(self) -> str:
        """Représentation pour le débogueur : chaque bateau avec sa longueur."""
        return f"Fleet({', '.join(f'{ship.name}({ship.length})' for ship in self.ships)})"
