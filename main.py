from ComputerPlayer import ComputerPlayer
from Game import Game
from HumanPlayer import HumanPlayer
from console_ui import ask_name

if __name__ == "__main__":
    try:
        Game(HumanPlayer(ask_name()), ComputerPlayer("Ordinateur")).play()
    except (KeyboardInterrupt, EOFError):
        print("\nPartie interrompue")
