import random

from Grid import Grid
from Player import Player


class ComputerPlayer(Player):
    """L'ordinateur : place sa flotte au hasard et tire au hasard sur les cases jamais visées."""

    def place_fleet(self) -> None:
        self.grid.place_randomly(self.fleet)

    def choose_target(self, enemy_grid: Grid) -> tuple[int, int]:
        # Seul cell.hit est consulté : l'ordinateur ne regarde jamais où sont les bateaux
        candidates = [(cell.row, cell.col) for row in enemy_grid.cells for cell in row if not cell.hit]
        return random.choice(candidates)
