from bs4 import BeautifulSoup
import requests
import sys
from Site import Progress
from random import randint

class Wattpad:
    
    def requestPage(self,  url):
        headerlist=['Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0','Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/41.0','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36']
        
        header={'user-agent':headerlist[randint(0,len(headerlist)-1)]}
        return requests.get(url, headers=header)
    
    def __init__(self, url):
        self.title=''
        self.author=''
        self.story=''
        self.rawstoryhtml=[]
        self.length=1
        self.summary=''
        self.pbar=None
        self.url=url
        self.chapters=[]
        self.page=None
        #try:
          #  page=requests.get(self.url)
        #except:
          #  print('Error accessing '+self.url+'  Try checking internet connection and url')
            #return None
        
        soup=BeautifulSoup(self.requestPage(self.url).content, 'html.parser')
        #print(soup.prettify())
        self.title=soup.find('h1').get_text()
        self.author=soup.find('span', attrs={'class': 'author h6'}).get_text()[3:]
        self.chapters.append(soup.find('h2').get_text())
        self.summary=soup.find('p', attrs={'class': 'item-description'}).get_text()
        self.rawstoryhtml.append(soup.find('pre'))
        
        print(self.title+'\nby '+ self.author+'\n'+self.summary)
        
        self.length=len(soup.find('ul', attrs={'class':'table-of-contents'}).find_all('li'))
        
        self.pbar=Progress.Progress(self.length)
        self.pbar.Update()
        
        #print(self.rawstoryhtml[0].prettify())
        
        if soup.find('a', attrs={'class': 'next-part-link'}):
            #print(soup.find('a', attrs={'class': 'next-part-link'}).get('href'))
            self.addNextPage(soup.find('a', attrs={'class': 'next-part-link'}).get('href'))
        
        self.pbar.End()
        
        for j in range(0,len(self.rawstoryhtml)):
            tmp=self.rawstoryhtml[j].prettify()[5:]
            tmp=tmp.replace('&amp;apos','\'')
            self.rawstoryhtml[j]=BeautifulSoup(tmp, 'html.parser')
        
        for i in range(0, len(self.rawstoryhtml)):
            self.story=self.story+self.chapters[i]+'\n'
            self.story=self.story+self.rawstoryhtml[i].get_text()
        self.story=self.story.replace('\n', '\n\n')
            
    def addNextPage(self, url):
        soup=BeautifulSoup(self.requestPage(url).content, 'html.parser')
        self.chapters.append('Chapter '+soup.find('h2').get_text())
        #self.rawstoryhtml.append(soup.find('div', attrs={'class':'panel-reading'}))
        self.rawstoryhtml.append(soup.find('pre'))
        self.pbar.Update()
        if soup.find('a', attrs={'class': 'next-part-link'}):
            #print(soup.find('a', attrs={'class': 'next-part-link'}).get('href'))
            self.addNextPage(soup.find('a', attrs={'class': 'next-part-link'}).get('href'))
        
    
    
    
