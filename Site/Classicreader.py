from bs4 import BeautifulSoup
import requests
from time import sleep 
import re
import sys
class Classicreader:
    title=''
    author=''
    story=''
    rawstoryhtml=[]
    chapters=[]
    
    def __init__(self, url):
        try:
            page=requests.get(url)
        except:
            print('Error accessing website: try checking internet connection and url')
            sys.exit()
        soup=BeautifulSoup(page.content, 'html.parser')
        #grabs important metadata information
        self.title=soup.find('span', attrs={'class': 'book-header'}).get_text()
        print(self.title)
        self.author=soup.find('span', attrs={'class': 'by-line'}).contents[1].get_text()
        print(self.author)
        
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
                print('got table of contents page')
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
        
        for i in links:
            self.AddNextPage('https://www.classicreader.com'+i.get('href'))
            self.chapters.append(i.get_text())
        
        #print(self.chapters)
            
    def AddNextPage(self, link):
        page=requests.get(link)
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
