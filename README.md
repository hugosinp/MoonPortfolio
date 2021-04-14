# :new_moon: MoonPortfolio :new_moon: 

__Subject :__ Asset Manager

__Goal :__ 

User-Friendly Asset Manager which allows users to easily manage their assets whatever the broker is.

A MoonUser can :
* Create a portfolio
* Add new Assets
* Add transactions (Buy, Sell, Convert, Transfer)
* Follow his portfolio's activity
* Manage his expenses

## Functional Analysis :
MoonPortfolio
### Synopsis :
 
Monke has 3 assets on Binance and 2 others on Coinbase. However, Monke would like to manage all of his assets and have a global view on their evolution overtime.

Monke creates a portfolio on MoonPortfolio and inputs all the data about his assets's transactions.
A transaction is defined by the its type (Buy, Sell, Convert, Transfer) and the concerned asset. Then, informations such as buy/sell date, amount will be asked to input the exact transaction.

Now, Monke can check all of his assets activity in one place and consult the Coin Market to make Godlike decisions.


### Use Case Diagram :
![](documentation/UseCase.PNG "Use Case Diagram")

# Technical Analysis

| Functionalities                                 | MoSCoW | Done ? |
| :--------------------                           | ------ | -----: |
| Creation non graphique d'un Reseau              | M | OUI |
| Lancement d'un test                             | M | OUI |
| Recuperation du Resultat                        | M | OUI |
| Ajout de la fonction d'activation d'un Neurone  | M | OUI |
| Retropropagation de l'erreur                    | M | OUI |
| Lancement d'un entrainement complet             | S | OUI |
| Lancement d'un entrainement avec un fichier     | S | OUI |
| Utiliser un Reseau Entrainé                     | S | NON |
| Sauvegarder un Reseau                           | C | OUI |
| Charger un Reseau                               | C | OUI |
| Transformer une image en données d'entrainement | W | NON |
| Ajouter une interface graphique                 | S | OUI |