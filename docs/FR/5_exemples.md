# Exemples DAUPS

## Exemple 1

```daups-docs
Algo
    x : int
Begin
    print "Donner une valeur entiere"
    get x
    x <-- x+1
    print x
End
```

## Exemple 2

```daups-docs
Algo
    x, y : float
Begin
    print "donnez une valeur entiere"
    get x
    y <-- 3*x+1
    print y
End
```

## Exemple 3

```daups-docs
Algo
    x, y, temp : float
Begin
    print "Donner des valeurs numeriques"
    get x
    get y
    temp <-- x
    x <-- y
    y <-- temp
End
```

## Exemple 4

```daups-docs
Algo
    a, b, c, D, x1, x2 : float
Begin
    print "Quel est le parametre a ?"
    get a
    print "Quel est le parametre b ?"
    get b
    print "Quel est le parametre c ?"
    get c
    D <-- (b*b - 4*a*c)
    if (D < 0) then
        print "Delta est negatif et l'equation n'admet aucune racine reelle"
    else if D == 0 then
        print "Delta = 0 et l'equation admet une solution double x = ", -b/(2*a)
    else
        x1 <-- (-b - SQRT(D)) / (2*a)
        x2 <-- (-b + SQRT(D)) / (2*a)
        print "Delta positif, l'equation admet 2 solutions reelles et distinctes", x1, " et ", x2
End
```

## Exemple 5

```daups-docs
Algo
    a, b, c : int
Begin
    print "Saisir un entier"
    get a
    print "Saisir un entier"
    get b
    print "Saisir un entier"
    get c
    if (a==(b+c) or b==(a+c) or c==(a+b)) then
        print "oui"
    else
        print "non"
End
```

## Exemple 6

```daups-docs
Algo
    a, b, c, d, e, f, x, y : int
Begin
    get a
    get b
    get c
    get d
    get e
    get f
    if ((d*b)-(e*a))==0 then
        # les droites ont la même pente
        # les coeff directeurs sont égaux
        # a/b==d/e <=> ae=db
        if b==0 and e==0 then
            # cas de 2 droites verticales
            if (c*d)==(f*a) then
                # 2 droites verticales confondues
                print "Infinite de solutions"
            else
                # les 2 droites verticales sont parallèles
                print "pas de solution"
        else
            if ((b*f)-(e*c))==0 then
                # droite confondues
                print "Infinite de solutions"
            else
                # les droites sont parallèles
                print "Pas de solutions"
    else
        # ((db-ea)!=0)
        x <-- ((b*f)-(e*c))/((d*b)-(e*a))
        if b == 0 then
            # e!=0
            y <-- (f/e)-(d/e)*x
        else
            y <-- (c/b)-(a/b)*x
        print "x=", x
        print "y=", y
End
```

## Exemple 7

```daups-docs
Algo
    n : float
Begin
    print "Saisir un entier"
    get n
    if (n<10) then
        print "Ajourné"
    else
        if n < 12 then
            print "Passable"
        else
            if n<14 then
                print "AB"
            else
                if n<16 then
                    print "B"
                else
                    print "TB"
End
```

## Exemple 8

```daups-docs
Algo
#calcule x^n
    x : float
    n : int
    i : int #compteur
    r : float #variable stockant le résultat
Begin
    print "Quelle est la valeur de x ?"
    get x
    while (x<0)
        print "x ne peut pas etre négatif, entrez une autre valeur !"
        get x
    print "Quelle est la valeur de n ?"
    get n
    while (n<0)
        print "n ne peut pas être négatif, entrez une autre valeur!"
        get n
    i <-- 0
    r <-- 1
    while (i<n)
        r <-- r*x
        i <-- i+1
    print r
End
```

## Exemple 9

```daups-docs
Algo
# somme des impaires < 100
    cpt, r : int
Begin
    cpt <-- 1
    r <-- 0
    while (cpt<= 100)
        if (cpt mod 2) != 0 then
            r <-- r + cpt
        cpt <-- cpt+1
    print r
End
```

## Exemple 10

```daups-docs
Algo
# Est-ce un nombre premier ?
    n, d, somme : int
Begin
    get n
    d <-- 1
    somme <-- 0
    while (d<n)
        if (n mod d) == 0 then
            somme <-- somme + d
        d <-- d+1
    print "La somme des diviseurs est :"
    print somme
    if somme == 1 then
        print "Ce nombre est premier."
End
```

## Exemple 11

```daups-docs
Algo
# Tous les nombres parfaits ≤ n
    n, d, somme : int
Begin
    get n
    while (n > 1)
        # Chercher les diviseurs de ce nombre n
        d <-- 1
        somme <-- 0
        while (d < n)
            if ((n mod d) == 0) then
                # d est un diviseur de n
                somme <-- somme + d
            d <-- d + 1
        if (somme == n) then
            # n est un nombre parfait
            print n
        n <-- n - 1
End

```

## Exemple 12

```daups-docs
Algo
# Tous les multiples de 7 entre i et j
    i, j : int
Begin
    print "Debut : "
    get i
    print "Fin : "
    get j
    while (i<j)
        if ((i mod 7) == 0) then
            print i
            print " est un multiple de 7."
            print "Saut-de-ligne"
        i <-- i+1
End
```

## Exemple 13

```daups-docs
Algo
# Affichage du tableau
    nbLignes : int # numéro de la ligne courante
    i : int # entier à afficher
    nbCol : int # numéro de la colonne courante
Begin
    nbLignes <-- 1
    while (nbLignes <= 4)
        nbCol <-- 1
        i <-- 1
        while (nbCol <= 5)
            print i
            print " "
            i <-- i + nbLignes
            nbCol <-- nbCol + 1
        print "Saut-de-ligne"
        nbLignes <-- nbLignes + 1
End

```

## Exemple 14

```daups-docs
Algo
# Suite croissante ?
    n : int
    i : int # compteur
    p : int # nombre précédemment saisi
    c : int # nombre courant saisi
    b : bool # vrai tant que la suite est triée
Begin
    n <-- 0
    while (n <= 0)
        get n
    get c
    i <-- 1 # On a déjà saisi un entier - reste (n-1)
    b <-- True
    while (i < n)
        p <-- c # on stocke l'entier précédemment saisi
        get c
        if (p > c) then
            # si l'entier est < au précédent
            b <-- False # Valeurs non-ordonnées de manière croissante.
        i <-- i + 1
    if (b == True) then
        print "Les", n, "valeurs sont triées de façon croissante."
    else
        print "Les", n, "valeurs ne sont pas triées."
End

```

## Exemple 15

```daups-docs
Algo
# Somme des pairs == Somme des impairs ?
    n : int
    si : int # sommes des entiers impairs
    sp : int # sommes des entiers pairs
    i : int # compteur
    e : int # entier saisi
Begin
    n <-- 0
    si <-- 0
    sp <-- 0
    while (n <= 0)
        print "Saisir une valeur positive non nulle :"
        get n
    i <-- 0
    while (i < n)
        e <-- 0
        while (e <= 0)
            print "Saisir un entier positif non nul :"
            get e
        if (e mod 2 == 0) then
            sp <-- sp + e
        else
            si <-- si + e
        i <-- i + 1
    if (si == sp) then
        print "La somme des nombres pairs est égale à la somme des nombres impairs."
    else
        print "La somme des nombres pairs n'est pas égale à la somme des nombres impairs."
End

```

## Exemple 16

```daups-docs
function maximum(n1 : float, n2 : float) : float
    Begin
        if (n1 > n2) then
            return n1
        else
            return n2
    End

Algo
    n1, n2 : float
Begin
    print "Saisir deux valeurs"
    get n1
    get n2
    print maximum(n1, n2)
End

```

## Exemple 17

```daups-docs
function cube(x : float) : float
    Begin
        return x ** 3
    End

function volume(r : float) : float
    Begin
        return (4 / 3) * Pi * cube(r)
    End

Algo
    r : float
Begin
    print "Saisir le rayon"
    get r
    print volume(r)
End

```

## Exemple 18

```daups-docs
function tableMulti(base : int, debut : int, fin : int)
        n : float
    Begin
        print "Fragment de la table de multiplication par", base, ": "
        n <-- debut
        while (n <= fin)
            print n, "x", base, "=", n * base
            print "Saut-de-ligne"
            n <-- n + 1
    End

Algo
    b, d, f : int
Begin
    print "Saisir la base, le début et la fin"
    get b
    get d
    get f
    tableMulti(b, d, f)
End
```

## Exemple 19

```daups-docs
function pgcdParDiviseurs(a : int, b : int) : int
        pgcd : int
    Begin
        pgcd <-- b
        while (pgcd > 1)
            if (a mod pgcd == 0 and b mod pgcd == 0) then
                return pgcd
            pgcd <-- pgcd - 1
        return 1
    End

function maximum(a : int, b : int) : int
    Begin
        if (a > b) then
            return a
        else
            return b
    End

function minimum(a : int, b : int) : int
    Begin
        if (a < b) then
            return a
        else
            return b
    End

function pgcdParDifferences(a : int, b : int) : int
        diff : int
    Begin
        diff <-- a - b
        while (diff > 0)
            a <-- maximum(diff, b)
            b <-- minimum(diff, b)
            diff <-- a - b
        return a
    End

function pgcdParEuclide(a : int, b : int) : int
        reste : int
    Begin
        reste <-- a mod b
        while (reste > 0)
            a <-- b
            b <-- reste
            reste <-- a mod b
        return b
    End

Algo
    a, b : int
Begin
    get a
    get b
    print pgcdParDiviseurs(a, b), "Saut-de-ligne"
    print pgcdParDifferences(a, b), "Saut-de-ligne"
    print pgcdParEuclide(a, b)
End

```

## Exemple 20

```daups-docs
Algo
    taille, i, dessus, indice : int
    somme, moyenne, grand : float
    note : array of float
Begin
    get taille
    note <-- create_array(taille)
    somme <-- 0

    for i <-- 0 to taille - 1
        print "Note en position ", i+1, " ?"
        get note[i]
        somme <-- somme + note[i]

    moyenne <-- somme / taille
    print "la moyenne est", moyenne, "Saut-de-ligne"

    dessus <-- 0
    for i <-- 0 to taille - 1
        if note[i] >= moyenne then
            dessus <-- dessus + 1
    print "le nombre de notes au-dessus de la moyenne est", dessus, "Saut-de-ligne"

    grand <-- note[0]
    indice <-- 0
    for i <-- 1 to taille - 1
        if note[i] > grand then
            grand <-- note[i]
            indice <-- i

    print "le nombre maximum est", grand, "Saut-de-ligne"
    print "il est en position", indice + 1, "Saut-de-ligne"
End
```

## Exemple 21

```daups-docs
Algo
    i, long : int
    tab : array of int
Begin
    get long
    tab <-- create_array(long)

    for i <-- 0 to long - 1
        get tab[i]
        if tab[i] >= 0 then
            print tab[i], "Saut-de-ligne"
End
```

## Exemple 22

```daups-docs
Algo
    i, long, long2 : int
    tab, tab2 : array of int
Begin
    get long
    tab <-- create_array(long)
    tab2 <-- create_array(long)
    long2 <-- 0

    for i <-- 0 to long - 1
        print "Élément en position ", i + 1, " ?", "Saut-de-ligne"
        get tab[i]
        if tab[i] >= 0 then
            tab2[long2] <-- tab[i]
            long2 <-- long2 + 1

    print "le nouveau tableau contient ", long2, " éléments positifs", "Saut-de-ligne"
    tab <-- tab2

    for i <-- 0 to long2 - 1
        print tab[i], "Saut-de-ligne"
End
```

## Exemple 23

```daups-docs
Algo
    i, j, long : int
    tab : array of int
Begin
    get long
    tab <-- create_array(long)
    for i <-- 0 to long - 1
        print "Élément en position ", i + 1, " ?"
        get tab[i]

    j <-- 0
    for i <-- 0 to long - 1
        if tab[i] >= 0 then
            tab[j] <-- tab[i]
            j <-- j + 1

    long <-- j
    for i <-- 0 to long - 1
        print tab[i], "Saut-de-ligne"
End
```

## Exemple 24

```daups-docs
function tabAlea(n : int, a : int, b : int) : array of int
    T : array of int
    i : int
Begin
    T <-- create_array(n)
    for i <-- 0 to n - 1
        T[i] <-- nombreAleatoire(a, b)
    return T
End

function tabProduit(T : array of int) : int
    produit, i : int
Begin
    produit <-- 1
    for i <-- 0 to size(T) - 1
        produit <-- produit * T[i]
    return produit
End

Algo
    a, b, n, i, produit : int
    T : array of int
Begin
    print "Saisir les trois valeurs", "Saut-de-ligne"
    get n
    get a
    get b
    T <-- tabAlea(n, a, b)
    produit <-- tabProduit(T)
    for i <-- 0 to n - 1
        print T[i], "Saut-de-ligne"
    print produit, "Saut-de-ligne"
End
```

## Exemple 25

```daups-docs
Algo
    i, j : int
    tab : array of int
Begin
    tab <-- create_array(4, 2)
    for i <-- 0 to 3
        for j <-- 0 to 1
            tab[i][j] <-- 2 * i + j
    for i <-- 0 to 3
        for j <-- 0 to 1
            print tab[i][j], "Saut-de-ligne"
End
```

## Exemple 26

```daups-docs
Algo
    i, j, grand : int
    tab : array of int
Begin
    tab <-- create_array(12, 8)
    for i <-- 0 to 11
        for j <-- 0 to 7
            print "Quel est l'élément de la ligne ", i + 1, " et de la colonne ", j + 1, " ?", "Saut-de-ligne"
            get tab[i][j]

    grand <-- tab[0][0]
    for i <-- 0 to 11
        for j <-- 0 to 7
            if tab[i][j] > grand then
                grand <-- tab[i][j]
    print "le nombre maximum est ", grand, "Saut-de-ligne"
End
```