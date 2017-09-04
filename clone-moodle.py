import getpass
import os,sys,zipfile,time

# Hide the traceback
sys.tracebacklimit = 0

# Raise the Import Errors
try:
    import requests
except ImportError:
    raise ImportError('Le package "request" doit etre installe"')

try:
    from bs4 import BeautifulSoup
except ImportError:
    raise ImportError('Le package "bs4" doit etre installe"')

# Allow compatibility between Python2 and Python3
try:
    input = raw_input
except NameError:
    pass


# Constants
LOGIN_URL = 'https://moodle.polymtl.ca/login/index.php'
SIGLES_COURS = ['AER','ELE','GLQ','IFT','MTH','SPL','CAP','ENE','GML','IND','MEC','MTR','TPE','EST','INF','MET','PHS','SLI','SST','STI','BIO','CHE','DDI','GBM','ING','SMC','CIV','GCH']
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
SESSION = requests.session()

def createFolder(foldername):
    if not os.path.exists(foldername):
        print("Creation du dossier pour le cours " + foldername)
        os.makedirs(foldername)
    else:
        print("Le dossier " + foldername + " existe deja")
    os.chdir(foldername)

def request(url,cookie):
    return SESSION.post(url,headers=HEADERS, cookies=cookie)

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
        print("Succes lors de la connexion au serveur Moodle...\n")
        print("Vous avez " + str(len(linksToPages)) + " cours.\n")
    return linksToPages

def findRessourceTab(html):
    tabs = html.find("ul",attrs={"class":"unlist"}).find_all("li")

    for tab in tabs:
        if('resources' in tab.a.get('href')):
            linkTab = tab.a.get('href')
        else :
            linkTab = "none"
    return linkTab


def savefile(title,documentlink,cookie):

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
    if('/' in title):
        title = title.replace("/", "")

   
    # Fix for the error : [Errno 36] File name too long
    if len(title) >= 250:
        title = title[:230]

    with open(title + "." + filetype, "wb") as file:
            file.write(reqDocument.content)

def findAllDocuments(html,cookie):
    documents = html.find_all("td", attrs={"class":"c1"})

    for document in documents:
        title = document.a.text[1:]
        linkDocument = document.a.get('href')
        if('resource' in linkDocument):
            print(title)
            savefile(title,linkDocument,cookie)
        # verify if there's a folder    
        else:
            if ('folder' in linkDocument):
                req = request(linkDocument,cookie)
                dossierHTML = BeautifulSoup(req.text,"html.parser")
                title = dossierHTML.find('div',attrs={'role':'main'}).h2.text
                createFolder(title)
                id = dossierHTML.find('input',attrs={'name':'id'}).get('value')
                savefile(title,"https://moodle.polymtl.ca/mod/folder/download_folder.php?id="+id,cookie)
                
                # Download the file under a zip file
                zip = zipfile.ZipFile(title + ".zip")
                zip.extractall()
                zip.close()
                
                # Delete the zip file
                os.remove(title + ".zip")
                os.chdir("..")
            
def main():

    startTime = time.time()
    # User information
    username = input("Veuillez entrer votre nom d'utilisateur\n")
    password = getpass.getpass('Veuillez entrer votre mot de passe \n')


    # Data to send for the login
    data = {
        'username': username,
        'password': password,
        'rememberusername': 1,
        'loginbtn' : 'Connexion'
    }

    # Creating the folder
    createFolder("Polytechnique Montreal")


    # Login
    loginRequest = SESSION.post(LOGIN_URL,data=data, headers=HEADERS)
    loginCookie = loginRequest.cookies

    # Redirecting to home page
    home = request('https://moodle.polymtl.ca/my',loginCookie)
    homeHTML = BeautifulSoup(home.text,"html.parser")
    classes = fetchAllClasses(homeHTML)


    # Navigating through each class
    for thisClass in classes:
        req = request(thisClass,loginCookie)
        thisClassHTML = BeautifulSoup(req.text,"html.parser")

        # Getting the class title
        title = thisClassHTML.title.text[8:]

        # Creating the class folder
        createFolder(title)
    
        # Trying to access the ressource tab
        ressourceLink = findRessourceTab(thisClassHTML)

        # Accessing the ressource page
        if(ressourceLink != "none"):
            req = request(ressourceLink,loginCookie)
        else:
            # Skipping the class if there's no ressource tab
            os.chdir("..")
            continue
        ressourceHTML = BeautifulSoup(req.text,"html.parser")
        
        findAllDocuments(ressourceHTML,loginCookie)
        os.chdir("..")
    os.chdir("..")
    os.chdir("..")
    endTime = time.time()

    print("Fin de la tache. Duree totale :" + "{0:.2f}".format(round(endTime-startTime),2) + " secondes")


if __name__ == "__main__":
    main()
