# ![](https://share.polymtl.ca/alfresco/guestDownload/direct?path=/Company%20Home/Sites/salle-de-presse---web/documentLibrary/logos/logoImpactMax/polytechnique_promo_cmykPrint.jpg "Logo de Polytechnique Montréal")

# Clone-Moodle
Utilitaire qui vous permet de cloner votre répertoire moodle directement dans un dossier sur votre PC!

# Prérequis
Les modules 'requests' et 'bs4' sont requis pour le fonctionnement du script.

Afin de les installer, exécuter ces deux commandes :

`pip install requests`

`pip install bs4`

# Exécution du script
Pour lancer le script, exécuter cette commande.

`python clone-moodle.py`

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
| **RESTRICTED_CHARS**| Liste des charactères interdit par Windows pour les fichiers/dossiers|
| **HEADERS**         | Headers permettant au script de s'identifier auprès du serveur       |
| **SESSION**         | Session contenant les informations utiles pour les requêtes          |     

```python
LOGIN_URL = 'https://moodle.polymtl.ca/login/index.php'
SIGLES_COURS = ['AER','ELE','GLQ','IFT','MTH','SPL','CAP','ENE','GML','IND','MEC','MTR','TPE','EST','INF','MET','PHS','SLI','SST','SSH','STI','BIO','CHE','DDI','GBM','ING','SMC','CIV','GCH','LOG']
RESTRICTED_CHARS = ['*','\\','/','?',':','|','<','>','\"']
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
SESSION = requests.session()
```
 
 
# Liste des méthodes

## verifyString(name)
Méthode permettant d'analyser un nom possible de fichier/dossier et de le modifier afin qu'il respecte les normes Windows

| Paramètre           | Définition                                                           |
| -------------       |:-------------:                                                       |
| **name**      	  | Nom du fichier ou du dossier à analyser                              |
| **RETURN**      	  | Retourne le nom du fichier conforme	                                 |

```python
def verifyString(name):
    for char in RESTRICTED_CHARS:
        if char in name:
            name = name.replace(char,"")
    return name
```

## createFolder(foldername)
Méthode permettant de créer un dossier s'il n'y en existe aucun du même nom et de naviguer à l'intérieur de celui-ci

| Paramètre           | Définition                                                           |
| -------------       |:-------------:                                                       |
| **foldername**      | Nom du dossier à créer                                               |

```python
def createFolder(foldername):
    # Fix for the error : NotADirectoryError : [WinError 267]
    verifyString(foldername)
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
| **RETURN**          | Retourne la reponse de la requête sous forme d'objet                 |

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

## savefile(title,documentlink,cookie)
Méthode permettant de sauvegarder un fichier depuis une requête

| Paramètre           | Définition                                                           |
| -------------       |:-------------:                                                       |
| **title**           | Nom sous lequel le fichier va être enregistré                        |
| **documentlink**    | Lien vers le document à télécharger                                  |
| **cookie**          | Cookie contenant l'authentification de l'utilisateur                 |

```python
reqDocument = request(documentlink,cookie)
    filetype = reqDocument.headers['content-type'].split('/')[-1]

    if('charset=utf-8' in filetype):
        try:
            html = BeautifulSoup(reqDocument.text,"html.parser").find('div',attrs={'class':'resourceworkaround'})
            html.a.get('href')
        except AttributeError:
            filetypeArray = reqDocument.url.split('.')
            filetype = filetypeArray[len(filetypeArray)-1]
            if('id' in filetype):
                return None
        else :
            link = html.a.get('href')
            reqDocument = request(link,cookie)
            filetype = reqDocument.headers['content-type'].split('/')[-1]

    if('msword' in filetype):
        filetype = 'doc'

    # Fix for the error : FileNotFoundError: [Errno 2] No such file or directory
    verifyString(title)

    # Fix for the error : [Errno 36] File name too long
    if len(title) >= 250:
        title = title[:230]

    with open(title + "." + filetype, "wb") as file:
            file.write(reqDocument.content)
```

