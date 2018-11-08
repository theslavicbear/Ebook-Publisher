import requests
from bs4 import BeautifulSoup
import re
import sys

class Chyoa:
    title=''
    #initial author only for title page
    author=''
    #author for each individual chapter
    authors=[]
    #the h1 tag
    chapters=[]
    story=''
    temp=[]
    rawstoryhtml=[]
    #the question at the end of each page
    questions=[]
    summary=''
    renames=[]
    oldnames=[]
    
    
    def __init__(self, url):
        try:
            page=requests.get(url)
        except:
            print('Error accessing website: try checking internet connection and url')
        soup=BeautifulSoup(page.content, 'html.parser')
        self.title=soup.find('h3').get_text()
        self.authors.insert(0,soup.find_all('a')[7].get_text())
        self.chapters.insert(0, soup.find('h1').get_text())
        self.summary=soup.find('p', attrs={'class': 'synopsis'}).get_text()
        
        if soup.find('form', attrs={'id':'immersion-form'}) is not None:
            inputs=soup.find('form', attrs={'id': 'immersion-form'}).find_all('input', attrs={'value':''})
            for i in range(len(inputs)):
                print('Input immersion variable '+str(i)+' '+soup.find('label', attrs={'for':'c'+str(i)}).get_text()+' ('+inputs[i].get('placeholder')+')')
                self.renames.append(input())
                self.oldnames.append(inputs[i].get('placeholder'))
        
        
        
        #print(self.title+'\n'+str(self.authors)+'\n'+self.summary)
        #print(self.chapters)
        
        
        temp=soup.find('div', attrs={'class': 'chapter-content'}).prettify()
        self.questions.insert(0, soup.find_all('h2')[1].get_text())
        temp+='<h2>'+self.questions[0]+'</h2>'
        self.temp.insert(0, temp)
        for i in range(len(self.renames)):
            self.temp[0]=self.temp[0].replace(self.oldnames[i], self.renames[i])
        #print(self.temp[0])
        #self.rawstoryhtml.insert(0, BeautifulSoup(temp, 'html.parser'))
        #print(self.rawstoryhtml[0])
        
        for i in soup.find_all('a'):
            if i.text.strip()=='Previous Chapter':
                self.AddNextPage(i.get('href'))
                break
            
        #band-aid fix for names in chapter titles
        for i in range(len(self.chapters)):
            for j in range(len(self.renames)):
                #print(self.chapters[i])
                self.chapters[i]=self.chapters[i].replace(self.oldnames[j], self.renames[j])
                #print(self.chapters[i])
            
        #TODO regular expressions go here                    
            
        for i in range(len(self.temp)):
            self.temp[i]='<h4>by '+self.authors[i]+'</h4>'+self.temp[i]
            self.rawstoryhtml.append(BeautifulSoup(self.temp[i], 'html.parser'))
            self.story+=self.rawstoryhtml[i].get_text()
        self.author=self.authors[0]
        #print(self.chapters)
        
        #replaces replaceable text in the story
        for i in self.rawstoryhtml:
            for j in range(len(self.renames)):
                for k in i.find_all('span', attrs={'class': 'js-immersion-receiver-c'+str(j)}):
                    k.string=self.renames[j]
        
        
    def AddNextPage(self, url):
        try:
            page=requests.get(url)
        except:
            print('Error accessing website: try checking internet connection and url')
        soup=BeautifulSoup(page.content, 'html.parser')
        self.authors.insert(0,soup.find_all('a')[7].get_text())
        self.chapters.insert(0, soup.find('h1').get_text())
        temp=soup.find('div', attrs={'class': 'chapter-content'}).prettify()
        self.questions.insert(0, soup.find_all('h2')[1].get_text())
        temp+='<h2>'+self.questions[0]+'</h2>'
        self.temp.insert(0, temp)
        for i in range(len(self.renames)):
            self.temp[0]=self.temp[0].replace(self.oldnames[i], self.renames[i])
        #self.rawstoryhtml.insert(0, BeautifulSoup(temp, 'html.parser'))
        for i in soup.find_all('a'):
            if i.text.strip()=='Previous Chapter':
                self.AddNextPage(i.get('href'))
                return
        #gets author name if on last/first page I guess
        self.authors[0]=soup.find_all('a')[5].get_text()
        #print(self.authors)
