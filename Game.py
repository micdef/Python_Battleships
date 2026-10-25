import random
from collections.abc import Callable

from Player import Player, ShotResult
from ShotRecord import ShotRecord
from console_ui import announce_shot, announce_start, announce_winner


class Game:
    """Une partie entre deux joueurs : placement des flottes, tirage au sort, tours alternés, victoire."""

    def __init__(self, first: Player, second: Player, *, on_shot: Callable[[ShotRecord], None] | None = None) -> None:
        if first.grid.size != second.grid.size:
            raise ValueError("Les deux joueurs doivent avoir des grilles de même taille")
        self.players = [first, second]
        random.shuffle(self.players)  # tirage au sort : celui qui commence a un avantage
        self._history: list[ShotRecord] = []
        self._on_shot = on_shot  # observateur facultatif, prévenu après chaque tir (ex. vue spectateur)

    @property
    def history(self) -> tuple[ShotRecord, ...]:
        """Tous les coups joués, dans l'ordre ; en lecture seule pour l'extérieur."""
        return tuple(self._history)

    def play(self) -> Player:
        """Joue la partie jusqu'au bout et renvoie le vainqueur."""
        for player in self.players:
            player.place_fleet()
        shooter, target = self.players
        announce_start(shooter)
        while True:
            row, col = shooter.choose_target(target.grid)
            result = target.receive_shot(row, col)
            cell = target.grid[row, col]
            sunk_ship = cell.ship.name if result is ShotResult.SUNK else None
            record = ShotRecord(str(shooter), str(cell), result, sunk_ship)
            self._history.append(record)
            announce_shot(record)
            if self._on_shot:
                self._on_shot(record)
            if target.is_defeated:
                announce_winner(shooter, target, self.history)
                return shooter
            shooter, target = target, shooter
