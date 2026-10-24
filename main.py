from Fleet import Fleet
from Grid import Grid

if __name__ == "__main__":
    mine = Grid()
    mine.place_randomly(Fleet())
    print("\n".join(mine.render(reveal=True)))
