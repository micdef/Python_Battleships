"""Le contrat qu'une interface doit respecter pour suivre une partie (la console aujourd'hui, pygame demain)."""

from abc import abstractmethod
from typing import Protocol

from battleships.domain.player import Player
from battleships.domain.shot_record import ShotRecord


class GameView(Protocol):
    """Ce que la partie attend de son interface : être prévenue du début, de chaque tir et de la fin.

    Une classe peut le respecter de deux façons :
    - en le déclarant, comme ConsoleUI(GameView) : Python refuse alors de créer l'objet s'il manque une méthode ;
    - simplement en ayant les trois méthodes, sans le déclarer (pratique pour une fausse interface de test).
    """

    @abstractmethod
    def announce_start(self, first: Player) -> None:
        """Annonce le joueur tiré au sort pour commencer."""

    @abstractmethod
    def announce_shot(self, record: ShotRecord) -> None:
        """Annonce un tir et son résultat."""

    @abstractmethod
    def announce_winner(self, winner: Player, loser: Player, history: tuple[ShotRecord, ...]) -> None:
        """Annonce le vainqueur, en fin de partie, avec l'historique complet des coups."""
