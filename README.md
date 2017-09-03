# clone-moodle
Utilitaire qui vous permet de cloner votre répertoire moodle directement dans un dossier sur votre PC!

# Pré-requis
Les modules 'requests' et 'bs4' sont requis pour le fonctionnement du script.

Afin de les installer, exécuter ces deux commandes :

`pip install requests`

`pip install bs4`

# Exécution du script
Pour lancer le script, éxécuter cette commande.

`python clone-moodle`

> Veuillez entrer votre nom d'utilisateur

Par la suite, entrer votre nom d'utilisateur

> Veuillez entrer votre mot de passe

Finalement, entrer votre mot de passe. Celui-ci ne devrait pas apparaître à l'écran.

# Explication du code source

## Constantes
Voici les constantes pour ce script.

| Constante           | Définition                                                           |
| -------------       |:-------------:                                                       |
| **LOGIN_URL**       | URL de connexion au serveur moodle                                   |
| **SIGLES_COURS**    | Sigles des cours importants à la Polytechnique                       |
| **HEADERS**         | Headers permettant au script de s'identifier auprès du serveur       |
| **SESSION**         | Session contenant les informations utiles pour les requêtes          |     

```python
LOGIN_URL = 'https://moodle.polymtl.ca/login/index.php'
SIGLES_COURS = ['AER','ELE','GLQ','IFT','SPL','IND','PHS','BIO','CIV','ING','CHE','STI','MTH','INF','LOG']
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
SESSION = requests.session()
```
 
 
# Liste des méthodes
## createFolder(foldername)
Méthode permettant de créer un dossier s'il n'y en existe aucun du même nom et de naviguer à l'intérieur de celui-ci

| Paramètre           | Définition                                                           |
| -------------       |:-------------:                                                       |
| **foldername**      | Nom du dossier à créer                                               |

```python
def createFolder(foldername):
    if not os.path.exists(foldername):
        print("Creation du dossier pour le cours " + foldername)
        os.makedirs(foldername)
    else:
        print("Le dossier " + foldername + " existe deja")
    os.chdir(foldername)
```
## request(url,cookie)
Méthode permettant de faire une requête à une URL

| Paramètre           | Définition                                                           |
| -------------       |:-------------:                                                       |
| **url**             | Lien URL                                                             |
| **cookie**          | Cookie contenant l'authentification de l'utilisateur                 |
| **RETURN**          | Retourne la requête "POST" sous forme d'objet                        |

```python
def request(url,cookie):
    return SESSION.post(url,headers=HEADERS, cookies=cookie)
```

## fetchAllClasses(html)
Méthode permettant d'obtenir tous les cours dans Moodle et de les trier afin de seulement garder les cours importants

| Paramètre           | Définition                                                           |
| -------------       |:-------------:                                                       |
| **html**            | Code source HTML de la page                                          |
| **RETURN**          | Retourne un array de liens menant aux pages des cours                |

```python
def fetchAllClasses(html):
    # Allows us to find every classes
    classesFetch = html.find_all('div','course_title')
         
    # Cleaning up and keeping only the important classes
    linksToPages = []
    for i in range(0,len(classesFetch)):
        # Compare it with the array of classes prefix
        if classesFetch[i].text[:3] in SIGLES_COURS:
            linksToPages.append(classesFetch[i].h2.a.attrs.get('href'))
    
    if len(linksToPages) == 0:
        print("Erreur de connexion : mauvais nom d'utilisateur ou mauvais mot de passe")
        sys.exit()
    else:
        print("Succès lors de la connexion au serveur Moodle...\n")
        print("Vous avez " + str(len(linksToPages)) + " cours.\n")
    return linksToPages
```
## findRessourceTab(html):
Méthode permettant de trouver le lien menant aux ressources Moodle

| Paramètre           | Définition                                                           |
| -------------       |:-------------:                                                       |
| **html**            | Code source HTML de la page                                          |
| **RETURN**          | Retourne le lien vers la page ressource du cours                     |

```python
def findRessourceTab(html):
    tabs = html.find("ul",attrs={"class":"unlist"}).find_all("li")

    for tab in tabs:
        if('resources' in tab.a.get('href')):
            linkTab = tab.a.get('href')
        
        else :
            linkTab = "none"
    return linkTab
```


