# Fonctions intégrées du langage DAUPS

Le langage **DAUPS** propose plusieurs **fonctions intégrées** (*builtins*), accessibles directement sans redéfinition. Elles sont automatiquement chargées dans la table des symboles globale à chaque exécution.

## Liste des fonctions intégrées

| Nom               | Description                                                  | Nombre d'arguments     | Exemple d'appel                          |
|-------------------|--------------------------------------------------------------|------------------------|-------------------------------------------|
| `print`           | Affiche un ou plusieurs éléments sans retour à la ligne      | 0 ou plus (illimité)   | `print "Salut", x`                        |
| `get`             | Lit une valeur utilisateur et l'affecte à une variable       | 1 (obligatoire)        | `get x` ou `get tab[i][j]`               |
| `create_array`    | Crée un tableau vide de taille donnée                        | ≥1 (illimité)          | `tab <-- create_array(3, 4)`             |
| `run`             | Exécute un autre fichier `.dps` (ou `.txt`)                  | 1 (chemin string)      | `run "exemple.dps"`                      |
| `SQRT`            | Calcule la racine carrée d'un nombre                         | 1 (numérique)          | `print SQRT(25)`                         |
| `nombreAleatoire` | Génère un entier aléatoire entre deux bornes                 | 2 (numériques)         | `nombreAleatoire(1, 100)`                |
| `size`            | Retourne la taille d'un tableau ou d'une dimension spécifique| 1 ou 2 (tableau, [dim])| `size(tab)` ou `size(tab, 1)`            |
| `Pi`              | Constante mathématique (π)                                   | 0 (aucun)              | `print Pi`                               |

## Détails des fonctions

### 🔹 `print ...`

Affiche des valeurs sans retour automatique à la ligne.

- **Arguments** : 0 ou plus (`string`, `int`, `float`, etc.)
  > `"Saut-de-ligne"` est une chaîne spéciale pour un retour à la ligne.
- **Exemple** :
  ```daups-docs
  print "Bonjour", nom, 42
  ```

### 🔹 `get x`, `get tab[i]`

Demande une entrée utilisateur, typée dynamiquement selon la variable ciblée.

- **Arguments** : 1 (variable cible)
- **Exemple** :
  ```daups-docs
  get age
  get matrice[i][j]
  ```

### 🔹 `create_array(dim1, dim2, ...)`

Crée un tableau vide à une ou plusieurs dimensions.

- **Arguments** : ≥1 (chaque argument représente une dimension, de type `int`)
- **Exemples** :
  ```daups-docs
  tab <-- create_array(5)         # tableau 1D
  mat <-- create_array(4, 3)      # tableau 2D
  cube <-- create_array(2, 2, 2)  # tableau 3D
  ```

### 🔹 `run "chemin"`

Exécute un fichier DAUPS externe.

- **Arguments** : 1 (`string` - chemin vers un fichier `.dps` ou `.txt`)
- **Exemple** :
  ```daups-docs
  run "mon_fichier.dps"
  ```

### 🔹 `SQRT(valeur)`

Renvoie la racine carrée d'un nombre.

- **Arguments** : 1 (`int` ou `float`)
- **Exemple** :
  ```daups-docs
  r <-- SQRT(16)
  ```

### 🔹 `nombreAleatoire(min, max)`

Retourne un entier aléatoire compris dans l'intervalle `[min, max]`.

- **Arguments** : 2 (`int` ou `float`)
- **Exemple** :
  ```daups-docs
  n <-- nombreAleatoire(1, 10)
  ```

### 🔹 `size(tableau[, dimension])`

Renvoie la taille totale d'un tableau ou d'une dimension spécifique.

- **Arguments** : 1 (tableau) ou plus (tableau, dimension_1, ...)
- **Exemples** :
  ```daups-docs
  print size(tab)         # taille totale
  print size(tab, 1)      # taille de la 1ère dimension
  ```

### 🔹 `Pi`

Constante flottante équivalente à `π ≈ 3.141592653589793`.

- **Arguments** : 0
- **Exemple** :
  ```daups-docs
  print Pi
  ```