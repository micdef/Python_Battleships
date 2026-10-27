"""La boucle de partie en console : c'est elle qui fait avancer la partie, un tir à la fois."""

from battleships.application.game import Game
from battleships.clients.console.ui import ConsoleUI
from battleships.domain.player import Player


def place_fleet(player: Player, ui: ConsoleUI) -> None:
    """Place la flotte d'un joueur : au hasard pour l'ordinateur, au choix (automatique ou manuel) pour l'humain."""
    if player.is_automatic or ui.ask_automatic_placement():
        player.place_fleet()
    else:
        ui.place_manually(player.grid, player.fleet)


def run_game(game: Game, ui: ConsoleUI) -> Player:
    """Joue la partie jusqu'au bout et renvoie le vainqueur : l'ordinateur tire seul, l'humain au clavier."""
    for player in game.players:
        place_fleet(player, ui)
    game.start()
    while not game.is_over:
        shooter, target = game.current_shooter, game.current_target
        if shooter.is_automatic:
            game.play_automatic_turn()
        else:
            ui.refresh_screen(shooter.grid, shooter.fleet, target.grid)
            row, col = ui.ask_target(target.grid)
            game.play_turn(row, col)
    return game.winner
