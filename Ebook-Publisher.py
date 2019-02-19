#!/usr/bin/env python3
#from bs4 import BeautifulSoup
#import requests
#from time import sleep
import sys
from Site import *
import urllib.parse
try:
    from ebooklib import epub
except:
    print('Warning: No epub filetype support')
import argparse
import os
import threading
import queue


#Master array of supported sites
#TODO convert this to a dictionary
# sites=['www.literotica.com', 'www.fanfiction.net', 'www.fictionpress.com','www.classicreader.com','chyoa.com', 'www.wattpad.com']
sites={
    'www.literotica.com':lambda x:Literotica.Literotica(x),
    'www.fanfiction.net':lambda x:Fanfiction.Fanfiction(x),
    'www.fictionpress.com':lambda x:Fanfiction.Fanfiction(x),
    'www.classicreader.com':lambda x:Classicreader.Classicreader(x),
    'chyoa.com':lambda x:Chyoa.Chyoa(x),
    'www.wattpad.com':lambda x:Wattpad.Wattpad(x),
}

#function for making text files
def MakeText(site):
    published=open(wd+site.title+'.txt', 'w')
    published.write(site.title+'\n')
    published.write('by '+site.author+'\n\n')
    published.write(site.story)
    published.close()
    
#This function is basically all space magic from the docs of ebooklib
def MakeEpub(site):
    book=epub.EpubBook()
    book.set_identifier(site.url)
    titlepage=epub.EpubHtml(title='Title Page', file_name='Title.xhtml', lang='en')
    titlepage.content='<h1>'+site.title+'</h1><h3>by '+site.author+'</h3><br /><a href=\'url\'>'+site.url+'<a>'
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

    if type(site) is not Literotica.Literotica:
        toc=()
        for i in range(len(site.rawstoryhtml)):
            c.append(epub.EpubHtml(title=site.chapters[i], file_name='Chapter '+str(i+1)+'.xhtml', lang='en'))
            if type(site) is Chyoa.Chyoa:
                c[i].content='<h2>\n'+site.chapters[i]+'\n</h2>\n'+site.truestoryhttml[i]
            else:
                c[i].content='<h2>\n'+site.chapters[i]+'\n</h2>\n'+site.rawstoryhtml[i].prettify()
            book.add_item(c[i])
            toc=toc+(c[i],)
        book.toc=toc
        book.spine.append('nav')
    
    #fallback method
    else:
        c.append(epub.EpubHtml(title=site.title, file_name='Story.xhtml', lang='en'))
        c[0].content=site.storyhtml
        book.add_item(c[0])
    #more ebooklib space magic
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    #book.spine.append('nav')
    for i in c:
        book.spine.append(i)
    epub.write_epub(wd+site.title+'.epub', book, {})
    

def MakeClass(url):
    #getting url
    domain=urllib.parse.urlparse(url)[1]
    site=sites[domain](url)
    # if sites[0]==domain:
    #     site=Literotica.Literotica(url)
    # elif sites[1]==domain:
    #     site=Fanfiction.Fanfiction(url)
    # elif sites[2]==domain:
    #     site=Fanfiction.Fanfiction(url)
    # elif sites[3]==domain:
    #     site=Classicreader.Classicreader(url)
    # elif sites[4]==domain:
    #     site=Chyoa.Chyoa(url)
    # elif sites[5]==domain:
    #     site=Wattpad.Wattpad(url)
    # else:
    #     print(domain)
    #     print('Unsupported website, terminating program')
    #     site=None
    if args.t:
        q.put(site)
    return site

#setting up commandline argument parser
parser=argparse.ArgumentParser()
parser.add_argument('url', help='The URL of the story you want', nargs='?')
parser.add_argument('-o','--output-type', help='The file type you want', choices=['txt', 'epub'])
parser.add_argument('-f','--file', help="Use text file containing a list of URLs instead of single URL", action='store_true')
parser.add_argument('-d','--directory', help="Directory to place output files. Default ./")
parser.add_argument('-q','--quiet', help="Turns off most terminal output", action='store_true')
parser.add_argument('-t', help="Turns on multithreading mode. Recommend also enabling --quiet", action='store_true')
args=parser.parse_args()

if args.quiet:
    sys.stdout=open(os.devnull, 'w')
    #print('quiet enabled')

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
cwd=os.getcwd()
wd=os.path.join(cwd, wd)
if not os.path.exists(wd):
    os.makedirs(wd)

ftype=args.output_type

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
        q=queue.Queue()
        for i in urls:
            t=threading.Thread(target=MakeClass, args=(i,), daemon=True)
            t.start()
        while threading.active_count()>1:
            s=q.get()
            if ftype=='epub':
                #for site in s:
                MakeEpub(s)
            else:
                #for site in s:
                MakeText(s)
            
    else:
        for i in urls:
            #site=MakeClass(i)
            if ftype=='epub':
                MakeEpub(MakeClass(i))
            else:
                MakeText(MakeClass(i))

#the single input version
else:
    site=MakeClass(args.url)
    if site==None:
        sys.exit()
    if ftype=='epub':
        MakeEpub(site)
    else:
        MakeText(site)
