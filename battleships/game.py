"""Le déroulement d’une partie."""

import random
from collections.abc import Callable

from battleships.game_view import GameView
from battleships.player import Player, ShotResult
from battleships.shot_record import ShotRecord


class Game:
    """Une partie entre deux joueurs : placement des flottes, tirage au sort, tours alternés, victoire."""

    def __init__(
        self, first: Player, second: Player, *, view: GameView, on_shot: Callable[[ShotRecord], None] | None = None
    ) -> None:
        """Prépare la partie : mêmes règles des deux côtés, tirage au sort du premier tireur, interface à prévenir.

        view reçoit les annonces de la partie ; on_shot est un observateur facultatif (ex. vue spectateur).
        """
        if first.rules != second.rules:
            raise ValueError("Les deux joueurs doivent jouer avec les mêmes règles")
        self.players = [first, second]
        random.shuffle(self.players)  # tirage au sort : celui qui commence a un avantage
        self._view = view
        self._history: list[ShotRecord] = []
        self._on_shot = on_shot

    @property
    def history(self) -> tuple[ShotRecord, ...]:
        """Tous les coups joués, dans l'ordre ; en lecture seule pour l'extérieur."""
        return tuple(self._history)

    def play(self) -> Player:
        """Joue la partie jusqu'au bout et renvoie le vainqueur."""
        for player in self.players:
            player.place_fleet()
        shooter, target = self.players
        self._view.announce_start(shooter)
        while True:
            row, col = shooter.choose_target(target.grid)
            result = target.receive_shot(row, col)
            cell = target.grid[row, col]
            sunk_ship = cell.ship.name if result is ShotResult.SUNK else None
            record = ShotRecord(str(shooter), str(cell), result, sunk_ship)
            self._history.append(record)
            self._view.announce_shot(record)
            if self._on_shot:
                self._on_shot(record)
            if target.is_defeated:
                self._view.announce_winner(shooter, target, self.history)
                return shooter
            shooter, target = target, shooter
