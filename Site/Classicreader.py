from bs4 import BeautifulSoup
import requests
import re
import sys
from Site import Common
class Classicreader:
    
    def __init__(self, url):
        self.title=''
        self.author=''
        self.story=''
        self.rawstoryhtml=[]
        self.chapters=[]
        self.pbar=None
        self.url=url
        self.duplicate = False
        page=Common.RequestPage(url)
        if page is None:
            print('Could not complete request for page: ' + url)
            return None
        
        soup=BeautifulSoup(page.content, 'html.parser')
        #grabs important metadata information
        self.title=soup.find('span', attrs={'class': 'book-header'}).get_text()
        
        if Common.dup:
            if Common.CheckDuplicate(self.title):
                self.duplicate = True
                return None
        
        
        Common.prnt(self.title)
        self.author=soup.find('span', attrs={'class': 'by-line'}).contents[1].get_text()
        Common.prnt(self.author)
        
        #looks to see if on table of contents page
        #exception handling could be removed from here
        if soup.find('h2') is None: #and len(soup.find_all('a', attrs={'class':'categories'}))>15:
            #checks to see if single page story
            if len(soup.find_all('a', attrs={'class':'categories'}))==15:
                paragraphs=soup.find_all('p')
                #print(paragraphs)
                text=''
                for p in paragraphs:
                    self.story+=re.sub(r'\n\s*', r'', p.get_text(), flags=re.M)+'\n\n'
                    #print(p.get_text())
                    text+='<p>'+re.sub(r'\n\s*', r'', p.get_text(), flags=re.M)+'</p>\n'
                temp=BeautifulSoup(text, 'html.parser')
                self.chapters.append(self.title)
                self.rawstoryhtml.append(temp)
                return
            try:
                url='https://www.classicreader.com'+soup.find_all('a', attrs={'class':'categories'})[7].get('href')
                page=requests.get(url)
                soup=BeautifulSoup(page.content, 'html.parser')
                Common.prnt('got table of contents page')
            except:
                paragraphs=soup.find_all('p')
                #print(paragraphs)
                text=''
                for p in paragraphs:
                    self.story+=re.sub(r'\n\s*', r'', p.get_text(), flags=re.M)+'\n\n'
                    #print(p.get_text())
                    text+='<p>'+re.sub(r'\n\s*', r'', p.get_text(), flags=re.M)+'</p>\n'
                temp=BeautifulSoup(text, 'html.parser')
                self.chapters.append(self.title)
                self.rawstoryhtml.append(temp)
                return
            
        
        
        
        links=soup.find_all('a', attrs={'class': 'chapter-title'})
        
        self.pbar=Common.Progress(len(links))
        #self.pbar.Update()
        
        for i in links:
            self.AddNextPage('https://www.classicreader.com'+i.get('href'))
            self.chapters.append(i.get_text())
            self.pbar.Update()
        
        self.pbar.End()
        #print(self.chapters)
            
    def AddNextPage(self, link):
        page=Common.RequestPage(link)
        
        if page is None:
            print('Could not complete request for page: ' + url)
            return None
        
        soup=BeautifulSoup(page.content, 'html.parser')
        paragraphs=soup.find_all('p')
        #print(paragraphs)
        text=''
        for p in paragraphs:
            self.story+=re.sub(r'\n\s*', r'', p.get_text(), flags=re.M)+'\n\n'
            #print(p.get_text())
            text+='<p>'+re.sub(r'\n\s*', r'', p.get_text(), flags=re.M)+'</p>\n'
        temp=BeautifulSoup(text, 'html.parser')
        self.rawstoryhtml.append(temp)
