import requests
from bs4 import BeautifulSoup
import re
import sys
from Site import Progress

class Chyoa:

    
    def __init__(self, url):
        self.title=''
        #initial author only for title page
        self.author=''
        #author for each individual chapter
        self.authors=[]
        #the h1 tag
        self.chapters=[]
        self.story=''
        self.temp=[]
        self.rawstoryhtml=[]
        #the question at the end of each page
        self.questions=[]
        self.summary=''
        self.renames=[]
        self.oldnames=[]
        self.truestoryhttml=[]
        self.length=1
        self.pbar=None
        self.url=url
        try:
            page=requests.get(self.url)
        except:
            print('Error accessing website: try checking internet connection and url')
        soup=BeautifulSoup(page.content, 'html.parser')
        self.title=soup.find('h3').get_text()
        self.authors.insert(0,soup.find_all('a')[7].get_text())
        self.chapters.insert(0, soup.find('h1').get_text())
        self.summary=soup.find('p', attrs={'class': 'synopsis'}).get_text()
        
        tmp=soup.find('p', attrs={'class': 'meta'}).get_text()
        t=[s for s in tmp.split() if s.isdigit()]
        self.length=int(t[0])        
      
        
        if soup.find('form', attrs={'id':'immersion-form'}) is not None:
            inputs=soup.find('form', attrs={'id': 'immersion-form'}).find_all('input', attrs={'value':''})
            for i in range(len(inputs)):
                print('Input immersion variable '+str(i)+' '+soup.find('label', attrs={'for':'c'+str(i)}).get_text()+' ('+inputs[i].get('placeholder')+') (Leave blank to keep placeholder name)')
                try:
                    newname=input()
                    self.renames.append(newname)
                except:
                    self.renames.append('')
                self.oldnames.append(inputs[i].get('placeholder'))
                if self.renames[i]=='':
                    self.renames[i]=self.oldnames[i]
        
        
        print(self.title+'\n'+str(self.authors)+'\n'+self.summary)
        #print(self.chapters)
        
        self.pbar=Progress.Progress(self.length)
        
        
        #for name in self.renames:
            
        
        
        
        temp=str(soup.find('div', attrs={'class': 'chapter-content'}))
        self.questions.insert(0, soup.find_all('h2')[1].get_text())
        temp+='<h2>'+self.questions[0]+'</h2>'
        self.temp.insert(0, temp)
        self.pbar.Update()
        #print(self.temp[0])
        #for i in range(len(self.renames)):
            #self.temp[0]=self.temp[0].replace(self.oldnames[i], self.renames[i])
            #self.temp[0]=self.temp[0].replace('\n  <span class="js-immersion-receiver-c'+str(i)+'">\n   '+self.oldnames[i]+'\n  </span>\n  ',' '+self.renames[i])
        #print(self.temp[0])
        #self.rawstoryhtml.insert(0, BeautifulSoup(temp, 'html.parser'))
        #print(self.rawstoryhtml[0])
        
        for i in soup.find_all('a'):
            if i.text.strip()=='Previous Chapter':
                self.AddNextPage(i.get('href'))
                break
        self.pbar.End()
            
        #band-aid fix for names in chapter titles
        #WARNING DO NOT PUT THIS TO PRODUCTION
        for i in range(len(self.chapters)):
            for j in range(len(self.renames)):
                #print(self.chapters[i])
                self.chapters[i]=self.chapters[i].replace(self.oldnames[j], self.renames[j])
                #print(self.chapters[i])
            
        #TODO regular expressions go here                    
            
        for i in range(len(self.temp)):
            self.temp[i]='<h4>by '+self.authors[i]+'</h4>'+self.temp[i]
            self.rawstoryhtml.append(BeautifulSoup(self.temp[i], 'html.parser'))
        #print(self.rawstoryhtml[len(self.rawstoryhtml)-1].get_text())
        self.author=self.authors[0]
        #print(self.chapters)
        
        #replaces replaceable text in the story
        for i in self.rawstoryhtml:
            for j in range(len(self.renames)):
                for k in i.find_all('span', attrs={'class': 'js-immersion-receiver-c'+str(j)}):
                    k.string=self.renames[j]
            self.story+=i.get_text()
            
            self.truestoryhttml.append(str(i))
        
        for i in range(len(self.truestoryhttml)):
            self.truestoryhttml[i]=self.truestoryhttml[i].replace('\n  <span', '<span')
            self.truestoryhttml[i]=self.truestoryhttml[i].replace('<span', ' <span')
            for j in self.renames:
                self.truestoryhttml[i]=self.truestoryhttml[i].replace('\n   '+j+'\n', j)
            self.truestoryhttml[i]=self.truestoryhttml[i].replace('  </span>\n  ', '</span> ')
        #print(self.story)
        #print(self.truestoryhttml[len(self.truestoryhttml)-1])
        #for i in range(len(self.renames)):
            #self.story=self.story.replace('\r   '+self.renames[i]+'\r', self.renames[i])
            #for j in i.contents:
                #try:
                    #self.story+=re.sub(r'\n\s*', r'', j.get_text(), flags=re.M)+'\n'
                #except:
                    #self.story+=re.sub(r'\n\s*', r'', j, flags=re.M)+' '
                    #print('stringobject found')
                #self.story+='\n'
                
    def AddNextPage(self, url):
        try:
            page=requests.get(url)
        except:
            print('Error accessing website: try checking internet connection and url')
        soup=BeautifulSoup(page.content, 'html.parser')
        self.authors.insert(0,soup.find_all('a')[7].get_text())
        self.chapters.insert(0, soup.find('h1').get_text())
        temp=str(soup.find('div', attrs={'class': 'chapter-content'}))
        self.questions.insert(0, soup.find_all('h2')[1].get_text())
        temp+='<h2>'+self.questions[0]+'</h2>'
        self.temp.insert(0, temp)
        #for i in range(len(self.renames)):
            #self.temp[0]=self.temp[0].replace(self.oldnames[i], self.renames[i])
            #self.temp[0]=self.temp[0].replace('\n  <span class="js-immersion-receiver-c'+str(i)+'">\n   '+self.oldnames[i]+'\n  </span>\n  ',' '+self.renames[i])
        #self.rawstoryhtml.insert(0, BeautifulSoup(temp, 'html.parser'))
        self.pbar.Update()
        for i in soup.find_all('a'):
            if i.text.strip()=='Previous Chapter':
                self.AddNextPage(i.get('href'))
                return
        #gets author name if on last/first page I guess
        self.authors[0]=soup.find_all('a')[5].get_text()
        #print(self.authors)
