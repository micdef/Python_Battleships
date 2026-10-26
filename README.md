# Battleships

Bataille navale jouable en console, écrite en Python.

Avec ce projet, j'apprends la programmation orientée objet en Python. Je viens du monde
.NET et C# : le paradigme reste le même, mais Python demande une autre façon de le comprendre.

J'aime les jeux de société et j'ai envie de les faire découvrir à mon fils sur ordinateur :
la bataille navale m'a semblé une bonne mise en bouche.

## Fonctionnalités

- 1.0 - Partie contre l'ordinateur ; le premier tireur est tiré au sort
- 1.0 - Placement de la flotte automatique ou manuel
- 1.0 - Écran rafraîchi à chaque tour : vos bateaux (une couleur par bateau) et vos tirs côte à côte,
  avec en dessous les derniers coups joués
- 1.0 - Annonces « À l'eau », « Touché », « Coulé » (avec le nom du bateau coulé)
- 1.0 - Historique complet de la partie affiché à la fin
- 1.0 - Flottes configurables dans le code (flotte classique par défaut)
- 1.1 - Mode spectateur : regarder une partie entre deux ordinateurs
- 2.0 - Bateau nommé dès qu'il est touché, comme le veut le règlement

## Lancer le jeu

Aucune dépendance : uniquement la bibliothèque standard de Python.

    python main.py

Testé avec Python 3.15, sous Windows 11 (Terminal Windows avec PowerShell et CMD) et Linux (WSL).
Le terminal doit interpréter les codes ANSI (couleurs et effacement de l'écran) :
l'ancienne console Windows (conhost) ne le fait pas encore, voir la feuille de route.

## Comment jouer

- **Menu** : `1` pour jouer contre l'ordinateur, `2` pour regarder une partie entre deux ordinateurs
  (vous choisissez alors la pause entre deux tirs, de 0 à 5 secondes).
- **Placement** : `A` pour automatique, `M` pour manuel. En manuel, donnez la case de départ
  puis le sens : `B7 H` place le bateau vers la droite, `B7 V` vers le bas.
- **Tir** : donnez une coordonnée, par exemple `B7`.
- **Quitter** : `Ctrl+C`.

| Symbole | Signification |
|---|---|
| `~` | eau |
| `B` | votre bateau (une couleur par bateau) |
| `X` | touché |
| `o` | tir dans l'eau |
| `.` | case adverse pas encore visée |

## Conception

- **Architecture hexagonale** : le domaine (`battleships/domain`, les règles et les objets du jeu) ne dépend
  de rien ; l'application (`battleships/application`, la partie et ses contrats) ne dépend que du domaine ;
  les clients (`battleships/clients`, aujourd'hui la console) se branchent dessus. Un test vérifie ces dépendances.
- **Modèle et interface séparés** : les classes du jeu (`Cell`, `Grid`, `Ship`, `Fleet`) ne font
  aucune entrée ni sortie.
- **Interface injectée** : la partie ne connaît qu'un contrat, `GameView`. La console (`ConsoleUI`)
  déclare le respecter et est donnée à la partie par `main.py` ; une autre interface pourra la remplacer
  sans modifier la partie.
- **Polymorphisme** : une classe abstraite `Player`, deux implémentations (`HumanPlayer`,
  `ComputerPlayer`) ; la partie ne sait pas qui est humain.
- **Contrats vérifiés à chaque couche** et opérations « tout ou rien » : un placement refusé
  ne modifie pas la grille.
- **Une seule source de vérité** : « coulé » et « flotte détruite » sont calculés, jamais stockés.
- **Historique immuable** : chaque coup est un enregistrement figé, exposé en lecture seule.

## Développement

Outils de développement (tests et qualité du code), dans un environnement virtuel :

    python -m pip install -r requirements-dev.txt

Avant chaque commit :

    python -m ruff check --fix
    python -m ruff format
    python -m pytest

- **pytest** : plus de 120 tests, dont des tests de régression pour chaque bug corrigé.
- **Ruff** : style PEP 8, ordre des imports et pièges courants (lignes de 120 caractères).
- **Contrat de documentation** : un test échoue si un module, une classe ou une fonction n'a pas de docstring.

## Feuille de route

Le jeu suit les règles d'origine de la bataille navale ; chaque version les conserve.

### V2 (en cours) : architecture et version graphique
- [x] Tests automatisés (pytest)
- [x] Qualité du code vérifiée par Ruff, et contrat de documentation
- [x] Code du jeu regroupé dans un package
- [x] Interface injectée dans la partie (contrat `GameView`)
- [x] Module de règles : toutes les règles du jeu réunies en un seul endroit
- [x] Architecture hexagonale : domaine, application et clients séparés
- [ ] Partie pilotable tour par tour
- [ ] Textes centralisés et erreurs typées : le modèle ne contient plus aucun texte d'affichage
- [ ] Version graphique (pygame), au choix avec la version console

### V2.x : versions mineures
- Ordinateur plus malin, avec trois niveaux de difficulté : facile (au hasard), moyen (vise autour d'un bateau touché) et difficile (déduit le sens du bateau et le suit)
- Couleurs et effacement de l'écran dans l'ancienne console Windows, option sans couleurs
- Traduction anglaise

### V3 : client web
- Jouer à deux depuis un navigateur, en réseau local uniquement (piste : FastAPI et WebSockets)

### V4 : base de données et authentification
- Parties et joueurs enregistrés, connexion des joueurs
- Ouverture du jeu en ligne vers l'extérieur, seulement une fois l'authentification en place

### V5 : intelligence artificielle
- Ordinateur qui apprend des parties enregistrées : niveau de difficulté « expert »

## Licence

Ce projet est publié sous [PolyForm Strict 1.0.0](LICENSE) :
utilisation libre à des fins non commerciales ; toute utilisation commerciale,
modification ou redistribution nécessite l'accord préalable de l'auteur.
