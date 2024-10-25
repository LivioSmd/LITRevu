# LITRevu
Web application for sharing book reviews and ratings 


## Création d'un Environnement Local

1. **Clonez le dépôt** :
   ```bash
   git clone https://github.com/LivioSmd/LITRevu.git
   cd LITRevu
   python -m venv venv
   
3. **Activez l'environnement virtuel** :
  Sur Windows :
    venv\Scripts\activate
  Sur macOS et Linux :
    source venv/bin/activate
  
4. **Installez les dépendances** :
  pip install -r requirements.txt
  
5. **Migratez la base de données** :
  python manage.py migrate
  
6. **Démarrez le serveur de développement** :
  python manage.py runserver
  
7. **Accéder à l'application** :
  à l'adresse : http://127.0.0.1:8000/


