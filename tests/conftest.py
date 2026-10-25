"""Fixtures partagées par tous les tests.

conftest.py est un nom réservé : pytest charge ce fichier automatiquement, sans import, et rend ses fixtures
disponibles à tous les tests de ce dossier. Une fixture est injectée dans un test par son nom : il suffit que
le test ait un paramètre du même nom (comme l'injection de dépendances, mais par le nom du paramètre).
"""

import random
import pytest
from collections.abc import Callable

import console_ui


@pytest.fixture(autouse=True)
def clean_state():
    """Avant chaque test : hasard reproductible, et aucune annonce laissée en attente par un test précédent.

    autouse=True : appliquée à tous les tests sans qu'ils la demandent.
    Le code avant yield s'exécute avant le test, le code après yield s'exécute après, même si le test échoue
    (l'équivalent du constructeur et du Dispose d'une classe de tests xUnit).
    Remise à zéro nécessaire tant que console_ui garde un état global (à supprimer par la refactorisation V2).
    """
    random.seed(1234)
    # noinspection PyProtectedMember
    console_ui._pending_messages.clear()
    yield
    # noinspection PyProtectedMember
    console_ui._pending_messages.clear()


@pytest.fixture
def keyboard() -> Callable[..., Callable[[str], str]]:
    """Fabrique une fausse saisie clavier qui renvoie les réponses données, dans l'ordre.

    C'est une fixture « fabrique » : elle ne renvoie pas un clavier, mais une fonction qui en crée,
    pour que chaque test choisisse ses propres réponses. Exemple : keyboard("M", "A1 H").
    """

    def make(*answers: str) -> Callable[[str], str]:
        """Crée un faux clavier qui répond answers[0], puis answers[1]... sans tenir compte de la question."""
        replies = iter(answers)
        return lambda prompt: next(replies)

    return make
