

# 🧩 A-Maze-Ing — Générateur de labyrinthes avec animation temps réel

A-Maze-Ing est un générateur de labyrinthes en Python basé sur le célèbre
algorithme **DFS Recursive Backtracker**, entièrement visualisé en **temps réel**
dans le terminal.

Le projet suit une architecture **MVC propre**, avec :
- un **MazeGenerator** modulaire,
- un **MazeController** orchestrateur,
- une **TerminalView** capable d'afficher et d'animer la construction du labyrinthe.

---

## ✨ Fonctionnalités principales

- ✔ Génération de labyrinthe par **DFS Backtracking**
- ✔ Animation temps réel : les murs se creusent sous vos yeux
- ✔ Curseur dynamique indiquant la cellule active
- ✔ Rendu ASCII / Unicode propre et lisible
- ✔ Encodage final du labyrinthe au format **hexadécimal**
- ✔ Architecture MVC claire et extensible
- ✔ Support du motif **42** (cellules isolées)
- ✔ Validation de la connectivité du labyrinthe

---

## 🎥 Démonstration (ASCII)

Step: E
●───┐
│   │
└───┘


*(Le curseur vert ● se déplace et creuse les murs en temps réel.)*

---

## 🏗 Architecture du projet

a-maze-ing/
│
├── controller/
│   └── maze_controller.py     # Orchestrateur MVC
│
├── mazegen/
│   └── maze_generator.py      # Générateur DFS (track-based)
│
├── model/
│   ├── maze.py                # Structure du labyrinthe
│   ├── maze_validator.py      # Validation de la connectivité
│   └── config_parser.py       # Lecture du fichier .maze
│
├── view/
│   └── terminal_view.py       # Animation + rendu ASCII
│
└── a_maze_ing.py              # Point d'entrée


---

## ⚙️ Comment ça marche ?

### 1. Le générateur (MazeGenerator)

Le générateur **ne casse pas les murs** directement.  
Il produit une **trace (`track`)** contenant :

- `N`, `E`, `S`, `W` → avancer  
- `BACK` → retour arrière  

Cette trace représente **exactement** le parcours du DFS.

### 2. La vue (TerminalView)

La vue lit `track` et :

- déplace un curseur vert ●
- casse les murs en temps réel (`remove_wall`)
- réaffiche le labyrinthe à chaque étape

### 3. Le contrôleur (MazeController)

Il :

1. charge la config  
2. instancie le générateur  
3. récupère `maze` + `track`  
4. lance l’animation  
5. affiche le labyrinthe final  
6. encode en hex  

---

## 🧪 Fichier de configuration `.maze`

Exemple :

WIDTH=20
HEIGHT=10
SEED=42
PERFECT=True
ALGORITHM=backtracker


---

## 🚀 Lancer le projet

```bash
python3 a_maze_ing.py config.maze

🔢 Encodage hexadécimal
Chaque cellule est encodée selon les bits :

| Mur   | Bit | Valeur  |
|-------|-----|---------|
| Nord  | 1   | 0b0001  |
| Est   | 2   | 0b0010  |
| Sud   | 4   | 0b0100  |
| Ouest | 8   | 0b1000  |

Une cellule fermée = 15  
Une cellule ouverte dépend des murs cassés.

Le labyrinthe final est imprimé en hex :

🛣 Roadmap
[ ] Ajout du PathFinder + affichage du chemin solution

[ ] Mode pas-à-pas (appuyer pour avancer)

[ ] Mode accéléré / instantané

[ ] Support MLX (affichage graphique)

[ ] Export PNG / SVG

[ ] Génération multi-algorithmes (Prim, Kruskal, Aldous-Broder…)
