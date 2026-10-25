"""Point d’entrée du jeu (python main.py) : choix du mode, puis lancement de la partie."""

from battleships.computer_player import ComputerPlayer
from battleships.console_ui import ConsoleUI
from battleships.game import Game
from battleships.human_player import HumanPlayer

if __name__ == "__main__":
    # Point d'assemblage : c'est ici, et seulement ici, que l'on choisit l'interface et qu'on la donne aux objets
    ui = ConsoleUI()
    try:
        if ui.ask_watch_mode():
            first, second = ComputerPlayer("Ordinateur 1"), ComputerPlayer("Ordinateur 2")
            Game(first, second, view=ui, on_shot=ui.spectator_view(first, second, ui.ask_delay())).play()
        else:
            Game(HumanPlayer(ui.ask_name(), ui), ComputerPlayer("Ordinateur"), view=ui).play()
    except KeyboardInterrupt, EOFError:
        print("\nPartie interrompue")
