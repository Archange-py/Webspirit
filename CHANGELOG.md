# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Construction stable de la documentation avec sphinx dans un nouveau répertoire docs/
- Ajout d'un fichier requirement.txt pour les dépendances spécifiques à sphinx
- Ajout d'une documentation claire et efficace dans chaque fichier pour les fonctions et les classes
- Ajout d'un fichier CHANGELOG.md claire et efficace

### Fixed

- Correction du chemin d'accès à docs/build/html pour le déploiement sur GitHub Pages avec le Workflow GitHub dans docs.yml 
- Ajout des ressources manquantes CHANGELOG.md, requirements.txt et du répertoire docs/ dans le fichier MANIFEST.in
- Correction de la présence de deux dossiers log dans le projet

### Changed

- Modification du README.md
- Refactorisation de chaque fichier de la librairie
- Reconfiguration de l'arbre des dossiers et fichiers

### Removed

- Mise en cache de l'application FFmpeg

## [0.0.2] - 2025-09-21

### Fixed

- Ajout de la bibliothèque build dans les dépendances à installer de publish.yml pour la publication sur PyPi avec le Workflow GitHub

## [0.0.1] - 2025-09-21

### Added

- Initialisation du dépôt avec tout les fichiers iconique à GitHub et relatif à une librairie python hébergé sur PyPi
- Mise en place d'un Workflow GitHub pour les tests avec unittest et doctest de manière dynamique, et pour la publication automatique sur PyPi lors du changement de la version dans pyproject.toml
- Ajout de la librairie FFMPEG, dépendance de yt-dlp
- Ajout de Jupiter Notebooks pour les examples des différents fichiers individuel de la librairie
- Mise en place d'un logger efficace avec des couleurs, et une gestion claire des logs dans l'ensemble de la librairie


[unreleased]: https://github.com/Archange-py/Webspirit/compare/v0.0.1...HEAD
[0.0.2]: https://github.com/Archange-py/Webspirit/compare/v0.0.1...v0.0.2
[0.0.1]: https://github.com/Archange-py/Webspirit/releases/tag/v0.0.1