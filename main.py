"""Point d’entrée du jeu (python main.py) : choix du mode, puis lancement de la partie."""

from battleships.application.game import Game
from battleships.clients.console.game_loop import run_game
from battleships.clients.console.ui import ConsoleUI
from battleships.domain.player import Player
from battleships.domain.strategy import RandomStrategy

if __name__ == "__main__":
    # Point d'assemblage : c'est ici, et seulement ici, que l'on choisit l'interface et qu'on la donne aux objets
    ui = ConsoleUI()
    try:
        if ui.ask_watch_mode():
            first = Player("Ordinateur 1", strategy=RandomStrategy())
            second = Player("Ordinateur 2", strategy=RandomStrategy())
            game = Game(first, second, view=ui, on_shot=ui.spectator_view(first, second, ui.ask_delay()))
        else:
            game = Game(Player(ui.ask_name()), Player("Ordinateur", strategy=RandomStrategy()), view=ui)
        run_game(game, ui)
    except KeyboardInterrupt, EOFError:
        print("\nPartie interrompue")
