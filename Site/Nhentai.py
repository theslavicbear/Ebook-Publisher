import requests
from bs4 import BeautifulSoup
import sys
from Site import Common
from time import sleep


class Nhentai:

    
    def __init__(self, url):
        self.title=''#
        self.chapters=['']
        #initial author only for title page
        self.author=''#
        #the h1 tag
        self.temp=[]
        self.rawstoryhtml=['']
        self.truestoryhttml=[]
        self.length=1
        self.pbar=None
        self.url=url
        self.images=[] #testing images
        self.hasimages = True
        try:
            page=requests.get(self.url)
        except:
            print('Error accessing website: try checking internet connection and url')
        soup=BeautifulSoup(page.content, 'html.parser')
        
        self.title = soup.find('meta', attrs={'itemprop':'name'}).get('content')
        for au in soup.find_all('a', attrs={'class':'tag'}):
            if au.get('href')[6:]=='/artist':
                self.author=au.get_text()
        
        
        
        self.truestoryhttml.append('')
        
        for i in soup.find_all('a'):
            #print(i.get('rel'))
            if i.get('rel')==['nofollow']:
                #print('new page')
                self.AddPage(i.get('href'))
                sleep(1)
       #print(self.images)
            
        #self.pbar.End()
        #progress bar will be updated on image download for accuracy
    
       
       
                
    def AddPage(self, url):
        #print('https://nhentai.net'+url.rstrip())
        #print('https://nhentai.net/g/53671/1/')
        try:
            page=requests.get('https://nhentai.net'+url.rstrip())
        except:
            print('Error accessing website: try checking internet connection and url')
        soup=BeautifulSoup(page.content, 'html.parser')
        #print(soup.prettify())
        
        #print(soup.find('img').get('src').prettify())
        try:
            self.images.append(soup.find('section', attrs={'id':'image-container'}).find('img').get('src'))
        except:
            print('Error in: '+url)
            print(soup.prettify())
        self.truestoryhttml[0]=self.truestoryhttml[0]+'<p><img src="img'+str(len(self.images))+'.jpg" /></p>'
        
        #if Common.images:
            #if soup.find('div', attrs={'class': 'chapter-content'}).find('img'):
                #for simg in soup.find('div', attrs={'class': 'chapter-content'}).find_all('img'):
                    #self.images.append(simg.get('src'))
                    #simg['src']='img'+str(len(self.images))+'.jpg'
                    #self.hasimages = True
        
