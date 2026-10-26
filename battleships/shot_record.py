"""L’enregistrement immuable d’un coup joué, pour l’historique de la partie."""

from dataclasses import dataclass

from battleships.player import ShotResult


@dataclass(frozen=True)
class ShotRecord:
    """Un coup joué, figé une fois enregistré : qui a tiré, où, et avec quel résultat."""

    shooter: str  # nom du tireur (une copie, pas une référence au joueur)
    position: str  # coordonnée lisible, ex. "B7"
    result: ShotResult  # résultat du tir
    ship_name: str | None = None  # bateau touché ou coulé (le règlement le fait nommer) ; None si à l'eau
