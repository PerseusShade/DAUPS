# Gestion des erreurs dans le langage DAUPS

L'interpréteur DAUPS est conçu pour détecter et signaler les erreurs fréquentes à l'exécution. Grâce à une analyse statique et dynamique, il fournit des messages explicites facilitant le débogage et la compréhension du comportement du code.

## Types d'erreurs détectées

| Type d'erreur                 | Description                                                                 |
|-------------------------------|-----------------------------------------------------------------------------|
| Variable non déclarée         | Utilisation d'une variable absente des déclarations                         |
| Variable non initialisée      | Lecture d'une variable avant affectation                                   |
| Conflit de type               | Affectation ou opération incompatible avec le type attendu                  |
| Appel de fonction inconnu     | Appel d'une fonction non définie ou mal orthographiée                       |
| Mauvais nombre d'arguments    | Appel de fonction avec trop ou pas assez de paramètres                      |
| Accès hors tableau            | Tentative d'accès à un indice inexistant                                    |
| Type non pris en charge       | Usage d'un type inexistant ou mal formé                                     |
| Expression invalide           | Syntaxe incorrecte dans une affectation ou un test conditionnel             |
| Erreur utilisateur (entrée)   | Saisie d'une valeur non conforme au type de la variable                     |
| Mauvaise instruction          | Mot-clé ou structure non reconnue                                           |

## Exemples d'erreurs et messages correspondants

### Variable non déclarée

```daups-docs
Algo
Begin
    x <-- 5  # x n'a pas été déclaré
End
```

```text
RunTime error: Variable 'x' is not declared

    x <-- 5  # x n'a pas été déclaré
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
```

### Conflit de type

```daups-docs
Algo
    x : int
Begin
    x <-- "texte"
End
```

```text
RunTime error: Variable 'x' is of type 'int', but got 'String'

    x <-- "texte"
          ^^^^^^^
```

### Appel de fonction inconnu

```daups-docs
Algo
    resultat : int
Begin
    resultat <-- inconnu(3)
End
```

```text
RunTime error: 'inconnu' is not defined

    resultat <-- inconnu(3)
                 ^^^^^^^^^^
```

### Mauvais nombre d'arguments

```daups-docs
function f(a : int, b : int) : int
    Begin
        return a + b
    End

Algo
Begin
    print f(3)  # il manque un argument
End
```

```text
RunTime error: 1 too few arguments passed into 'f'
Expected 2 arguments, got 1

    print f(3)  # il manque un argument
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
```

### Accès hors tableau

```daups-docs
Algo
    tab : array of int
Begin
    tab <-- create_array(3)
    print tab[5]  # hors bornes
End
```

```text
RunTime error: Index access error (probably out of bounds)

    print tab[5]  # hors bornes
          ^^^^^^^^^^^^^^^^^^^^^
```

## Déclenchement des erreurs

Les erreurs sont déclenchées soit :

- **Lors de l'analyse statique** (déclarations, types)
- **À l'exécution** (accès mémoire, appels dynamiques, saisie utilisateur)

L'interpréteur interrompt l'exécution dès qu'une erreur est détectée, tout en indiquant précisément **la ligne concernée**, **le type d'erreur**, ainsi que **la variable ou la fonction impliquée**.

## Bonnes pratiques pour éviter les erreurs

- Déclarer systématiquement les variables avec leur type avant `Begin`.
- Respecter les types lors des affectations et des appels de fonctions.
- Vérifier la taille des tableaux avant tout accès par indice.
- Lire attentivement les messages d'erreur, conçus pour être explicites.