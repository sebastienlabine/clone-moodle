#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding=utf8
import getpass
import os
import sys
import zipfile
import time

if sys.version[0] == '2':
    reload(sys)
    sys.setdefaultencoding("utf-8")

# Raise the Import Errors
try:
    import requests
except ImportError:
    raise ImportError('Le package "requests" doit etre installe"')

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
SIGLES_COURS = ['AER', 'ELE', 'GLQ', 'IFT', 'MTH', 'SPL', 'CAP', 'ENE', 'GML', 'IND', 'MEC', 'MTR', 'TPE', 'EST',
                'INF', 'MET', 'PHS', 'SLI', 'SST', 'SSH', 'STI', 'BIO', 'CHE', 'DDI', 'GBM', 'ING', 'SMC', 'CIV', 'GCH', 'LOG']
RESTRICTED_CHARS = ['*', '\\', '/', '?', ':', '|', '<', '>', '\"']
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
           'Accept-Encoding': 'gzip, deflate, br',
           }
SESSION = requests.session()


def verifyString(name):
    for char in RESTRICTED_CHARS:
        if char in name:
            name = name.replace(char, "")
    return name


def createFolder(foldername):
    # Fix for the error : NotADirectoryError : [WinError 267]
    foldername = verifyString(foldername)
    if not os.path.exists(foldername):
        print("Creation du dossier pour le cours " + foldername)
        os.makedirs(foldername)
    else:
        print("Le dossier " + foldername + " existe deja")


def request(url, cookie):
    return SESSION.post(url, headers=HEADERS, cookies=cookie)


def fetchAllClasses(html):
    # Allows us to find every classes
    classesFetch = html.find_all('h4')

    # Cleaning up and keeping only the important classes
    classesFetch = (list(set(classesFetch)))
    linksToPages = []
    for i in range(0, len(classesFetch)):
        if classesFetch[i].a.text[:3] in SIGLES_COURS:
            linksToPages.append(classesFetch[i].a.attrs.get('href'))
    print("Vous avez " + str(len(linksToPages)) + " cours.\n")
    return linksToPages

def savefile(title, documentlink, cookie):
    reqDocument = request(documentlink, cookie)
    filetype = reqDocument.headers['content-type'].split('/')[-1]

    # IF the file is code or a page
    if('charset=utf-8' in filetype.lower()):
        try:
            html = BeautifulSoup(reqDocument.text, "html.parser").find(
                'div', attrs={'class': 'resourceworkaround'})
            html.a.get('href')
        except AttributeError:
            filetypeArray = reqDocument.url.split('.')
            filetype = filetypeArray[len(filetypeArray)-1]

            # Don't download if it's a page
            if('id' in filetype):
                return None
            if('?forcedownload=1' in filetype):
                filetype = filetype.replace('?forcedownload=1', "")
        else:
            link = html.a.get('href')
            reqDocument = request(link, cookie)
            filetype = reqDocument.headers['content-type'].split('/')[-1]

    if('msword' in filetype):
        filetype = 'doc'
    if('vnd.ms-powerpoint' in filetype):
        filetype = 'ppt'
    if("vnd.openxmlformats-officedocument.wordprocessingml.document" in filetype):
        filetype = 'docx'

    if("vnd.openxmlformats-officedocument.presentationml.slideshow" in filetype):
        filetype = 'ppsx'

    if("gzip" in filetype):
        filetype = 'tar.gz'
    
    # Fix for the error : FileNotFoundError: [Errno 2] No such file or directory
    title = verifyString(title)

    # Fix for the error : [Errno 36] File name too long
    if len(title) >= 250:
        title = title[:230]

    with open(title + "." + filetype, "wb") as file:
        file.write(reqDocument.content)


def findAllDocuments(html, cookie):
    documents = html.find_all("td", attrs={"class": "cell c1"})
    for document in documents:
        title = document.a.text[1:]
        documentURL = document.a.get('href')
        if('resource' in documentURL):
            print("Téléchargement du fichier " + title + "...")
            savefile(title, documentURL, cookie)
        if("folder" in documentURL):
            req = request(documentURL, cookie)
            folderHTML = BeautifulSoup(req.text, "html.parser")
            folderName = folderHTML.find("div", {"role": "main"}).h2.text
            print(folderName)
            createFolder(folderName)
            os.chdir(folderName)
            folderId = documentURL.split("=")[1]
            savefile(folderName, "https://moodle.polymtl.ca/mod/folder/download_folder.php?id="+folderId, cookie)
            # Download the file under a zip file
            zip = zipfile.ZipFile(folderName + ".zip")
            zip.extractall()
            zip.close()
            # Delete the zip file
            os.remove(folderName + ".zip")
            os.chdir("..")


def accessResourceURL(classURL, cookie):
    resourceURL = classURL.replace("view","resources")
    req = request(resourceURL, cookie)
    return BeautifulSoup(req.text, "html.parser")

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
        'loginbtn': 'Connexion'
    }
    # Login
    loginRequest = SESSION.post(LOGIN_URL, data=data, headers=HEADERS)
    loginCookie = loginRequest.cookies

    # Redirecting to home page
    # URL that shows all classes
    url = "https://moodle.polymtl.ca/my/index.php?mynumber=-2"
    home = request(url, loginCookie)
    homeHTML = BeautifulSoup(home.text, "html.parser")
    if(homeHTML.title.text == "Tableau de bord"):
        print("Login Succesful")
        # Creating the folder
        createFolder("Polytechnique Montreal")
        os.chdir("Polytechnique Montreal")

        classes = fetchAllClasses(homeHTML)

        # Navigating through each class
        for currentClass in classes:
                req = request(currentClass, loginCookie)
                currentClassHTML = BeautifulSoup(req.text, "html.parser")
                title = currentClassHTML.title.text[8:]
                createFolder(title)
                os.chdir(title)
                resourceHTML = accessResourceURL(currentClass, loginCookie)
                findAllDocuments(resourceHTML, loginCookie)
                os.chdir("..")
    else:
        print("Erreur de connexion : mauvais nom d'utilisateur ou mauvais mot de passe")
        sys.exit()

    endTime = time.time()

    print("Fin de la tache. Duree totale :" +
          "{0:.2f}".format(round(endTime-startTime), 2) + " secondes")

if __name__ == "__main__":
    main()
