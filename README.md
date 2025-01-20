# Voltalis Integration for Home Assistant

DEPRECATED : 
Voltalis a stoppé l'utilisation de son api [`MyVoltalis`](https://classic.myvoltalis.com/).

Cette intégration pour Home Assistant permet de contrôler et surveiller les appareils connectés via l'API "classic" de [`MyVoltalis`](https://classic.myvoltalis.com/).

## Fonctionnalités

* **Contrôle des Switches** : Allumez ou éteignez les appareils connectés à MyVoltalis directement depuis Home Assistant.
* **Surveillance de la Consommation** : Suivez la consommation d'énergie instantanée et totale de vos appareils.
* **Mise à jour en Temps Réel** : Recevez des mises à jour en temps réel sur l'état et la consommation d'énergie de vos appareils.

## Prérequis

* Compte [`MyVoltalis`](https://myvoltalis.com/) avec des appareils connectés.
* Home Assistant.

## Installation

1. **Télécharger l'Intégration** :
   * Téléchargez le dossier de l'intégration depuis ce repo GitHub.
   * Placez le dossier dans votre dossier `custom_components` de Home Assistant.
2. **Redémarrer Home Assistant** :
   * Redémarrez votre instance Home Assistant pour charger l'intégration.
3. **Configuration via l'Interface Utilisateur** :
   * Allez dans `Configuration` > `Intégrations`.
   * Cliquez sur `Ajouter une intégration` et recherchez `Voltalis`.
   * Entrez vos identifiants MyVoltalis pour connecter l'intégration.

## Configuration

L'intégration est configurée entièrement via l'interface utilisateur de Home Assistant.

## Entités et Services

L'intégration crée les entités et services suivants :

* **Switches** : Chaque appareil connecté à MyVoltalis est ajouté en tant que switch dans Home Assistant.
* **Capteurs** :
  * `voltalis_immediate_consumption` : Affiche la consommation d'énergie instantanée en Watts.
  * `voltalis_total_consumption` : Affiche la consommation d'énergie totale en Watt-heures.

## Dépannage

Consultez les logs de Home Assistant en cas de problème pour obtenir des informations de dépannage.

## Compatibilité avec Versatile Thermostat

Cette intégration est idéale pour être utilisée en conjonction avec l'intégration [`versatile_thermostat`](https://www.home-assistant.io/integrations/versatile_thermostat/) de Home Assistant. En ajoutant des capteurs de température à votre configuration, vous pouvez créer un système de gestion de l'énergie et de la température encore plus robuste et intelligent.

## Contributions

Les contributions à ce projet sont les bienvenues. Veuillez soumettre des bugs et des demandes de fonctionnalités via les issues GitHub.

## Licence

Ce projet est sous licence. Voir le fichier `LICENSE` pour plus de détails.
