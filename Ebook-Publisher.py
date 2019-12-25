#!/usr/bin/env python3
#from bs4 import BeautifulSoup
#import requests
#from time import sleep
import sys
from Site import *
import urllib.parse
#try:
from EpubMaker import epub as epub
    #from ebooklib import epub
#except:
#    print('Warning: No epub filetype support')
import argparse
import os
import threading
import queue
import shutil
from zipfile import ZipFile
from time import sleep

#Master dict of supported sites
sites={
    'www.literotica.com':lambda x:Literotica.Literotica(x),
    'www.fanfiction.net':lambda x:Fanfiction.Fanfiction(x),
    'www.fictionpress.com':lambda x:Fanfiction.Fanfiction(x),
    'www.classicreader.com':lambda x:Classicreader.Classicreader(x),
    'chyoa.com':lambda x:Chyoa.Chyoa(x),
    'www.wattpad.com':lambda x:Wattpad.Wattpad(x),
    'nhentai.net':lambda x:Nhentai.Nhentai(x),
}

#function for making text files
def MakeText(site):
    if type(site) is not Nhentai.Nhentai:
        published=open(wd+site.title+'.txt', 'w')
        published.write(site.title+'\n')
        published.write('by '+site.author+'\n\n')
        published.write(site.story)
        published.close()
    
def MakeHTML(site):
    if (type(site) is Chyoa.Chyoa or type(site) is Nhentai.Nhentai) and site.hasimages:
        published=open(wd+site.title+'/'+site.title+'.html', 'w')
    else:
        published=open(wd+site.title+'.html', 'w')
    published.write('<!DOCTYPE html>\n')
    published.write('<html lang="en">\n')
    published.write('<head>\n<title>'+site.title+' by '+site.author+'</title>\n</head>\n')
    published.write('<h1>'+site.title+'</h1><h3>by '+site.author+'</h3><br /><a href='+site.url+'>'+site.url+'</a>\n')
    for i in range(len(site.rawstoryhtml)):
        if type(site) is Chyoa.Chyoa:
            published.write('<h2>\n'+site.chapters[i]+'\n</h2>\n'+site.truestoryhttml[i])
        elif type(site) is Nhentai.Nhentai:
            published.write(site.truestoryhttml[i])
        elif type(site) is Literotica.Literotica:
            published.write(site.storyhtml)
        else:
            published.write('<h2>\n'+site.chapters[i]+'\n</h2>\n'+site.rawstoryhtml[i].prettify())
    published.write('</html>')
    
    
    published.close()
    
def GetImage(url):
    req = urllib.request.Request(url, headers={'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'})
    return urllib.request.urlopen(req).read()
            
    
#This function is basically all magic from the docs of EpubMaker
def MakeEpub(site):
    book=epub.EpubBook()
    book.set_identifier(site.url)
    titlepage=epub.EpubHtml(title='Title Page', file_name='Title.xhtml', lang='en')
    titlepage.content='<h1>'+site.title+'</h1><h3>by '+site.author+'</h3><br /><a href='+site.url+'</a>'
    #add summary information
    try:
        titlepage.content+='<br /><p>'+site.summary+'</p>'
    except:
        pass
    book.add_item(titlepage)
    book.spine=[titlepage]
    book.set_title(site.title)
    book.set_language('en')
    book.add_author(site.author)
    c=[]

    if type(site) is not Literotica.Literotica and type(site) is not Nhentai.Nhentai:
        toc=[]
        for i in range(len(site.rawstoryhtml)):
            c.append(epub.EpubHtml(title=site.chapters[i], file_name='Chapter '+str(i+1)+'.xhtml', lang='en'))
            if type(site) is Chyoa.Chyoa:
                c[i].content='<h2>\n'+site.chapters[i]+'\n</h2>\n'+site.truestoryhttml[i]
            elif type(site) is Nhentai.Nhentai:
                c[i].content=site.truestoryhttml[i]
            else:
                c[i].content='<h2>\n'+site.chapters[i]+'\n</h2>\n'+site.rawstoryhtml[i].prettify()
            book.add_item(c[i])
            toc.append(c[i])
            
        book.toc=toc
        book.spine.append('nav')
    elif type(site) is Nhentai.Nhentai:
        c.append(epub.EpubHtml(title='none', file_name='Chapter 1.xhtml', lang='en'))
        c[0].content=site.truestoryhttml[0]
        book.add_item(c[0])
        book.spine.append('nav')
    
    #fallback method    
    else:
        c.append(epub.EpubHtml(title=site.title, file_name='Story.xhtml', lang='en'))
        c[0].content=site.storyhtml
        book.add_item(c[0])
        #print(site.title)
    #more ebooklib space magic
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    #book.spine.append('nav')
    for i in c:
        book.spine.append(i)
    epub.write_epub(wd+site.title+'.epub', book)
    
    if type(site) is Chyoa.Chyoa or type(site) is Nhentai.Nhentai:
        if site.hasimages == True:
            with ZipFile(wd+site.title+'.epub', 'a') as myfile:
                i=1
                for url in site.images:
                    zeros = '0' * (len(str(site.isize))-1)
                    if len(zeros)>1 and i > 9:
                        zeros='0'
                    elif len(zeros)==1 and i > 9:
                        zeros = ''
                    if i > 99:
                        zeros = ''
                    with myfile.open('EPUB/'+zeros+str(i)+'.jpg', 'w') as myimg:
                        myimg.write(GetImage(url))
                    i=i+1
    

def MakeClass(url):
    #getting url
    domain=urllib.parse.urlparse(url)[1]
    if domain == 'nhentai.net' and args.t:
        with lock:
            site=sites[domain](url)
    else:
        site=sites[domain](url)
    #site=sites[domain](url)
    if args.t:
        if ftype=='epub':
            #for site in s:
            MakeEpub(site)
        elif ftype=='html':
            MakeHTML(site)
        else:
            #for site in s:
            MakeText(site)
        q.put(site)
    return site

#setting up commandline argument parser
parser=argparse.ArgumentParser()
parser.add_argument('url', help='The URL of the story you want', nargs='?')
parser.add_argument('-o','--output-type', help='The file type you want', choices=['txt', 'epub', 'html'], default='txt')
parser.add_argument('-f','--file', help="Use text file containing a list of URLs instead of single URL", action='store_true')
parser.add_argument('-d','--directory', help="Directory to place output files. Default ./")
parser.add_argument('-q','--quiet', help="Turns off most terminal output", action='store_true')
parser.add_argument('-t', help="Turns on multithreading mode. Recommend also enabling --quiet", action='store_true')
parser.add_argument('-i', '--insert-images', help="Downloads and inserts images for Chyoa stories", action='store_true')
args=parser.parse_args()

if args.quiet:
    Common.quiet=True
    #sys.stdout=open(os.devnull, 'w')
    #print('quiet enabled')
if args.insert_images:
    Common.images=True

stdin=False
if not sys.stdin.isatty():
    args.file=True
    stdin=True
elif not args.url:
    print(args.url)
    parser.error('No input')

if args.directory is None:
    wd='./'
else:
    wd=args.directory
Common.wd = wd

Common.opf = args.output_type

cwd=os.getcwd()
#TODO should use non-relative path
wd=os.path.join(cwd, wd)
if not os.path.exists(wd):
    os.makedirs(wd)

ftype=args.output_type
q=queue.Queue()

if args.file:
    
    #gets the list of urls
    if not stdin:
        f=open(args.url, 'r')
        urls=f.readlines()
        f.close()
    else:
        urls=[]
        stdinput=sys.stdin.read()
        urls=stdinput.split()

    #the multithreaded variant
    if args.t:
        lock = threading.Lock()
        threads = 0
        for i in urls:
            t=threading.Thread(target=MakeClass, args=(i,), daemon=True)
            t.start()
            threads +=1
        #siteThreads = threading.active_count()
        while threads>0:
            s=q.get()
            #threading.active_count()-=1
            #sleep(.01)
            threads -=1
    else:
        for i in urls:
            #site=MakeClass(i)
            if ftype=='epub':
                MakeEpub(MakeClass(i))
            elif ftype=='html':
                MakeHTML(MakeClass(i))
            else:
                MakeText(MakeClass(i))

#the single input version
else:
    lock = threading.Lock() #here for compatability
    site=MakeClass(args.url)
    if site==None:
        sys.exit()
    if ftype=='epub':
        MakeEpub(site)
    elif ftype=='html':
        MakeHTML(site)
    else:
        MakeText(site)
    while threading.active_count()>1:
        sleep(.01)
