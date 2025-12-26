# Webspirit TODO List

## PyPi - Pour la partie librairie python

- Utiliser un patron de conception pour les décorateurs avec () et sans (un décorateur en plus à mettre avant la classe/fonction)

- Il faut qu'il soit possible de donner pour CheckType un dictionnaire valeur:annotation soit plusieurs type à tester ou un ... je me comprends

- Création d'une classe Annotation

- Fichier .template pour une arborescence pré-cré de dossiers type comme musiques, vidéo - séries, sagas, film, youtube, ...

- Fichier .csv pour lier les fichiers télécharger avec leurs fichiers .json, qui servira à lier toutes les métadonnées possibles suivant le type du fichier : image, vidéo, sous-titre, ... 

- Dans le dossier tmp, un dossier avec un id unique en fonction de l'horloge comme 09290404-{type:vidéo, image, ...}-{date}

- système d'add-ons pour télécharger des ressources distinctes, avec une classe (patron de conception) déjà créé, par exemple pour Minecraft (icônes des items du jeux, des mods, ...), Windows (images et icônes systèmes dans les fichiers .dll), Pinterest (images et vidéo), Navigateur (icônes des sites web)

- Correctif - importer (depuis l'application automatique si le module FFMPEG n'est pas présent) manuellement FFMPEG

- générer les variables de manière automatique de toute l'arborescence des fichiers, ou seulement dans certain dossier comme downloads

- Ajouts de test pour vérifier que toutes les variables de types chemin existe (peut être tout convertir en StrPath d'office ?), et si ce sont des directories, ajouter sa création si il n'existe pas, comme par exemple pour logs ou user

- Ajouter une recherche automatique du fichier ffmpeg.exe dans le répertoire par défaut

- ajouter une installation avec l'application, et donc si présente l'ajouts du requirements associé en plus de celui global

## Application

- Création automatique d'un .exe avec un workflow github pour lancer l'application depuis windows

- Ajouter une documentation pour l'application
