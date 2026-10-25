"""Point d’entrée du jeu (python main.py) : choix du mode, puis lancement de la partie."""

from ComputerPlayer import ComputerPlayer
from console_ui import ask_delay, ask_name, ask_watch_mode, spectator_view
from Game import Game
from HumanPlayer import HumanPlayer

if __name__ == "__main__":
    try:
        if ask_watch_mode():
            first, second = ComputerPlayer("Ordinateur 1"), ComputerPlayer("Ordinateur 2")
            Game(first, second, on_shot=spectator_view(first, second, ask_delay())).play()
        else:
            Game(HumanPlayer(ask_name()), ComputerPlayer("Ordinateur")).play()
    except KeyboardInterrupt, EOFError:
        print("\nPartie interrompue")
