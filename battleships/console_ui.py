"""Interface console : saisies du joueur, couleurs, affichage des grilles, annonces et historique."""

import re
import time
from collections.abc import Callable
from itertools import zip_longest

from battleships.cell import Cell
from battleships.fleet import Fleet
from battleships.game_view import GameView
from battleships.grid import Grid
from battleships.player import Player
from battleships.shot_record import ShotRecord

# Codes couleur ANSI : une couleur par bateau sur sa propre grille (le rouge reste libre pour plus tard)
RESET = "\033[0m"
SHIP_COLORS = ("\033[94m", "\033[92m", "\033[93m", "\033[95m", "\033[96m", "\033[33m")
ANSI_CODE = re.compile(r"\x1b\[[0-9;]*m")
CLEAR_SCREEN = "\033[H\033[2J\033[3J"  # curseur en haut à gauche, efface l'écran puis l'historique de défilement


def ship_colorizer(fleet: Fleet) -> Callable[[Cell, str], str]:
    """Renvoie la fonction qui colore chaque case de bateau avec la couleur propre à ce bateau."""
    colors = {ship: SHIP_COLORS[index % len(SHIP_COLORS)] for index, ship in enumerate(fleet)}

    def style(cell: Cell, symbol: str) -> str:
        """Colore le symbole d’une case de bateau ; les autres cases restent inchangées."""
        return f"{colors[cell.ship]}{symbol}{RESET}" if cell.has_ship else symbol

    return style


def visible_len(text: str) -> int:
    """Longueur affichée d'un texte : les codes couleur sont invisibles et ne comptent pas."""
    return len(ANSI_CODE.sub("", text))


def parse_placement(text: str, grid: Grid) -> tuple[int, int, bool]:
    """Découpe une saisie « B7 H » en (row, col, horizontal)."""
    parts = text.split()
    if len(parts) != 2:
        raise ValueError("Format attendu : coordonnée puis sens (ex. B7 H)")
    row, col = grid.parse_position(parts[0])
    direction = parts[1].upper()
    if direction not in ("H", "V"):
        raise ValueError("Le sens doit être H (horizontal) ou V (vertical)")
    return row, col, direction == "H"


def print_side_by_side(left_title: str, left_lines: list[str], right_title: str, right_lines: list[str]) -> None:
    """Affiche deux blocs de lignes côte à côte, chacun sous son titre, en ignorant les codes couleur."""
    left = [left_title] + left_lines
    right = [right_title] + right_lines
    width = max(visible_len(line) for line in left)  # largeur de la colonne de gauche, titre compris
    for left_line, right_line in zip(left, right, strict=True):
        padding = " " * (width - visible_len(left_line))
        print(f"{left_line}{padding}      {right_line}")


def show_grids(own_grid: Grid, own_fleet: Fleet, enemy_grid: Grid) -> None:
    """Affiche côte à côte sa grille de bateaux (en couleurs) et sa grille de tirs (vue adverse), avec leurs titres."""
    print_side_by_side(
        "Bateaux :", own_grid.render(reveal=True, style=ship_colorizer(own_fleet)), "Tirs :", enemy_grid.render()
    )


def format_shot(record: ShotRecord) -> str:
    """Texte d'un coup joué, identique dans les annonces et dans l'historique."""
    detail = f" ({record.sunk_ship})" if record.sunk_ship else ""
    return f"{record.shooter} tire en {record.position} : {record.result.value}{detail}"


def show_history(history: tuple[ShotRecord, ...]) -> None:
    """Affiche tous les coups de la partie, un tour par ligne (le premier tireur à gauche)."""
    print("\nHistorique de la partie :")
    first_shots, second_shots = history[0::2], history[1::2]
    width = max(len(format_shot(record)) for record in first_shots)
    for number, (first, second) in enumerate(zip_longest(first_shots, second_shots), start=1):
        right = format_shot(second) if second else ""
        print(f"{number:>3}. {format_shot(first):<{width}}   {right}")


def revealed_grid(player: Player) -> list[str]:
    """Grille complète d'un joueur, bateaux visibles et en couleurs (fin de partie, spectateur)."""
    return player.grid.render(reveal=True, style=ship_colorizer(player.fleet))


class ConsoleUI(GameView):
    """La console d'une partie : pose les questions au joueur et affiche le jeu.
    Déclare respecter le contrat GameView.
    Chaque instance a ses propres annonces en attente : deux consoles ne partagent rien.
    """

    def __init__(self, read: Callable[[str], str] = input) -> None:
        """Crée une console.
        read est la source des saisies : le clavier par défaut, une fausse saisie dans les tests.
        """
        self._read = read
        self._pending_messages: list[str] = []  # annonces affichées sous les grilles au prochain rafraîchissement

    # --- Questions au joueur ---

    def ask_name(self) -> str:
        """Demande le nom du joueur ; « Joueur » si la saisie est vide."""
        return self._read("Votre nom : ").strip() or "Joueur"

    def ask_watch_mode(self) -> bool:
        """Demande le mode de jeu ; True pour regarder une partie entre deux ordinateurs."""
        while True:
            answer = self._read(
                "1. Jouer contre l'ordinateur\n2. Regarder une partie ordinateur contre ordinateur\nVotre choix : "
            )
            if answer.strip() in ("1", "2"):
                return answer.strip() == "2"
            print("Refusé : répondez 1 ou 2\n")

    def ask_delay(self) -> float:
        """Demande la pause entre deux tirs, en secondes (0,5 par défaut, 0 à 5 acceptés)."""
        while True:
            answer = (
                self._read("Pause entre deux tirs, en secondes (Entrée = 0,5) (Min: 0,0 - Max 5,0) : ")
                .strip()
                .replace(",", ".")
            )
            if not answer:
                return 0.5
            try:
                delay = float(answer)
            except ValueError:
                print("Refusé : donnez un nombre (ex. 0,5)\n")
                continue
            if 0 <= delay <= 5:
                return delay
            print("Refusé : la pause doit être comprise entre 0,0 et 5,0 secondes\n")

    def ask_automatic_placement(self) -> bool:
        """Demande le mode de placement ; True pour automatique."""
        while True:
            answer = self._read("Placement automatique (A) ou manuel (M) ? ").strip().upper()
            if answer in ("A", "M"):
                return answer == "A"
            print("Refusé : répondez A ou M\n")

    def place_manually(self, grid: Grid, fleet: Fleet) -> None:
        """Fait placer chaque bateau par le joueur ; redemande tant que la saisie est refusée."""
        for ship in fleet:
            while True:
                print("\n".join(grid.render(reveal=True, style=ship_colorizer(fleet))))
                answer = self._read(f"{ship} ({ship.length} cases), position et sens (ex. B7 H) : ")
                try:
                    row, col, horizontal = parse_placement(answer, grid)
                    grid.place(ship, row, col, horizontal=horizontal)
                    break
                except ValueError as error:
                    print(f"Refusé : {error}\n")

    def ask_target(self, enemy_grid: Grid) -> tuple[int, int]:
        """Demande une case à viser ; refuse les cases hors grille ou déjà visées."""
        while True:
            answer = self._read("Votre tir (ex. B7) : ")
            try:
                row, col = enemy_grid.parse_position(answer)
                if enemy_grid[row, col].hit:
                    raise ValueError(f"{enemy_grid[row, col]} a déjà été visée")
                return row, col
            except ValueError as error:
                print(f"Refusé : {error}\n")

    # --- Affichage du jeu ---

    def refresh_screen(self, own_grid: Grid, own_fleet: Fleet, enemy_grid: Grid) -> None:
        """Efface l'écran et réaffiche les deux grilles, avec dessous les annonces depuis le dernier affichage."""
        print(CLEAR_SCREEN, end="")
        show_grids(own_grid, own_fleet, enemy_grid)
        print()
        self._flush_messages()
        print()

    def _flush_messages(self) -> None:
        """Affiche les annonces en attente, puis les oublie."""
        for message in self._pending_messages:
            print(message)
        self._pending_messages.clear()

    def spectator_view(self, left: Player, right: Player, delay: float) -> Callable[[ShotRecord], None]:
        """Renvoie l'observateur qui, après chaque tir, réaffiche les deux grilles dévoilées puis marque une pause."""

        def show(record: ShotRecord) -> None:
            """Après chaque tir : réaffiche les deux flottes dévoilées et le dernier tir, puis marque la pause."""
            print(CLEAR_SCREEN, end="")
            print_side_by_side(f"{left} :", revealed_grid(left), f"{right} :", revealed_grid(right))
            print()
            self._flush_messages()
            time.sleep(delay)

        return show

    # --- Contrat GameView : les annonces de la partie ---

    def announce_start(self, first: Player) -> None:
        """Met en attente l’annonce du tirage au sort, affichée au prochain rafraîchissement."""
        self._pending_messages.append(f"Tirage au sort : {first} commence.")

    def announce_shot(self, record: ShotRecord) -> None:
        """Met en attente l’annonce d’un tir, affichée au prochain rafraîchissement."""
        self._pending_messages.append(format_shot(record))

    def announce_winner(self, winner: Player, loser: Player, history: tuple[ShotRecord, ...]) -> None:
        """Écran final : derniers tirs, vainqueur, les deux grilles dévoilées et l'historique de la partie."""
        print(CLEAR_SCREEN, end="")
        self._flush_messages()
        print(f"\n{winner} a gagné !")
        print_side_by_side(f"{winner} :", revealed_grid(winner), f"{loser} :", revealed_grid(loser))
        show_history(history)
