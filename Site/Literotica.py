from bs4 import BeautifulSoup
#TODO comments and cleaning up
import requests
from time import sleep
import sys
from Site import Common
class Literotica:    
    def __init__(self, url):
        self.title=''
        self.author=''
        self.story=''
        self.rawstoryhtml=[0]
        self.storyhtml=''
        self.url=url
        self.duplicate = False
        page = Common.RequestPage(url)
        
        if page is None:
            print('Could not complete request for page: ' + url)
            return None
        
        #while page.status_code!=200:
            #print("Error getting page, trying again: status code: "+str(page.status_code))
            #time.sleep(5)
        soup = BeautifulSoup(page.content, 'html.parser')
        titlehtml=soup.find('h1')
        self.title=titlehtml.text.strip()
        
        if Common.dup:
            if Common.CheckDuplicate(self.title):
                self.duplicate = True
                return None
        
        authorhtml=soup.find('span', attrs={'class': 'b-story-user-y x-r22'})
        #print(authorhtml.prettify())
        self.author=authorhtml.text.strip()
        self.rawstoryhtml[0]=soup.find('div', attrs={'class': 'b-story-body-x x-r15'})
        self.story=self.rawstoryhtml[0].text.strip()
        Common.prnt(self.title+' by '+self.author)
        
        if soup.find('a', attrs={'class': 'b-pager-next'}) is not None:
            self.AddNextPage(soup)
            
        for i in self.rawstoryhtml:
            self.storyhtml+=str(i.contents[0].prettify())
        
    #TODO Clean up this mess a bit
    def AddNextPage(self, soup):
        nexturl=soup.find('a', attrs={'class': 'b-pager-next'}).get('href')
        page = Common.RequestPage(nexturl)
        
        if page is None:
            print('Could not complete request for page: ' + url)
            return None
        
        soup=BeautifulSoup(page.content, 'html.parser')
        self.rawstoryhtml.append(soup.find('div', attrs={'class': 'b-story-body-x x-r15'}))
        self.story+=soup.find('div', attrs={'class': 'b-story-body-x x-r15'}).text.strip()
        if soup.find('a', attrs={'class': 'b-pager-next'}) is not None:
            self.AddNextPage(soup)
        
