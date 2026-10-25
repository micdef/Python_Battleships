import random
import pytest
from collections.abc import Callable

import console_ui


@pytest.fixture(autouse=True)
def clean_state():
    """Avant chaque test : hasard reproductible, et aucune annonce laissée en attente par un test précédent."""
    random.seed(1234)
    # noinspection PyProtectedMember
    console_ui._pending_messages.clear()
    yield
    # noinspection PyProtectedMember
    console_ui._pending_messages.clear()


@pytest.fixture
def keyboard() -> Callable[..., Callable[[str], str]]:
    """Fabrique une fausse saisie clavier qui renvoie les réponses données, dans l'ordre."""

    def make(*answers: str) -> Callable[[str], str]:
        replies = iter(answers)
        return lambda prompt: next(replies)

    return make
