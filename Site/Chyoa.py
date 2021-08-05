import requests
from bs4 import BeautifulSoup
import re
import sys
from Site import Common
import os
import time
from threading import Lock
import threading
import queue
import copy
import urllib.parse
from datetime import datetime
lock = Lock()
lock2 = Lock()


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
        self.backwards = not Common.chyoa_force_forwards
        self.depth = []
        self.quiet = Common.quiet
        self.epubnextpages = []
        self.nextLinks=[]
        self.partial = False
        self.partialStart=1
        self.ogUrl=self.url
        
        page = Common.RequestPage(url)
        
        if page is None:
            print('Could not complete request for page: ' + url)
            return None
        
        soup=BeautifulSoup(page.content, 'html.parser')
        self.title=soup.find('h3').get_text()
        if self.title=='Log In':
            try:
                self.title=soup.find('h1').get_text()
                self.backwards = False
                
            except:
                pass
        
        
        
        
        
        elif not self.backwards:
            self.partial = True
            
            
        #get update timestamp:
        if (self.backwards or self.partial) and Common.chyoaDupCheck:
            date=soup.find('p', attrs={'class':'dates'}).strong.get_text()
            #date='Jun 18, 2022'
            timestamp=datetime.strptime(date, "%b %d, %Y")
            #print(timestamp)
            if not Common.CheckDuplicateTime(self.title, timestamp):
                Common.prnt('Story not updated: '+self.url, f=True)
                self.duplicate= True
                return None
        
        #check duplicate with timestamp
        
        if Common.dup:
            if Common.CheckDuplicate(self.title):
                self.duplicate = True
                return None
        
        if self.backwards or self.partial:
            self.authors.insert(0,soup.find_all('a')[7].get_text())
        else:
            self.authors.insert(0,soup.find_all('a')[5].get_text())
        self.chapters.insert(0, soup.find('h1').get_text())
        self.summary=soup.find('p', attrs={'class': 'synopsis'}).get_text()
                
        tmp=soup.find('p', attrs={'class': 'meta'}).get_text()
        t=[s for s in tmp.split() if s.isdigit()]
        self.length=int(t[0])
        self.partialStart=self.length
      
        
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
                with lock2:
                    for simg in soup.find('div', attrs={'class': 'chapter-content'}).find_all('img'):
                        
                        imgtemp=simg.get('src')
                        simg['src']='img'+str(len(Common.urlDict[self.ogUrl])+1)+'.jpg'
                        Common.urlDict[self.ogUrl][len(Common.urlDict[self.ogUrl])]=imgtemp
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
        #self.backwards = not Common.chyoa_force_forwards
        for i in soup.find_all('a'):
            if i.text.strip()=='Previous Chapter' and self.backwards:
                newLink=i.get('href')
                while newLink is not None:
                    newLink=self.AddPrevPage(newLink)
                    
                self.backwards = True
                break
            
        #Gets here if it's the intro page that is used
        if not self.backwards:
            self.Pages=[]
            urls=[]
            
            #Starting the Progress Bar
            numChaptersTempTemp = soup.find_all('li')
            for i in numChaptersTempTemp:
                if i.find('i', attrs={'class':'bt-book-open'}):
                    numChapters=i.get_text().split()[0]
                    #Removes commas from stories with over 999 pages
                    numChapters=numChapters.replace(',','')
            try:
                if not Common.mt:
                    if self.partial:
                        print('Downloading an unknown number of pages')
                    else:
                        self.pbar=Common.Progress(int(numChapters))
                        self.pbar.Update()
            except:
                pass
            
            self.q=queue.Queue()
            #print(threading.active_count())

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
                        self.epubtemp[0]+='\n<a href="'+str(j)+'.xhtml">'+link.strip()+'</a>\n<br />'
                    
                    nextLink='\n<a href="#'+str(j)+'">'+'Previous Chapter'+'</a>\n<br />'    
                    self.temp[0]+='\n<a href="#'+str(j)+'">'+link.strip()+'</a>\n<br />' 
                    self.nextLinks.append(nextLink)
                    urls.append(i.get('href'))
                    j+=1
            self.Pages.extend(urls)
            j=1
            self.pageQueue=[]
            for u in urls:
                if Common.mt and not self.partial:
                    chapNum = int(soup.find('p', attrs={'class':'meta'}).get_text().split()[1])
                    firstLinkId=None
                    threading.Thread(target=self.ThreadAdd, args=(u, j, self.renames, self.oldnames, chapNum, '<a href="#Chapter 0">Previous Chapter</a>\n<br />', '\n<a href="'+'Chapter 1'+'.xhtml">'+'Previous Chapter'+'</a>\n<br />', self.nextLinks[j-1], firstLinkId, self.url), daemon=True).start() #TODO 
                else:
                    if Common.mt:
                        Common.prnt('Warning: Cannot multithread partial Chyoa story: '+self.url+'\nUsing default method to download an unknown number of pages')
                    defArgs=(u, j, 1, '<a href="#Chapter 0">Previous Chapter</a>\n<br />', '\n<a href="'+'Chapter 1'+'.xhtml">'+'Previous Chapter'+'</a>\n<br />', self.nextLinks[j-1], None)
                    self.pageQueue.append(defArgs)
                    while self.pageQueue!=[]:
                        #n=self.pageQueue[0]
                        self.AddNextPage(self.pageQueue.pop(0))
                        
                j+=1
            if Common.mt and not self.partial:
                i = int(numChapters)-1
                print("Pages to add: "+str(i))
                while i >0:
                    #print(str(i))
                    try:
                        self.q.get(timeout=30)
                    except queue.Empty as e:
                        print("Unsure if all threads ended")
                        break
                    i-=1
                #print(threading.active_count())
                self.pageQueue=[]
                
                for page in self.Pages:
                    self.pageQueue.append(page)
                    while self.pageQueue!=[]:
                        self.addPage(self.pageQueue.pop(0))
                
                
            
        try:
            self.pbar.End()
        except:
            pass
        if self.backwards:
            
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
            
            
            
        self.story=self.story.replace('\n', Common.lineEnding)
        
        for i in range(0,len(self.truestoryhttml)):
            self.rawstoryhtml[i]=BeautifulSoup(self.truestoryhttml[i], 'html.parser')
            
        
        if any(x in ('epub', 'EPUB') for x in Common.opf):
            for i in range(0, len(self.epubtruestoryhttml)):
                self.epubrawstoryhtml[i]=BeautifulSoup(self.epubtruestoryhttml[i], 'html.parser')
        
        if Common.images and self.hasimages and any(x in ('html', 'HTML') for x in Common.opf):
            for i in range(0,len(Common.urlDict[self.url])):
                Common.prnt("Getting image "+str(i+1) +" at: "+str(Common.urlDict[self.url][i]))
                try:
                    Common.imageDL(self.title, Common.urlDict[self.url][i], i+1, size=len(Common.urlDict[self.url]))
                except urllib.error.HTTPError as FE:
                    continue

                
    def AddPrevPage(self, url):
        page = Common.RequestPage(url)
        
        if page is None:
            print('Could not complete request for page: ' + url)
            return None            

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
                return i.get('href')
        #gets author name if on last/first page I guess
        self.authors[0]=soup.find_all('a')[5].get_text()
        return None
        
    #def AddNextPage(self, (url, depth, prevChapNum, prevLink, epubPrevLink, currLink, prevLinkId)):   
    def AddNextPage(self, args):
        url=args[0]
        depth=args[1]
        prevChapNum=args[2]
        prevLink=args[3]
        epubPrevLink=args[4]
        currLink=args[5]
        prevLinkId=args[6]
        
        page = Common.RequestPage(url)

        if page is None:
            print('Could not complete request for page: ' + url)
            return None

        soup=BeautifulSoup(page.content, 'html.parser')
        self.authors.append(soup.find_all('a')[7].get_text())
        self.chapters.append(soup.find('h1').get_text())
        
        epubCurrLink='\n<a href="'+str(depth)+'.xhtml">'+'Previous Chapter'+'</a>\n<br />'
        
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
        if self.partial:
            Common.prnt(str(depth))
        j = 1
        
        nextpages=[]
        epubnextpages=[]
        nextpagesurl=[]
        nextpagesdepth=[]
        nextLinks=[]
        temp+='<br />'
        epubtemp=temp
        for i in soup.find('div', attrs={'class':'question-content'}).find_all('a'):
            if i.get_text().strip() != 'Add a new chapter':
                
                link = i.get_text()
                #Band aid fix for replaceable text in the next chapter links
                for l in range(len(self.renames)):
                        link=link.replace(self.oldnames[l], self.renames[l])
                nextLink='\n<a href="#'+str(depth)+'.'+str(j)+'">'+'Previous Chapter'+'</a>\n<br />'
                #nextLinks.append(nextLink)
                
                if any(x in ('epub', 'EPUB') for x in Common.opf):
                    epubnextpages.append('\n<a href="'+str(depth)+'.'+str(j)+'.xhtml">'+link.strip()+'</a>\n<br />')
                nextpages.append('\n<a href="#'+str(depth)+'.'+str(j)+'">'+link.strip()+'</a>\n<br />')
                #nextpages.append(prevLink)
                nextpagesurl.append(i)
                nextpagesdepth.append(j)
                j+=1
        temp+=prevLink

        if any(x in ('epub', 'EPUB') for x in Common.opf):
            epubtemp+=epubPrevLink
            for j in epubnextpages:
                epubtemp+=j
            self.epubtemp.append(epubtemp)            
        
        for j in nextpages:
            temp+=j
        self.temp.append(temp)
        try:
            self.pbar.Update()
        except:
            pass
        #Checks if new page was a link backwards and exits if so
        chapNum = int(soup.find('p', attrs={'class':'meta'}).get_text().split()[1])
        
        if prevChapNum >= chapNum:
            return None
        
        #Other check if current page is a link and doesn't continue if so
        prevLinkCheck1=soup.find('span', attrs={'class':'controls-left'})
        prevLinkCheck2=prevLinkCheck1.find_all('a')[0].get('href')
        prevLinkId1=urllib.parse.urlparse(prevLinkCheck2)[2].split('.')[1]
        
        currLinkId=urllib.parse.urlparse(url)[2].split('.')[1]
        if prevLinkId is not None and prevLinkId1 != prevLinkId:
            #print(prevLinkId1)
            #print(prevLinkId)
            

            return
        
        n2=[]
        for i,j in zip(nextpagesurl, nextpagesdepth):
            n2.append([i.get('href'), str(depth)+'.'+str(j), chapNum, currLink, epubCurrLink, nextLink, currLinkId])
        self.pageQueue[0:0]=n2
        
    def ThreadAdd(self, url, depth, renames, oldnames, chapNum, currLink, epubCurrLink, nextLink, currLinkId, ogUrl):
        #if self.Pages.count(url)>1:
        #    print("found issue at" + str(url))
        #    return None
        self.Pages[self.Pages.index(url)]=(Page(url, depth, renames, oldnames, self.q, chapNum, currLink, epubCurrLink, nextLink, currLinkId, ogUrl))
    
    def addPage(self, page):
        #print('adding page: '+str(page))
        #while isinstance(page, str):
            #self.q.get()
        #try:
        self.depth.append(page.depth)
        #except AttributeError as E:
            #print(page)
        self.authors.append(page.author)
        self.chapters.append(page.chapter)
        self.images.extend(page.images)
        if page.hasimages:
            self.hasimages=True
        self.questions.append(page.questions)
        self.epubtemp.extend(page.epubtemp)
        self.temp.extend(page.temp)
        
        if page.children !=[]:
            for zzz in range(0, len(page.children)):
                #try:
                while isinstance(page.children[zzz], str):
                    self.q.get()
            #prepend child pages to the queue
            self.pageQueue[0:0]=page.children


        
class Page:
    
    visitedPages={}
    
    def __init__(self, url, depth, renames, oldnames, q, prevChapNum, prevLink, epubPrevLink, currLink, prevLinkId, ogUrl):
        #if url in self.visitedPages:
        #    self.__dict__ = copy.deepcopy(self.visitedPages[url].__dict__)
        #    return
        #else:
        #    self.visitedPages[url]=self
        self.children=[]
        self.depth=str(depth)
        self.author=''
        self.chapter=''
        self.images=[]
        self.hasimages=False
        self.questions=[]
        self.epubtemp=[]
        self.temp=[]
        self.renames = renames
        self.oldnames = oldnames
        self.q=q
        self.chapNum=0
        self.prevChapNum=prevChapNum
        self.prevLink=prevLink
        self.currLink=currLink
        self.epubPrevLink=epubPrevLink
        self.prevLinkId=prevLinkId
        
        self.ogUrl=ogUrl
        
        self.AddNextPage(url, depth)
        self.q.put(self, False)

    
    def AddNextPage(self, url, depth):
        #print(url)
        page = Common.RequestPage(url)
        
        if page is None:
            print('Could not complete request for page: ' + url)
            return None

        soup=BeautifulSoup(page.content, 'html.parser')
        self.author=(soup.find_all('a')[7].get_text())
        self.chapter=(soup.find('h1').get_text())
        
        
        if Common.images:
            if soup.find('div', attrs={'class': 'chapter-content'}).find('img'):
                with lock2:
                    for simg in soup.find('div', attrs={'class': 'chapter-content'}).find_all('img'):
                        
                        imgtemp=simg.get('src')
                        simg['src']='img'+str(len(Common.urlDict[self.ogUrl])+1)+'.jpg'
                        Common.urlDict[self.ogUrl][len(Common.urlDict[self.ogUrl])]=imgtemp
                self.hasimages = True
        
        temp2 = soup.find('div', attrs={'class': 'chapter-content'})
        #self.depth+=(str(depth))
        Common.prnt(str(depth))
        temp='<div id="'+str(depth)+'">'+str(temp2)     
        self.questions.append(soup.find('header', attrs={'class':"question-header"}).get_text())
        temp+='<h2>'+self.questions[-1]+'</h2>\n</div>'
        #Common.prnt(str(depth))
        j = 1
        
        nextpages=[]
        epubnextpages=[]
        nextpagesurl=[]
        nextpagesdepth=[]
        urls=[]
        temp+='<br />'
        epubtemp=temp
        nextLinks=[]
        #epubNextLinks=[]
        epubCurrLink='\n<a href="'+str(depth)+'.xhtml">'+'Previous Chapter'+'</a>\n<br />'
        
        temp+= self.prevLink
        
        
        for i in soup.find('div', attrs={'class':'question-content'}).find_all('a'):
            if i.get_text().strip() != 'Add a new chapter':
                
                link = i.get_text()
                #Band aid fix for replaceable text in the next chapter links
                for l in range(len(self.renames)):
                        link=link.replace(self.oldnames[l], self.renames[l])
                
                
                if any(x in ('epub', 'EPUB') for x in Common.opf):
                    epubnextpages.append('\n<a href="'+str(depth)+'.'+str(j)+'.xhtml">'+link.strip()+'</a>\n<br />')
                nextLink='\n<a href="#'+str(depth)+'.'+str(j)+'">'+'Previous Chapter'+'</a>\n<br />'
                nextLinks.append(nextLink)
                nextpages.append('\n<a href="#'+str(depth)+'.'+str(j)+'">'+link.strip()+'</a>\n<br />')
                nextpagesurl.append(i)
                urls.append(i.get('href'))
                nextpagesdepth.append(j)
                j+=1
        
        if any(x in ('epub', 'EPUB') for x in Common.opf):
            epubtemp+=self.epubPrevLink
            for j in epubnextpages:
                epubtemp+=j
            self.epubtemp.append(epubtemp)            
        
        
        for j in nextpages:
            temp+=j
        self.temp.append(temp)
        try:
            self.pbar.Update()
        except:
            pass
        
        
        
        #Checks if new page was a link backwards and exits if so
        self.chapNum = int(soup.find('p', attrs={'class':'meta'}).get_text().split()[1])
        
        if self.prevChapNum >= self.chapNum:
            return None
            
        #Other check if current page is a link and doesn't continue if so
        prevLinkCheck1=soup.find('span', attrs={'class':'controls-left'})
        prevLinkCheck2=prevLinkCheck1.find_all('a')[0].get('href')
        prevLinkId=urllib.parse.urlparse(prevLinkCheck2)[2].split('.')[1]
        
        currLinkId=urllib.parse.urlparse(url)[2].split('.')[1]
        if self.prevLinkId is not None and prevLinkId!=self.prevLinkId:
            #print(self.prevLinkId)
            #print(prevLinkId)
            

            return
        
        
        self.children.extend(urls)
        for i in range(0, len(nextpagesurl)): #zip(nextpagesurl, nextpagesdepth):
            threading.Thread(target=self.ThreadAdd, args=(nextpagesurl[i].get('href'), str(depth)+'.'+str(nextpagesdepth[i]), self.renames, self.oldnames, self.currLink, epubCurrLink, nextLinks[i], currLinkId), daemon=True).start()
    def ThreadAdd(self, url, depth, renames, oldnames, currLink, epubCurrLink, nextLink, currLinkId):
        #if self.children.count(url)>1:
            #print("found issue at" + str(url))
        self.children[self.children.index(url)]=(self.__class__(url, depth, renames, oldnames, self.q, self.chapNum, currLink, epubCurrLink, nextLink, currLinkId, self.ogUrl))


