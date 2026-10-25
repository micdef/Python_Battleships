import pytest

from Fleet import Fleet
from Grid import Grid
from Player import ShotResult
from ShotRecord import ShotRecord
from console_ui import (ANSI_CODE, announce_shot, ask_delay, ask_name, ask_watch_mode, format_shot, parse_placement,
                        print_side_by_side, refresh_screen, ship_colorizer, show_history, visible_len)


@pytest.mark.parametrize(("text", "expected"), [("B7 H", (6, 1, True)), (" a1   v ", (0, 0, False))])
def test_parse_placement_reads_position_and_direction(text, expected):
    assert parse_placement(text, Grid()) == expected


@pytest.mark.parametrize(("text", "message"), [("B7", "Format"), ("B7 H V", "Format"), ("B7 X", "sens"),
                                               ("Z1 H", "hors")])
def test_parse_placement_refuses_invalid_text(text, message):
    with pytest.raises(ValueError, match=message):
        parse_placement(text, Grid())


@pytest.mark.parametrize(("answer", "expected"), [("", 0.5), ("1.5", 1.5), ("0,5", 0.5), (" 0,2 ", 0.2)])
def test_ask_delay_accepts_point_comma_and_default(keyboard, answer, expected):
    """Régression : la conversion de la virgule s'appliquait à la question au lieu de la réponse."""
    assert ask_delay(keyboard(answer)) == expected


def test_ask_delay_asks_again_until_the_value_is_valid(keyboard, capsys):
    assert ask_delay(keyboard("abc", "9", "-1", "5")) == 5
    assert capsys.readouterr().out.count("Refusé") == 3


def test_ask_watch_mode_asks_again_until_1_or_2(keyboard):
    assert ask_watch_mode(keyboard("3", "2")) is True
    assert ask_watch_mode(keyboard("1")) is False


def test_empty_name_becomes_joueur(keyboard):
    assert ask_name(keyboard("   ")) == "Joueur"
    assert ask_name(keyboard(" Michaël ")) == "Michaël"


def test_visible_len_ignores_color_codes():
    assert visible_len("\033[94mB\033[0m") == 1


def test_side_by_side_stays_aligned_with_colors(capsys):
    grid, fleet = Grid(), Fleet()
    grid.place_randomly(fleet)
    print_side_by_side("Bateaux :", grid.render(reveal=True, style=ship_colorizer(fleet)),
                       "Tirs :", grid.render())
    lines = ANSI_CODE.sub("", capsys.readouterr().out).splitlines()
    right_column = len(lines[0]) - len("Tirs :")
    assert all(line[right_column - 6:right_column] == " " * 6 for line in lines)


def test_format_shot_names_the_sunk_ship():
    """Régression : la parenthèse fermante manquait après le nom du bateau."""
    record = ShotRecord("Michaël", "B7", ShotResult.SUNK, "Croiseur")
    assert format_shot(record) == "Michaël tire en B7 : Coulé (Croiseur)"


def test_history_keeps_the_winning_shot_when_the_count_is_odd(capsys):
    """Le premier tireur qui gagne a tiré une fois de plus : zip_longest ne doit pas perdre ce dernier coup."""
    history = (ShotRecord("A", "A1", ShotResult.MISS), ShotRecord("B", "B1", ShotResult.MISS),
               ShotRecord("A", "C1", ShotResult.SUNK, "Torpilleur"))
    show_history(history)
    assert "A tire en C1 : Coulé (Torpilleur)" in capsys.readouterr().out


def test_pending_messages_are_shown_once_under_the_grids(capsys):
    announce_shot(ShotRecord("Ordinateur", "C2", ShotResult.HIT))
    refresh_screen(Grid(), Fleet(), Grid())
    refresh_screen(Grid(), Fleet(), Grid())
    assert capsys.readouterr().out.count("Ordinateur tire en C2 : Touché") == 1
