"""Point d’entrée du jeu (python main.py) : choix du mode, puis lancement de la partie."""

from battleships.application.game import Game
from battleships.clients.console.human_player import HumanPlayer
from battleships.clients.console.ui import ConsoleUI
from battleships.domain.computer_player import ComputerPlayer

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
