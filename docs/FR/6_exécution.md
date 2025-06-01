# Déroulement de l'exécution dans le langage DAUPS

L'interpréteur DAUPS exécute un programme en respectant une structure rigide et typée, dans laquelle les blocs, les variables, les fonctions et les instructions sont validés à la fois statiquement et dynamiquement.

Ce chapitre décrit le pipeline complet d'exécution, depuis le chargement d'un fichier `.daups` jusqu'à la production des résultats.

## Étapes principales de l'exécution

1. Chargement du fichier
2. Parsing / Tokenisation
3. Analyse syntaxique
4. Analyse sémantique (types, fonctions, portées…)
5. Construction de la table des symboles
6. Exécution ligne par ligne
7. Gestion des erreurs et affichage des résultats

## 1. Chargement du fichier source

Les fichiers DAUPS sont généralement des fichiers `.daups` ou `.txt` contenant une structure de ce type :

```daups-docs
Algo
    a, b : int
Begin
    get a
    get b
    print a + b
End
```

Le fichier est lu en entier, puis les lignes sont traitées séquentiellement.

## 2. Analyse syntaxique et construction du bloc

L'interpréteur détecte les blocs principaux (`Algo`, `Begin`, `End`) et construit une structure logique du programme, incluant :

- Les instructions simples (`get`, `print`, `x <-- 3`)
- Les blocs de contrôle (`if`, `while`, `for`)
- Les définitions de fonctions
- Les déclarations de variables

## 3. Table des symboles

Les variables déclarées et fonctions définies sont enregistrées dans une table des symboles :

- Globalement pour l'ensemble du programme
- Par portée locale pour chaque fonction

Chaque symbole est associé à :

- un nom
- un type (int, float, etc.)
- une valeur (initiale ou déterminée à l'exécution)
- un contexte (local ou global)

## 4. Exécution des instructions

Le bloc principal est exécuté dans l'ordre d'écriture. Chaque ligne peut correspondre à :

- une affectation
- une lecture utilisateur
- une instruction de contrôle
- un appel de fonction (intégrée ou utilisateur)

Les expressions sont évaluées dynamiquement avec contrôle de type.

## 5. Appel de fonctions

Lorsqu'une fonction est appelée :

- Les arguments sont évalués
- Un contexte local est créé
- Les variables locales sont isolées de l'environnement global
- Une valeur est retournée, si la fonction en prévoit une

Exemple :

```daups-docs
function f(x : int) : int
    Begin
        return x * 2
    End

Algo
    y : int
Begin
    y <-- f(3)
    print y
End
```

## 6. Gestion des erreurs

Toute erreur détectée pendant l'exécution (variable non déclarée, type incompatible, indice hors limites, etc.) interrompt immédiatement le programme, avec un message d'erreur explicite.

## 7. Fin de l'exécution

Lorsque toutes les instructions du bloc principal sont exécutées :

- Les résultats sont affichés dans la console (ou capturés si redirigés)
- Le programme se termine normalement si aucune erreur n'a été levée

## Exemple d'un programme complet exécuté

```daups-docs
Algo
    a, b : int
    resultat : int
Begin
    get a
    get b
    resultat <-- a + b
    print "Résultat :", resultat
End
```

## Résumé

L'exécution dans DAUPS suit une structure stricte mais prévisible :

- Pas de compilation : tout est interprété dynamiquement
- Les types et les portées sont strictement respectés
- Le contrôle des erreurs est systématique
- Les fonctions et tableaux sont gérés dynamiquement