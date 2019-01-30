import requests
from bs4 import BeautifulSoup
import os

pagesList = []
languages = {}
englishUS = 'EnglishUS'


def getLanguages():
    """Get all Languages from the site and store them in a dictionary with language Code and Name 
    for laster use on the folder names.
    some English US URLs has /en-us/ inside and some dont - so added 2 keys with same languageName
    """
    response = requests.get('https://naturalcycles.com')
    soup = BeautifulSoup(response.text, 'html.parser')
    langList = soup.findAll(class_="lang")
    for lang in langList:
        langCode = lang.findChild()['href'].replace("/","")
        langName = lang.findChild().text.strip().replace(" ","")
        languages[langCode] = langName
    languages['en-us']=englishUS
        

def addLangNameToSplitedPath(splitedPath):
    """Adds language name to splittedPath, if a language does not exist in path adds EnglishUS
    Args:
        splitedPath: array of a splited Url path 
    Returns:
        array with full language Name
    """
    if len(splitedPath) < 2: 
        return splitedPath.append(englishUS)
    if languages.get(splitedPath[1]) != None:
        splitedPath[1] = languages[splitedPath[1]]
    else:
        splitedPath.insert(1,englishUS)
    return splitedPath
        
    
def isLinkValid(link):
    """Checks if a link is valid (and should be scanned for images)
    Args:
        link: the link to be checked
    Returns:
        bool: true if the link is valid, false if its invalid
    """
    if ".com" in link:
        start,end = link.split(".com",1)
        if not(start.endswith("naturalcycles")): #not a naturalCycles URL blabla.com
            return False
    if "www" in link:
        start,end = link.split("www",1)
        if("naturalcycles" not in end): #not a naturalCycles URL www.blabla.es
            return False
    if (len(link) <= 1 or '#' in link or link.startswith("mail") or 'click?' in link): #not a website link
        return False
    if ".naturalcycles.com" in link:
        start,end = link.split("naturalcycles.com",1) #urls with naturalCycles but not on the website: blog.naturalcycles.com
        if(start not in ["http://www.","http://www","http://","https://"]):
           return False
    return True

def isValidImg(imgUrl):
    """checkes if an img link is valid - has an image file type
    Args:
        imgUrl: a url of an image from an img tag
    Returns:
        bool: true if its valid, false if its invalid
    """
    if imgUrl.has_attr('src'):
         if imgUrl['src'].endswith(('.png','.jpg','.jpeg','.gif','.tif')):
             return True
    return False
    
def createDirFromUrl(url):
    """creates a diractory from a url (with required path hirarchy)
    Args:
        url: url of a web page
    Returns:
        string: a folder path created from the site
    """
    splitedUrl = url.replace(".","").split("/")
    splitedUrl.pop(0)
    splitedUrl.pop(0)
    
    if "www." in splitedUrl[0]:
        www,splitedUrl[0] = splitedUrl[0].split("www.",1)
    splitedPathWithLang = addLangNameToSplitedPath(splitedUrl)
    folderPath = ""
    for sitePart in splitedUrl:
        folderPath = os.path.join(folderPath,sitePart).replace("?", "")
    if not os.path.exists(folderPath):
        os.makedirs(folderPath)
    return folderPath

def createImageNameFromUrl(imgUrl):
    """creates an image name from an image url
    Args:
        imgUrl: a url of an image
    Returns:
        string: an image name 
    """  
    splitedurl = imgUrl.split("/")
    return splitedurl[len(splitedurl)-1].replace("?", "")

def downloadImages(url):
    """download all images of a url and its sub pages and store them in the same hirarchy folder
    url:
        url: url of a web page
    """
    
    #preventing scanning a url more than once
    if url in pagesList: 
        return
    pagesList.append(url)

    #get all images from the url
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    img_tags = soup.find_all('img')

    urls = []
    for img in img_tags:
        if isValidImg(img):
            urls.append(img['src'])
    if len(urls) > 0:
        folderPath = createDirFromUrl(url)
        for url in urls:
            if url == "": continue
            imageName = createImageNameFromUrl(url)
            fileName = os.path.join(folderPath, imageName)
            with open(fileName, 'wb') as f:                
                try:
                    print("Downloading .... " + url)
                    response = requests.get(url)
                    f.write(response.content)
                except:
                    print("Could not download:  " + url)

    #get all links of the current webpage and recorsivly download images from them
    linkTags = soup.findAll('a')
    if len(linkTags) > 0:
        for linkTag in linkTags:
            if linkTag.has_attr('href'):
                subPageUrl = linkTag['href']
                if (isLinkValid(subPageUrl)):
                    if subPageUrl[0] == '/': #some Urls are relative - using a full url to srote them in a valid diractory
                        subPageUrl = 'https://naturalcycles.com' + subPageUrl
                    downloadImages(subPageUrl)

# main
getLanguages()
downloadImages('https://naturalcycles.com')
