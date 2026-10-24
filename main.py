from ComputerPlayer import ComputerPlayer
from HumanPlayer import HumanPlayer
from console_ui import show_grids

if __name__ == "__main__":
    human, computer = HumanPlayer("Michaël"), ComputerPlayer("Ordinateur")
    for player in (human, computer):
        player.place_fleet()  # même appel, comportement différent selon le joueur
    show_grids(human.grid, human.fleet, computer.grid)
