from collections.abc import Callable

from Fleet import Fleet
from Grid import Grid


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
            print("\n".join(grid.render(reveal=True)))
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


def show_grids(own_grid: Grid, enemy_grid: Grid) -> None:
    """Affiche côte à côte sa grille de bateaux et sa grille de tirs (vue adverse), chacune avec son titre."""
    left = ["Bateaux :"] + own_grid.render(reveal=True)
    right = ["Tirs :"] + enemy_grid.render()
    width = max(len(line) for line in left)  # largeur de la colonne de gauche, titre compris
    for left_line, right_line in zip(left, right):
        print(f"{left_line:<{width}}      {right_line}")
