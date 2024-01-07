
Discord Bot Project
Introduction

Ce projet de bot Discord est conçu pour interagir avec les utilisateurs, gérer l'historique des commandes et fournir des informations sur les artistes en utilisant une API externe.

Fonctionnalités

Gestion de l'historique des commandes : Le bot conserve l'historique des commandes des utilisateurs, leur permettant de récupérer leur dernière commande, de voir toutes les commandes et d'effacer leur historique des commandes.

Verrouillage de l'historique des commandes (Lorsque l'un des utilisateurs travaille avec l'historique, définir un drapeau pour indiquer qu'il est verrouillé)

Questionnaire : Les utilisateurs sont invités à répondre à un questionnaire lorsqu'ils utilisent la commande correspondante $help questionaire about programming start.

Stocker soit l'historique, soit l'avancement des conversations dans une table de hachage pour que les données soient liées à l'utilisateur. La clé de la table doit donc être une 
donnée représentant l'ID du compte Discord d'un utilisateur et la donnée, pour l'historique.

Informations sur les artistes : Le bot peut récupérer et afficher des informations sur les artistes, y compris des détails sur les membres, la date de création, le premier album, les lieux, les dates de concert et les relations.

Interagissez avec le bot à l'aide de diverses commandes telles que :

$lastcommand : Récupère la dernière commande exécutée par l'utilisateur
$allcommands : Affiche l'historique des commandes de l'utilisateur
$hello : Salue l'utilisateur
$clearhistory : Efface l'historique des commandes de l'utilisateur
$help : Affiche l'aide sur les commandes disponibles
$reset : Réinitialise l'état du bot
$speak about : Lance une conversation sur un sujet donné
$artistinfos : Récupère et affiche des informations sur un artiste musical
Getting Started

Prerequisites: 

Python 3
Discord.py library
Replit database (for command history persistence)
External API for artist information (groupietrackers.herokuapp.com)



Contribution

Les contributions sont les bienvenues ! Si vous avez des améliorations ou de nouvelles fonctionnalités à suggérer, n'hésitez pas à créer un problème ou à soumettre une demande de tirage.



