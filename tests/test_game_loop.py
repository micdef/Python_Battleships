"""Tests de la boucle de partie en console : placement des flottes et partie complète au clavier."""

from battleships.application.game import Game
from battleships.clients.console.game_loop import place_fleet, run_game
from battleships.domain.fleet import ShipType
from battleships.domain.player import Player
from battleships.domain.rules import Rules


def test_computer_places_its_fleet_without_any_question(computer, console):
    """L'ordinateur place sa flotte seul : la console ne lui pose aucune question."""
    player = computer("Ordinateur")
    place_fleet(player, console())  # aucune réponse prévue : une question ferait échouer le test
    assert player.fleet.is_placed


def test_human_can_choose_automatic_placement_after_a_typo(console, capsys):
    """Une réponse invalide est refusée, puis le placement automatique est accepté."""
    human = Player("Michaël")
    place_fleet(human, console("x", "A"))
    assert human.fleet.is_placed
    assert "Refusé : répondez A ou M" in capsys.readouterr().out


def test_human_can_place_manually(console):
    """Le joueur peut placer ses bateaux lui-même au clavier."""
    human = Player("Michaël", Rules(ship_types=(ShipType("Torpilleur", 2),)))
    place_fleet(human, console("M", "A1 V"))
    assert [str(cell) for cell in human.fleet.ships[0].cells] == ["A1", "A2"]


def test_two_computers_play_a_whole_game_without_any_question(computer, console, capsys):
    """Mode spectateur : la boucle mène une partie entre deux ordinateurs sans rien demander."""
    game = Game(computer("A"), computer("B"), view=console())
    winner = run_game(game, console())
    assert winner is game.winner
    assert game.is_over


def test_scripted_human_can_play_a_whole_game(computer, console, capsys):
    """Une partie complète contre l’ordinateur va jusqu’au bout avec un joueur au clavier."""
    every_cell = [f"{chr(ord('A') + col)}{row + 1}" for row in range(10) for col in range(10)]
    ui = console("A", *every_cell)
    game = Game(Player("Michaël"), computer("Ordinateur"), view=ui)
    winner = run_game(game, ui)
    assert winner.name in ("Michaël", "Ordinateur")
    assert any(record.shooter == "Michaël" for record in game.history)
