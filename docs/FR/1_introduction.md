# Introduction au langage DAUPS

**DAUPS** est un langage de programmation pédagogique conçu pour favoriser l'apprentissage structuré de l'algorithmique. Il permet d'écrire, tester et exécuter des algorithmes à l'aide d'une syntaxe rigide et typée, proche des standards universitaires.

Développé dans un cadre académique, DAUPS s'adresse principalement aux étudiants en informatique de niveau débutant, afin de leur offrir une transition naturelle entre la théorie algorithmique et la programmation effective.

## Objectifs du langage

DAUPS a été conçu pour :

- Encourager une rédaction rigoureuse des algorithmes,
- Imposer la déclaration explicite des variables avec un **typage statique**,
- Faciliter la compréhension des erreurs via des messages clairs à l'exécution,
- Offrir un environnement de développement complet via une **extension Visual Studio Code dédiée**.

## Caractéristiques principales

- **Typage statique explicite** : chaque variable doit être déclarée avec un type (`int`, `float`, `string`, etc.) avant utilisation.
- **Déclarations obligatoires** : toute variable non déclarée ou mal utilisée entraîne une erreur à l'exécution.
- **Structure stricte** : les programmes commencent par `Algo`, contiennent un bloc `Begin ... End`, et peuvent inclure des fonctions typées.
- **Détection d'erreurs** : l'interpréteur vérifie la cohérence du typage, la portée des variables et la validité des appels de fonction.
- **Écosystème intégré** : l'exécution est assurée par un interpréteur Python, et l'extension VS Code fournit un environnement interactif avec coloration syntaxique, autocomplétion, info-bulles et exécution directe.

## Exécution d'un programme DAUPS

Pour exécuter du code DAUPS :

1. Installez l'extension officielle depuis le marketplace Visual Studio Code : [https://vscode.com/extension](https://vscode.com/extension).
2. Créez un nouveau fichier avec l'extension `.daups`.
3. Rédigez votre algorithme en respectant la syntaxe du langage.
4. Cliquez sur le bouton **▷** dans la barre supérieure pour lancer l'interpréteur.

L'environnement signale automatiquement les erreurs de syntaxe, de typage ou d'exécution, et propose des suggestions contextuelles via l'autocomplétion et les infobulles.

## Ressources complémentaires

- **Interpréteur DAUPS** : moteur d'exécution écrit en Python.
- **Extension VS Code** : améliore la lisibilité et l'interaction avec le code.
- **Documentation en ligne** : régulièrement mise à jour et disponible dans plusieurs langues.

Si vous avez une question, une suggestion ou constatez une erreur dans cette documentation, vous pouvez créer une *issue* ici :
[https://github.com/PerseusShade/DAUPS-docs/issues](https://github.com/PerseusShade/DAUPS-docs/issues)