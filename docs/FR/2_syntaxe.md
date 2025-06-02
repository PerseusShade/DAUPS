# Syntaxe du langage DAUPS

Le langage DAUPS est un langage de pseudocode à structure rigide. Il est conçu pour être facilement lisible et proche du langage naturel, tout en imposant une structure stricte pour garantir une exécution correcte.

## Structure générale

Un programme commence par le mot-clé `Algo`, suivi éventuellement de déclarations de variables. Le bloc principal est délimité par les mots-clés `Begin` et `End`.

```daups-docs
Algo
    Déclaration_de_variables
Begin
    Instructions
End
```

## Commentaires

Les commentaires commencent par `#` et s'étendent jusqu'à la fin de la ligne.

```daups-docs
# Ceci est un commentaire
get x  # Ceci aussi
```

## Types de base

Les types de données suivants sont pris en charge :

- `int` : entier
- `float` : réel
- `bool` : booléen
- `string` : chaîne de caractères
- `array of T` : tableau de type `T`, où `T` est l'un des types précédents (y compris un tableau)

```daups-docs
x : int
texte : string
liste : array of int
matrice : array of array of float
```

## Déclaration de variables

Les variables doivent être déclarées **avant le bloc `Begin`, dans le bloc Algo**. Plusieurs variables du même type peuvent être déclarées ensemble, séparées par des virgules.

```daups-docs
Algo
    identificateur_1 : type_1
    identificateur_2_1, identificateur_2_2 : type_2
Begin
    Instructions
End
```

## Affectation

L'opérateur d'affectation est `<--`.

```daups-docs
Algo
    identificateur_1 : type_1
    identificateur_2_1, identificateur_2_2 : type_2
Begin
    identificateur_1 <-- valeur
    identificateur_2_1 <-- expression
End
```

## Entrées / Sorties

### Lecture (`get`)

```daups-docs
get identificateur
get tableau[indexe]
```

### Affichage (`print`)

```daups-docs
print "Valeur de identificateur :", identificateur, "Saut-de-ligne"
```

> `"Saut-de-ligne"` est une chaîne spéciale pour un retour à la ligne.

## Contrôle de flux

### Conditionnelle (`if`, `else if`, `else`)

```daups-docs
if Condition then
    Instructions
else if Condition then
    Instructions
else
    Instructions
```

Exemple :

```daups-docs
if x > 0 then
    print "Positif"
if x == 0 then
    print "Nul"
else
    print "Négatif"
```

### Boucles

#### Tant que (`while`)

```daups-docs
while (Condition)
    Instructions
```

#### Pour (`for`)

```daups-docs
for i <-- 0 to 10
    print i
```

```daups-docs
for i <-- 10 downto 0
    print i
```

## Fonctions

Une fonction est définie par le mot-clé `function`, suivie du nom, des paramètres typés, du type de retour (s'il y en a un), et d'un bloc `Begin` / `End`.

```daups-docs
function nom(param_1 : type_1, ...) : type_retour
        var : type
    Begin
        Instructions
        return valeur
    End
```

Exemple :

```daups-docs
function maximum(a : int, b : int) : int
    Begin
        if a > b then
            return a
        else
            return b
    End
```

## Tableaux

### Déclaration

```daups-docs
t : array of int
mat : array of array of int
```

### Création

```daups-docs
t <-- create_array(5)
mat <-- create_array(3, 4)
```

### Accès

```daups-docs
t[0] <-- 42
get mat[i][j]
```

## Opérations autorisées par type

| Type     | Opérations possibles                                       |
|----------|------------------------------------------------------------|
| `int`    | `+`, `-`, `*`, `/`, `div`, `mod`, `==`, `<`, `>`...        |
| `float`  | `+`, `-`, `*`, `/`, `==`, `<`, `>`...                      |
| `bool`   | `and`, `or`, `not`, comparaisons                           |
| `string` | `+` (concaténation), comparaisons (`==`, `!=`, etc.)       |
| `array`  | accès par indice `t[i]`, taille `size(t)`, création        |

## Remarques importantes

- La casse est **sensible** (`Variable`, `variable`, `VARIABLE` ne désignent pas la même chose).
- L'indentation est **obligatoire**
- Le mot-clé `End` clôt tous les blocs (programme principal et fonctions).
- Les fonctions peuvent s'appeler entre elles ou être utilisées dans le bloc principal.
- Une erreur est levée si une variable est utilisée sans avoir été déclarée.