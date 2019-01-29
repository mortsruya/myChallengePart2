import requests
from bs4 import BeautifulSoup
import os

pagesList = []
languages = {}


def getLanguages():
    response = requests.get('https://naturalcycles.com')
    soup = BeautifulSoup(response.text, 'html.parser')
    langList = soup.findAll(class_="lang")
    for lang in langList:
        langCode = lang.findChild()['href'].replace("/","")
        langName = lang.findChild().text.strip()
        languages[langCode] = langName
    languages['en-us']="English US"
        
    

def addLangNameToSplitedPath(splitedPath):
    if len(splitedPath) < 2: 
        return splitedPath.append("English US")
    if languages.get(splitedPath[1]) != None:
        splitedPath[1] = languages[splitedPath[1]]
    else:
        splitedPath.insert(1,"English US")
    return splitedPath
        
    
def isLinkValid(link):
    if ".com" in link:
        start,end = link.split(".com",1)
        if not(start.endswith("naturalcycles")):
            return 0
    if "www" in link:
        start,end = link.split("www",1)
        if("naturalcycles" not in end):
            return 0
    if (len(link) <= 1 or '#' in link or link.startswith("mail") or 'click?' in link):
        return 0
    if ".naturalcycles.com" in link:
        start,end = link.split("naturalcycles.com",1)
        if(start not in ["http://www.","http://www","http://","https://"]):
           return 0
    return 1

def isValidImg(img):
     if img.has_attr('src'):
         if img['src'].endswith(('.png','.jpg','.jpeg','.gif','.tif')):
             return 1
     return 0;    
        

def createDirFromSite(site):
    splitedSite = site.split("/")
    splitedSite.pop(0)
    splitedSite.pop(0)
    
    if "www." in splitedSite[0]:
        www,splitedSite[0] = splitedSite[0].split("www.",1)
    splitedPathWithLang = addLangNameToSplitedPath(splitedSite)
    folderPath = ""
    for sitePart in splitedSite:
        folderPath = os.path.join(folderPath,sitePart).replace("?", "")
    if not os.path.exists(folderPath):
        os.makedirs(folderPath)
    return folderPath

def downloadImages(site):
    if site in pagesList:
        return
    pagesList.append(site)

    response = requests.get(site)
    soup = BeautifulSoup(response.text, 'html.parser')
    img_tags = soup.find_all('img')

    urls = []
    for img in img_tags:
        if isValidImg(img):
            urls.append(img['src'])
    if len(urls) > 0:
        folderPath = createDirFromSite(site)
        for url in urls:
            if url == "": continue
            splitedurl = url.split("/")
            imageName = splitedurl[len(splitedurl)-1].replace("?", "")
            fileName = os.path.join(folderPath, imageName)
            print(fileName)
            with open(fileName, 'wb') as f:                
                try:
                    response = requests.get(url)
                    f.write(response.content)
                except:
                    print("could not download:  " + url)

    linkTags = soup.findAll('a')
    if len(linkTags) > 0:
        for linkTag in linkTags:
            if linkTag.has_attr('href'):
                newPageUrl = linkTag['href']
                if (isLinkValid(newPageUrl)):
                    if newPageUrl[0] == '/':
                        newPageUrl = 'https://naturalcycles.com' + newPageUrl
                    downloadImages(newPageUrl)

# main

getLanguages()
downloadImages('https://naturalcycles.com')
