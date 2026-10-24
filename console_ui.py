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
        raise ValueError("Le sens doit être H (horizontal), V (vertical)")
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
                print(f"Refusé: {error}\n")
