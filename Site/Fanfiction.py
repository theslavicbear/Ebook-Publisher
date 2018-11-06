from bs4 import BeautifulSoup
import requests
from time import sleep
import re
import urllib.parse
import sys
#TODO clean up and comment
class Fanfiction:
    #simple string for the title
    title=''
    #simple string for the author
    author=''
    #Extra long string containing the text of the story
    story=''
    #each node of the list contains the raw html for one page of the story
    rawstoryhtml=[0]
    #the raw html but prettified and concatenated together
    storyhtml=''
    #array of chapter names
    chapters=[]
    #summary
    summary=''
    url=''
    
    def __init__(self, url):
        self.url=url
        try:
            page=requests.get(self.url)
        except:
            print('Error accessing website: try checking internet connection and url')
            sys.exit()
        soup=BeautifulSoup(page.content, 'html.parser')
        self.rawstoryhtml[0]=soup.find('div', attrs={'id': 'storytext'})
        #self.chapters=soup.find_all('option', attrs={'selected':''})
        
        #Fucking magic that collects the chapter titles
        #probably doesn't work for all stories
        #seems to work for all stories, adds extra chapter title to end, oh well
        try:
            for child in soup.find(attrs={'id': 'chap_select'}).descendants:
                if child.string is None:
                    continue
                else:
                    self.chapters.append(child.string)
            #we end up with an extra chapter at the end of the file, so the band-aid fix is to delete the last node
            del self.chapters[len(self.chapters)-1]
        except:
            print('Chapter name couldn\'t be grabbed')
            self.chapters.append(soup.find('b', attrs={'class': 'xcontrast_txt'}).text.strip())
            
            
        '''So here's the deal. fanfiction.net doesn't close any of the <option> tags that contain the chapter names, so BeautifulSoup closes them all 
            at the end. This means that each option is the child of the option above it. so good luck extracting the name of each chapter individually
            There's also two (2) chapter selection fields on each web page, which makes the output look worse than it really is, since we're only ever
            going to use the first one we won't have to worry about it
            '''
        #print("Chapters:")
        #print(self.chapters)
        self.summary=soup.find_all('div', attrs={'class': 'xcontrast_txt'})[0].text.strip()
        self.author=soup.find_all('a', attrs={'class': 'xcontrast_txt'})[2].text.strip()
        self.title=soup.find('b', attrs={'class': 'xcontrast_txt'}).text.strip()
        print(self.title+'\nby '+self.author+'\n'+self.summary)
        
        #exception handling to avoid errors on single page stories
        try:
            if soup.find('button', attrs={'type': 'BUTTON'}).text.strip()=='< Prev':
                print("Non-first page entered. Ebook-Publisher will only add subsequent pages and chapter titles will be wrong")
            for i in soup.find_all('button', attrs={'type': 'BUTTON'}):
                if i.text.strip()=='Next >':
                    self.AddNextPage(soup)
                    break
        except:
            print("excepting")
            pass
        
        for i in self.rawstoryhtml:
            self.storyhtml+=i.prettify()
        #print(self.storyhtml)
        self.story=self.storyhtml
        self.story=BeautifulSoup(self.story, 'lxml').text
        self.story=re.sub(r'\n\s*\n', r'\n\n', self.story, flags=re.M)
        #print(self.chapters)
        
    def AddNextPage(self, soup):
        for i in soup.find_all('button'):
            if i.text.strip()=='Next >':
                rawnexturl=i.get('onclick')
                if urllib.parse.urlparse(self.url)[1]=='www.fanfiction.net':
                    nexturl='https://www.fanfiction.net'+rawnexturl[15:-1]
                else:
                    nexturl='https://www.fictionpress.com'+rawnexturl[15:-1]
                #print(nexturl)
                try:
                    page=requests.get(nexturl)
                except:
                    print('Error accessing website: try checking internet connection and url')
                    sys.exit()
                soup=BeautifulSoup(page.content, 'html.parser')
                self.rawstoryhtml.append(soup.find('div', attrs={'id': 'storytext'}))
                self.AddNextPage(soup)
                break
            
            
