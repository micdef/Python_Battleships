import re
from collections.abc import Callable

from Cell import Cell
from Fleet import Fleet
from Grid import Grid

# Codes couleur ANSI : une couleur par bateau sur sa propre grille (le rouge reste libre pour plus tard)
RESET = "\033[0m"
SHIP_COLORS = ("\033[94m", "\033[92m", "\033[93m", "\033[95m", "\033[96m", "\033[33m")
ANSI_CODE = re.compile(r"\x1b\[[0-9;]*m")


def ship_colorizer(fleet: Fleet) -> Callable[[Cell, str], str]:
    """Renvoie la fonction qui colore chaque case de bateau avec la couleur propre à ce bateau."""
    colors = {ship: SHIP_COLORS[index % len(SHIP_COLORS)] for index, ship in enumerate(fleet)}

    def style(cell: Cell, symbol: str) -> str:
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


def place_manually(grid: Grid, fleet: Fleet, read: Callable[[str], str] = input) -> None:
    """Fait placer chaque bateau par le joueur ; redemande tant que la saisie est refusée."""
    for ship in fleet:
        while True:
            print("\n".join(grid.render(reveal=True, style=ship_colorizer(fleet))))
            answer = read(f"{ship} ({ship.length} cases), position et sens (ex. B7 H) : ")
            try:
                row, col, horizontal = parse_placement(answer, grid)
                grid.place(ship, row, col, horizontal=horizontal)
                break
            except ValueError as error:
                print(f"Refusé : {error}\n")


def ask_automatic_placement(read: Callable[[str], str] = input) -> bool:
    """Demande le mode de placement ; True pour automatique."""
    while True:
        answer = read("Placement automatique (A) ou manuel (M) ? ").strip().upper()
        if answer in ("A", "M"):
            return answer == "A"
        print("Refusé : répondez A ou M\n")


def ask_target(enemy_grid: Grid, read: Callable[[str], str] = input) -> tuple[int, int]:
    """Demande une case à viser ; refuse les cases hors grille ou déjà visées."""
    while True:
        answer = read("Votre tir (ex. B7) : ")
        try:
            row, col = enemy_grid.parse_position(answer)
            if enemy_grid[row, col].hit:
                raise ValueError(f"{enemy_grid[row, col]} a déjà été visée")
            return row, col
        except ValueError as error:
            print(f"Refusé : {error}\n")


def show_grids(own_grid: Grid, own_fleet: Fleet, enemy_grid: Grid) -> None:
    """Affiche côte à côte sa grille de bateaux (en couleurs) et sa grille de tirs (vue adverse), avec leurs titres."""
    left = ["Bateaux :"] + own_grid.render(reveal=True, style=ship_colorizer(own_fleet))
    right = ["Tirs :"] + enemy_grid.render()
    width = max(visible_len(line) for line in left)  # largeur de la colonne de gauche, titre compris
    for left_line, right_line in zip(left, right):
        padding = " " * (width - visible_len(left_line))
        print(f"{left_line}{padding}      {right_line}")
