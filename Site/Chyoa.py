import requests
from bs4 import BeautifulSoup
import re
import sys
from Site import Common
import os
import time
from threading import Lock

lock = Lock()

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
        self.epubtemp = []
        self.rawstoryhtml=[]
        self.epubrawstoryhtml = []
        #the question at the end of each page
        self.questions=[]
        self.summary=''
        self.renames=[]
        self.oldnames=[]
        self.truestoryhttml=[]
        self.epubtruestoryhttml = []
        self.length=1
        self.pbar=None
        self.url=url
        self.images=[] #testing images
        self.hasimages = False
        self.duplicate = False
        self.backwards = True
        self.depth = []
        self.quiet = Common.quiet
        self.epubnextpages = []
        try:
            page=requests.get(self.url)
        except:
            print('Error accessing website: try checking internet connection and url')
        soup=BeautifulSoup(page.content, 'html.parser')
        self.title=soup.find('h3').get_text()
        if self.title=='Log In':
            try:
                self.title=soup.find('h1').get_text()
                self.backwards = False
                
            except:
                pass
        
        if Common.dup:
            if Common.CheckDuplicate(self.title):
                self.duplicate = True
                return None
        
        if self.backwards:
            self.authors.insert(0,soup.find_all('a')[7].get_text())
        else:
            self.authors.insert(0,soup.find_all('a')[5].get_text())
        self.chapters.insert(0, soup.find('h1').get_text())
        self.summary=soup.find('p', attrs={'class': 'synopsis'}).get_text()
                
        tmp=soup.find('p', attrs={'class': 'meta'}).get_text()
        t=[s for s in tmp.split() if s.isdigit()]
        self.length=int(t[0])        
      
        
        if soup.find('form', attrs={'id':'immersion-form'}) is not None:
            inputs=soup.find('form', attrs={'id': 'immersion-form'}).find_all('input', attrs={'value':''})
            with lock:
                if Common.mt == True:
                    Common.quiet = True
                for i in range(len(inputs)):
                    print(self.title)
                    print('Input immersion variable '+str(i)+' '+soup.find('label', attrs={'for':'c'+str(i)}).get_text()+' ('+inputs[i].get('placeholder')+') (Leave blank to keep placeholder name)')
                    try:
                        newname=input()
                        self.renames.append(newname)
                    except:
                        self.renames.append('')
                    self.oldnames.append(inputs[i].get('placeholder'))
                    if self.renames[i]=='':
                        self.renames[i]=self.oldnames[i]
            if Common.mt == True:
                Common.quiet = self.quiet
                #if q:
                #    sys.stdout=open(os.devnull, 'w')
        #if args.quiet:
        Common.prnt(self.title+'\n'+str(self.authors)+'\n'+self.summary)
        #print(self.chapters)
        if self.backwards:
            self.pbar=Common.Progress(self.length)
        
        
        #for name in self.renames:
            
        
        if Common.images:
            if soup.find('div', attrs={'class': 'chapter-content'}).find('img'):
                for simg in soup.find('div', attrs={'class': 'chapter-content'}).find_all('img'):
                    self.images.append(simg.get('src'))
                    simg['src']='img'+str(len(self.images))+'.jpg'
                    self.hasimages = True
        
        temp=str(soup.find('div', attrs={'class': 'chapter-content'}))
        
        
        #The second H2 tag may not exist if there is no sub title on a story, so we grab the first in such an event
        try:
            self.questions.insert(0, soup.find('header', attrs={'class':"question-header"}).get_text())
        except IndexError as IE:
            self.questions.insert(0, soup.find_all('h2')[0].get_text())
        temp+='<h2>'+self.questions[0]+'</h2>'
        self.temp.insert(0, temp)
        if self.backwards:
            self.pbar.Update()

        
        #if soup.find('a').text.strip()==
        self.backwards = False
        for i in soup.find_all('a'):
            if i.text.strip()=='Previous Chapter':
                self.AddPrevPage(i.get('href'))
                self.backwards = True
                break
            
        #Gets here if it's the intro page that is used
        if not self.backwards:
            j = 1
            self.temp[0]+='\n<br />'
            self.epubtemp=self.temp.copy()
            for i in soup.find('div', attrs={'class':'question-content'}).find_all('a'):
                link= i.get_text()
                if link.strip() != 'Add a new chapter':
                    
                    #Band aid fix for replaceable text in the next chapter links
                    
                    for l in range(len(self.renames)):
                        link=link.replace(self.oldnames[l], self.renames[l])
                    
                    
                    if any(x in ('epub', 'EPUB') for x in Common.opf):
                        self.epubtemp[0]+='\n<a href="'+str(j)+'.xhtml">'+link.strip()+'</a>\n<br />\n'
                    self.temp[0]+='\n<a href="#'+str(j)+'">'+link.strip()+'</a>\n<br />\n'                        
                    self.AddNextPage(i.get('href'), j)
                    j+=1
            
            
            
        if self.backwards:
            self.pbar.End()
            self.epubtemp=self.temp.copy()
            
        #band-aid fix for names in chapter titles
        #WARNING DO NOT PUT THIS TO PRODUCTION
        for i in range(len(self.chapters)):
            for j in range(len(self.renames)):
                #print(self.chapters[i])
                self.chapters[i]=self.chapters[i].replace(self.oldnames[j], self.renames[j])
                #print(self.chapters[i])
            
        #TODO regular expressions go here                    
            
        
        for i in range(len(self.temp)):
            self.temp[i]='\n<h4>by '+self.authors[i]+'</h4>'+self.temp[i]
            if any(x in ('epub', 'EPUB') for x in Common.opf):
                self.epubtemp[i]='\n<h4>by '+self.authors[i]+'</h4>'+self.epubtemp[i]
            self.rawstoryhtml.append(BeautifulSoup(self.temp[i], 'html.parser'))
            if any(x in ('epub', 'EPUB') for x in Common.opf):
                self.epubrawstoryhtml.append(BeautifulSoup(self.epubtemp[i], 'html.parser'))
        #print(self.rawstoryhtml[len(self.rawstoryhtml)-1].get_text())
        self.author=self.authors[0]
        #print(self.chapters)
        
        #replaces replaceable text in the story
        for i in self.rawstoryhtml:
            for j in range(len(self.renames)):
                for k in i.find_all('span', attrs={'class': 'js-immersion-receiver-c'+str(j)}):
                    k.string=self.renames[j]
            self.story+=self.chapters[self.rawstoryhtml.index(i)]+i.get_text()
            
            self.truestoryhttml.append(str(i))
        if any(x in ('epub', 'EPUB') for x in Common.opf): 
            for i in self.epubrawstoryhtml:
                for j in range(len(self.renames)):
                    for l in i.find_all('span', attrs={'class': 'js-immersion-receiver-c'+str(j)}):
                        l.string=self.renames[j]
                self.epubtruestoryhttml.append(str(i))
        
        for i in range(len(self.truestoryhttml)):
            self.truestoryhttml[i]=self.truestoryhttml[i].replace('\n  <span', '<span')
            self.truestoryhttml[i]=self.truestoryhttml[i].replace('<span', ' <span')
            for j in self.renames:
                self.truestoryhttml[i]=self.truestoryhttml[i].replace('\n   '+j+'\n', j)
            self.truestoryhttml[i]=self.truestoryhttml[i].replace('  </span>\n  ', '</span> ')
            
        if any(x in ('epub', 'EPUB') for x in Common.opf):
            for i in range(len(self.epubtruestoryhttml)):
                self.epubtruestoryhttml[i]=self.epubtruestoryhttml[i].replace('\n <span', '<span')
                self.epubtruestoryhttml[i]=self.epubtruestoryhttml[i].replace('<span', ' <span')
                for j in self.renames:
                    self.epubtruestoryhttml[i]=self.epubtruestoryhttml[i].replace('\n   '+j+'\n', j)
                self.epubtruestoryhttml[i]=self.epubtruestoryhttml[i].replace('  </span>\n  ', '</span> ')
            
            
            
        self.story=self.story.replace('\n', '\n\n')
        
        for i in range(0,len(self.truestoryhttml)):
            self.rawstoryhtml[i]=BeautifulSoup(self.truestoryhttml[i], 'html.parser')
            
        
        if any(x in ('epub', 'EPUB') for x in Common.opf):
            for i in range(0, len(self.epubtruestoryhttml)):
                self.epubrawstoryhtml[i]=BeautifulSoup(self.epubtruestoryhttml[i], 'html.parser')
        
        if Common.images and self.hasimages and any(x in ('html', 'HTML') for x in Common.opf):
            for i in range(0,len(self.images)):
                Common.imageDL(self.title, self.images[i], i+1, size=len(self.images))

                
    def AddPrevPage(self, url):
        try:
            page=requests.get(url)
        except:
            print('Error accessing website: try checking internet connection and url')
        soup=BeautifulSoup(page.content, 'html.parser')
        self.authors.insert(0,soup.find_all('a')[7].get_text())
        self.chapters.insert(0, soup.find('h1').get_text())
        
        if Common.images:
            if soup.find('div', attrs={'class': 'chapter-content'}).find('img'):
                for simg in soup.find('div', attrs={'class': 'chapter-content'}).find_all('img'):
                    self.images.append(simg.get('src'))
                    simg['src']='img'+str(len(self.images))+'.jpg'
                    self.hasimages = True
        temp=str(soup.find('div', attrs={'class': 'chapter-content'}))
        self.questions.insert(0, soup.find('header', attrs={'class':"question-header"}).get_text())
        temp+='<h2>'+self.questions[0]+'</h2>'
        self.temp.insert(0, temp)
        
        
        self.pbar.Update()
        for i in soup.find_all('a'):
            if i.text.strip()=='Previous Chapter':
                self.AddPrevPage(i.get('href'))
                return
        #gets author name if on last/first page I guess
        self.authors[0]=soup.find_all('a')[5].get_text()
        
        
    def AddNextPage(self, url, depth):
        try:
            page=requests.get(url)
        except:
            print('Error accessing website: try checking internet connection and url')
        soup=BeautifulSoup(page.content, 'html.parser')
        self.authors.append(soup.find_all('a')[7].get_text())
        self.chapters.append(soup.find('h1').get_text())
        
        if Common.images:
            if soup.find('div', attrs={'class': 'chapter-content'}).find('img'):
                for simg in soup.find('div', attrs={'class': 'chapter-content'}).find_all('img'):
                    self.images.append(simg.get('src'))
                    simg['src']='img'+str(len(self.images))+'.jpg'
                    self.hasimages = True
        
        temp2 = soup.find('div', attrs={'class': 'chapter-content'})
        self.depth.append(str(depth))
        temp='<div id="'+str(depth)+'">'+str(temp2)     
        self.questions.append(soup.find('header', attrs={'class':"question-header"}).get_text())
        temp+='<h2>'+self.questions[-1]+'</h2>\n</div>'
        Common.prnt(str(depth))
        j = 1
        
        nextpages=[]
        epubnextpages=[]
        nextpagesurl=[]
        nextpagesdepth=[]
        temp+='<br />'
        epubtemp=temp
        for i in soup.find('div', attrs={'class':'question-content'}).find_all('a'):
            if i.get_text().strip() != 'Add a new chapter':
                
                link = i.get_text()
                #Band aid fix for replaceable text in the next chapter links
                for l in range(len(self.renames)):
                        link=link.replace(self.oldnames[l], self.renames[l])
                
                
                if any(x in ('epub', 'EPUB') for x in Common.opf):
                    epubnextpages.append('\n<a href="'+str(depth)+'.'+str(j)+'.xhtml">'+link.strip()+'</a>\n<br />')
                nextpages.append('\n<a href="#'+str(depth)+'.'+str(j)+'">'+link.strip()+'</a>\n<br />')
                nextpagesurl.append(i)
                nextpagesdepth.append(j)
                j+=1
        
        if any(x in ('epub', 'EPUB') for x in Common.opf):
            
            for j in epubnextpages:
                epubtemp+=j
            self.epubtemp.append(epubtemp)            
        
        for j in nextpages:
            temp+=j
        self.temp.append(temp)
        for i,j in zip(nextpagesurl, nextpagesdepth):
            self.AddNextPage(i.get('href'), str(depth)+'.'+str(j))


