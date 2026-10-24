from Fleet import Fleet
from Grid import Grid
from console_ui import place_manually

if __name__ == "__main__":
    mine = Grid()
    place_manually(mine, Fleet())
    print("\n".join(mine.render(reveal=True)))
