import requests
from bs4 import BeautifulSoup
import sys
from Site import Common
from time import sleep
import threading
import queue

class Nhentai:

    
    def __init__(self, url):
        self.title=''#
        self.chapters=['']
        #initial author only for title page
        self.author=''#
        #the h1 tag
        self.temp=[]
        self.rawstoryhtml=['']
        self.truestoryhttml=[]
        self.length=1
        self.pbar=None
        self.url=url
        self.images=[] #testing images
        self.hasimages = True
        self.isize=0
        self.duplicate = False
        self.queue = queue.Queue()
        try:
            page=requests.get(self.url)
        except:
            print('Error accessing website: try checking internet connection and url')
        soup=BeautifulSoup(page.content, 'html.parser')
        
        self.title = soup.find('meta', attrs={'itemprop':'name'}).get('content')
        
        if Common.dup:
            if Common.CheckDuplicate(self.title):
                self.duplicate = True
                return None
        
        for au in soup.find_all('div', attrs={'class':'tag-container'}):
            #print('HERE1')
            for au2 in au.find_all('a'):
                #print('HERE2')
                if au2.get('href')[:7]=='/artist':
                    #print('HERE')
                    self.author=au2.get('href')[8:-1]
                    #print(self.author)
        Common.prnt(self.title+' by '+self.author)
        
        self.truestoryhttml.append('')
        self.isize=len(soup.find_all('a', attrs={'rel':'nofollow'}))

        if any(x in ('html', 'HTML', 'txt', 'TXT') for x in Common.opf):
            self.pbar = Common.Progress(self.isize)
        
        for i in soup.find_all('a', attrs={'rel':'nofollow'}):
            self.GetURLS(i.get('href'))
            break
        self.AddPage()
        
        if any(x in ('txt', 'html', 'TXT', 'HTML') for x in Common.opf) and Common.mt:
            for i in range(0, len(self.images)):
                self.queue.get()
        
        if self.pbar is not None:
            self.pbar.End()
            
            
    def GetURLS(self, url):
        try:
            page=requests.get('https://nhentai.net'+url.rstrip(), headers={'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'})
        except:
            print('Error accessing website: try checking internet connection and url')
        soup=BeautifulSoup(page.content, 'html.parser')
        try:
            thisimage=soup.find('section', attrs={'id':'image-container'}).find('img').get('src')
            self.images.append(thisimage)
        except:
            print('Error in: '+url)
            
        for i in range(2, self.isize+1):
            self.images.append(thisimage[:-5]+str(i)+thisimage[-4:])
            
            
                
    def AddPage(self):
        i = 1
        for thisimage in self.images:      
            #print(thisimage)
            if any(x in ('html', 'HTML', 'epub', 'EPUB') for x in Common.opf):
                zeros = '0' * (len(str(self.isize))-1)
                num = i
                if len(zeros)>1 and num > 9:
                    zeros='0'
                elif len(zeros)==1 and num > 9:
                    zeros = ''
                if num > 99:
                    zeros = ''
                self.truestoryhttml[0]=self.truestoryhttml[0]+'<p><img src="'+zeros+str(num)+'.jpg" /></p>\n'
            if any(x in ('html', 'HTML', 'txt', 'TXT') for x in Common.opf):
                if Common.mt:
                    t=threading.Thread(target=Common.imageDL, args=(self.title, thisimage, i, self.isize, self.pbar, self.queue), daemon=False)
                    t.start()
                else:
                    Common.imageDL(self.title, thisimage, i, self.isize, self.pbar)
            i+=1
