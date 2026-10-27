"""Le déroulement d’une partie."""

import random
from collections.abc import Callable

from battleships.application.game_view import GameView
from battleships.domain.player import Player
from battleships.domain.shot_record import ShotRecord


class Game:
    """Une partie entre deux joueurs, jouée tour par tour : tirage au sort, tirs alternés, victoire.

    Ce sont les clients (console, pygame...) qui la font avancer, un tir à la fois : la partie ne pose
    jamais de question et n'attend jamais de saisie.
    """

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
        self._shooter, self._target = self.players
        self._view = view
        self._history: list[ShotRecord] = []
        self._on_shot = on_shot
        self._started = False
        self._winner: Player | None = None

    @property
    def history(self) -> tuple[ShotRecord, ...]:
        """Tous les coups joués, dans l'ordre ; en lecture seule pour l'extérieur."""
        return tuple(self._history)

    @property
    def current_shooter(self) -> Player:
        """Le joueur dont c'est le tour de tirer."""
        return self._shooter

    @property
    def current_target(self) -> Player:
        """Le joueur qui reçoit le prochain tir."""
        return self._target

    @property
    def winner(self) -> Player | None:
        """Le vainqueur ; None tant que la partie n'est pas finie."""
        return self._winner

    @property
    def is_over(self) -> bool:
        """Indique si la partie est finie (un vainqueur est connu)."""
        return self._winner is not None

    def start(self) -> None:
        """Ouvre la partie et annonce le premier tireur ; les deux flottes doivent déjà être placées."""
        if self._started:
            raise RuntimeError("La partie a déjà commencé")
        if not all(player.fleet.is_placed for player in self.players):
            raise RuntimeError("Les deux flottes doivent être placées avant le premier tir")
        self._started = True
        self._view.announce_start(self._shooter)

    def play_turn(self, row: int, col: int) -> ShotRecord:
        """Joue le tir du joueur dont c'est le tour, puis passe la main (ou annonce le vainqueur).

        Un tir refusé (hors grille, case déjà visée) lève une erreur et ne consomme pas le tour.
        """
        if not self._started:
            raise RuntimeError("La partie n'a pas commencé")
        if self.is_over:
            raise RuntimeError("La partie est finie")
        shooter, target = self._shooter, self._target
        result = target.receive_shot(row, col)  # le domaine refuse les tirs invalides, avant tout changement
        cell = target.grid[row, col]
        ship_name = cell.ship.name if cell.has_ship else None  # le règlement fait nommer le bateau touché
        record = ShotRecord(str(shooter), str(cell), result, ship_name)
        self._history.append(record)
        self._view.announce_shot(record)
        if self._on_shot:
            self._on_shot(record)
        if target.is_defeated:
            self._winner = shooter
            self._view.announce_winner(shooter, target, self.history)
        else:
            self._shooter, self._target = target, shooter
        return record

    def play_automatic_turn(self) -> ShotRecord:
        """Fait jouer l'ordinateur dont c'est le tour : sa stratégie choisit la case."""
        if not self._shooter.is_automatic:
            raise RuntimeError(f"{self._shooter} choisit ses tirs lui-même")
        return self.play_turn(*self._shooter.choose_target(self._target.grid))
