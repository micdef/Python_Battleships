"""L’enregistrement immuable d’un coup joué, pour l’historique de la partie."""

from dataclasses import dataclass

from battleships.player import ShotResult


@dataclass(frozen=True)
class ShotRecord:
    """Un coup joué, figé une fois enregistré : qui a tiré, où, et avec quel résultat."""

    shooter: str  # nom du tireur (une copie, pas une référence au joueur)
    position: str  # coordonnée lisible, ex. "B7"
    result: ShotResult  # résultat du tir
    sunk_ship: str | None = None  # nom du bateau, seulement s'il vient d'être coulé
