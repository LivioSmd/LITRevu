# LITRevu
Web application for sharing book reviews and ratings (Pyhton/Django)


## Création d'un Environnement Local

1. Clonez le dépôt :
```
git clone https://github.com/LivioSmd/LITRevu.git
```
2. Créez un nouvel environnement virtuel (venv), depuis le projet:
```
python -m venv env
```
3. Activez l'environnement virtuel :
Sur Windows / Sur Mac
```
source venv/bin/activate
```
4. Installer les packages requis:
```
pip install -r requirements.txt
```
5. Démarrez le serveur de développement :
```
python manage.py runserver
```
7. **Accéder à l'application** :
```
http://127.0.0.1:8000/
```

## Utilisation de l'application :
### L’application permet de :
- S’inscrire ;
- Se connecter.
- Demander des critiques de livres ou d’articles.
- Lire des critiques de livres ou d’articles.
- Publier des critiques de livres ou d’articles.
- Voir, modifier et supprimer ses propres billets et critiques ;
- S'abonner et se désabonner d'autres utilisateurs.

## Information complémentaire :
- Le corps de l'application ce situe dans le dossier App
- Le dossier [migrations] contient l'historique des migrations
- Le dossier [static] contient le dossier de stockage des images ainsi que toutes les files CSS
- Le dossier [templates] contient tous les dossiers des files html

