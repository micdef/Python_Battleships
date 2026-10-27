"""Tests de l'interface console : saisies, mise en forme des annonces et affichage côte à côte."""

import pytest

from battleships.clients.console.ui import (
    ANSI_CODE,
    ConsoleUI,
    format_shot,
    parse_placement,
    print_side_by_side,
    ship_colorizer,
    show_history,
    visible_len,
)
from battleships.domain.fleet import Fleet
from battleships.domain.grid import Grid
from battleships.domain.player import ShotResult
from battleships.domain.shot_record import ShotRecord


@pytest.mark.parametrize(("text", "expected"), [("B7 H", (6, 1, True)), (" a1   v ", (0, 0, False))])
def test_parse_placement_reads_position_and_direction(text, expected):
    """Une saisie de placement donne la case de départ et le sens, espaces et casse ignorés."""
    assert parse_placement(text, Grid()) == expected


@pytest.mark.parametrize(
    ("text", "message"), [("B7", "Format"), ("B7 H V", "Format"), ("B7 X", "sens"), ("Z1 H", "hors")]
)
def test_parse_placement_refuses_invalid_text(text, message):
    """Une saisie de placement incomplète, au sens inconnu ou hors grille est refusée."""
    with pytest.raises(ValueError, match=message):
        parse_placement(text, Grid())


@pytest.mark.parametrize(("answer", "expected"), [("", 0.5), ("1.5", 1.5), ("0,5", 0.5), (" 0,2 ", 0.2)])
def test_ask_delay_accepts_point_comma_and_default(console, answer, expected):
    """Régression : la conversion de la virgule s'appliquait à la question au lieu de la réponse."""
    assert console(answer).ask_delay() == expected


def test_ask_delay_asks_again_until_the_value_is_valid(console, capsys):
    """Une pause non numérique ou hors limites est redemandée."""
    assert console("abc", "9", "-1", "5").ask_delay() == 5
    assert capsys.readouterr().out.count("Refusé") == 3


def test_ask_watch_mode_asks_again_until_1_or_2(console):
    """Le menu redemande tant que le choix n’est pas 1 ou 2."""
    assert console("3", "2").ask_watch_mode() is True
    assert console("1").ask_watch_mode() is False


def test_empty_name_becomes_joueur(console):
    """Un nom vide devient « Joueur », et les espaces autour du nom sont retirés."""
    assert console("   ").ask_name() == "Joueur"
    assert console(" Michaël ").ask_name() == "Michaël"


def test_visible_len_ignores_color_codes():
    """Les codes couleur ne comptent pas dans la largeur affichée."""
    assert visible_len("\033[94mB\033[0m") == 1


def test_side_by_side_stays_aligned_with_colors(capsys):
    """Les couleurs ne décalent pas la grille de droite."""
    grid, fleet = Grid(), Fleet()
    grid.place_randomly(fleet)
    print_side_by_side("Bateaux :", grid.render(reveal=True, style=ship_colorizer(fleet)), "Tirs :", grid.render())
    lines = ANSI_CODE.sub("", capsys.readouterr().out).splitlines()
    right_column = len(lines[0]) - len("Tirs :")
    assert all(line[right_column - 6 : right_column] == " " * 6 for line in lines)


@pytest.mark.parametrize(
    ("result", "ship_name", "expected"),
    [
        (ShotResult.MISS, None, "Michaël tire en B7 : À l'eau"),
        (ShotResult.HIT, "Croiseur", "Michaël tire en B7 : Touché (Croiseur)"),
        (ShotResult.SUNK, "Croiseur", "Michaël tire en B7 : Coulé (Croiseur)"),
    ],
)
def test_format_shot_names_the_ship_hit_or_sunk(result, ship_name, expected):
    """Le bateau est nommé dès qu'il est touché, comme le veut le règlement (régression : parenthèse fermante)."""
    assert format_shot(ShotRecord("Michaël", "B7", result, ship_name)) == expected


def test_history_keeps_the_winning_shot_when_the_count_is_odd(capsys):
    """Le premier tireur qui gagne a tiré une fois de plus : zip_longest ne doit pas perdre ce dernier coup."""
    history = (
        ShotRecord("A", "A1", ShotResult.MISS),
        ShotRecord("B", "B1", ShotResult.MISS),
        ShotRecord("A", "C1", ShotResult.SUNK, "Torpilleur"),
    )
    show_history(history)
    assert "A tire en C1 : Coulé (Torpilleur)" in capsys.readouterr().out


def test_pending_messages_are_shown_once_under_the_grids(console, capsys):
    """Chaque annonce est affichée une seule fois, au rafraîchissement suivant."""
    ui = console()
    ui.announce_shot(ShotRecord("Ordinateur", "C2", ShotResult.HIT))
    ui.refresh_screen(Grid(), Fleet(), Grid())
    ui.refresh_screen(Grid(), Fleet(), Grid())
    assert capsys.readouterr().out.count("Ordinateur tire en C2 : Touché") == 1


def test_each_console_has_its_own_pending_messages(capsys):
    """Régression : les annonces en attente étaient un état global partagé par tout le programme."""
    first, second = ConsoleUI(), ConsoleUI()
    first.announce_shot(ShotRecord("Ordinateur", "C2", ShotResult.HIT))
    second.refresh_screen(Grid(), Fleet(), Grid())
    assert "Ordinateur tire en C2" not in capsys.readouterr().out


def test_ask_target_refuses_invalid_or_already_shot_cells(computer, console, capsys):
    """Le joueur ne peut viser ni une case hors grille, ni une case déjà visée."""
    enemy = computer("Cible")
    enemy.grid[6, 1].shoot()
    assert console("B7", "Z9", "C3").ask_target(enemy.grid) == (2, 2)
    output = capsys.readouterr().out
    assert "B7 a déjà été visée" in output
    assert "Z9 est hors de la grille" in output
