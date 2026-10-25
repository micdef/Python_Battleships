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

## Lancer le jeu

Aucune dépendance : uniquement la bibliothèque standard de Python.

    python main.py

Testé avec Python 3.15, sous Windows 11 (Terminal Windows avec PowerShell et CMD) et Linux (WSL).
Le terminal doit interpréter les codes ANSI (couleurs et effacement de l'écran) :
l'ancienne console Windows (conhost) ne le fait pas encore, voir la feuille de route.

## Comment jouer
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

- **Modèle et interface séparés** : les classes du jeu (`Cell`, `Grid`, `Ship`, `Fleet`) ne font
  aucune entrée ni sortie ; tout le dialogue console est isolé dans `console_ui`.
- **Polymorphisme** : une classe abstraite `Player`, deux implémentations (`HumanPlayer`,
  `ComputerPlayer`) ; la partie ne sait pas qui est humain.
- **Contrats vérifiés à chaque couche** et opérations « tout ou rien » : un placement refusé
  ne modifie pas la grille.
- **Une seule source de vérité** : « coulé » et « flotte détruite » sont calculés, jamais stockés.
- **Historique immuable** : chaque coup est un enregistrement figé, exposé en lecture seule.

## Feuille de route

### V2
- Couleurs et effacement de l'écran dans l'ancienne console Windows, option sans couleurs
- Interface console sous forme de classe injectée dans la partie (ouvre la voie à d'autres interfaces)
- Tests automatisés (pytest)
- Modes de jeu prédéfinis (taille de grille et flotte)
- Option « bateaux non adjacents »
- Mines (avec leur propre comportement)
- Ordinateur plus malin : il vise autour d'un bateau touché

### V3
- Ordinateur qui apprend de ses parties, à partir de l'historique des coups

## Licence

Ce projet est publié sous [PolyForm Strict 1.0.0](LICENSE) :
utilisation libre à des fins non commerciales ; toute utilisation commerciale,
modification ou redistribution nécessite l'accord préalable de l'auteur.
