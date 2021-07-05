from bs4 import BeautifulSoup
#TODO comments and cleaning up
import requests
from time import sleep
import sys
from Site import Common
from random import randint
class Literotica:    

    def requestPage(self,  url):
        headerlist=['Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0','Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/41.0','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36']
        header={'user-agent':headerlist[randint(0,len(headerlist)-1)]}
        return Common.RequestPage(url, headers=header)
        
        
    def __init__(self, url):
        self.title=''
        self.author=''
        self.story=''
        self.rawstoryhtml=[0]
        self.storyhtml=''
        self.url=url
        self.duplicate = False
        #page = Common.RequestPage(url)
        
        '''if page is None:
            print('Could not complete request for page: ' + url)
            return None
        '''
        
        #while page.status_code!=200:
            #print("Error getting page, trying again: status code: "+str(page.status_code))
            #time.sleep(5)
        soup=BeautifulSoup(self.requestPage(self.url).content, 'html.parser')
        #print(soup.prettify())
        titlehtml=soup.find('h1')
        self.title=titlehtml.text.strip()
        #print(self.title)
        
        if Common.dup:
            if Common.CheckDuplicate(self.title):
                self.duplicate = True
                return None
        
        authorhtml=soup.find('a', attrs={'class': 'y_eU'})
        #print(authorhtml.prettify())
        self.author=authorhtml.text.strip()
        #print(self.author)
        self.rawstoryhtml[0]=soup.find('div', attrs={'class': 'aa_ht'})
        self.story=self.rawstoryhtml[0].get_text(separator = Common.lineEnding)
        Common.prnt(self.title+' by '+self.author)
        
        nextLinkSoup=soup.find('a', attrs={'title': 'Next Page'})
        if nextLinkSoup is not None:
            self.AddNextPage(nextLinkSoup.get('href'))
            
        for i in self.rawstoryhtml:
            self.storyhtml+=str(i.contents[0].prettify())
        #print(self.storyhtml)
        
    #TODO Clean up this mess a bit
    def AddNextPage(self, thisLink):
        #print('start next page')
        soup=BeautifulSoup(self.requestPage('https://www.literotica.com'+thisLink).content, 'html.parser')
        
        self.rawstoryhtml.append(soup.find('div', attrs={'class': 'aa_ht'}))
        self.story+=soup.find('div', attrs={'class': 'aa_ht'}).get_text(separator =Common.lineEnding)
        nextLinkSoup=soup.find('a', attrs={'title': 'Next Page'})
        if nextLinkSoup is not None:
            self.AddNextPage(nextLinkSoup.get('href'))
        
