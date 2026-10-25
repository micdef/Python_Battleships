"""Fixtures partagées par tous les tests.
conftest.py est un nom réservé : pytest charge ce fichier automatiquement, sans import, et rend ses fixtures
disponibles à tous les tests de ce dossier. Une fixture est injectée dans un test par son nom : il suffit que
le test ait un paramètre du même nom (comme l'injection de dépendances, mais par le nom du paramètre).
"""

import random
from collections.abc import Callable

import pytest

from battleships.console_ui import ConsoleUI


@pytest.fixture(autouse=True)
def reproducible_random():
    """Avant chaque test : hasard reproductible, pour que chaque exécution donne le même résultat.

    autouse=True : appliquée à tous les tests sans qu'ils la demandent.
    """
    random.seed(1234)


@pytest.fixture
def console() -> Callable[..., ConsoleUI]:
    """Fabrique une console dont le faux clavier renvoie les réponses données, dans l'ordre.

    C'est une fixture « fabrique » : elle ne renvoie pas une console, mais une fonction qui en crée,
    pour que chaque test choisisse ses propres réponses. Exemple : console("M", "A1 H").
    Chaque appel crée une console neuve : aucune annonce ne passe d'un test à l'autre.
    """

    def make(*answers: str) -> ConsoleUI:
        """Crée une console qui répond answers[0], puis answers[1]... sans tenir compte de la question."""
        replies = iter(answers)  # itérateur : next() lit une réponse à la fois, comme IEnumerator.MoveNext()
        return ConsoleUI(read=lambda prompt: next(replies))

    return make
