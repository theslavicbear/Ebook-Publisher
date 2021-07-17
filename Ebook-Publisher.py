#!/usr/bin/env python3
import sys
from Site import *
import urllib.parse
from EpubMaker import epub as epub
import argparse
import os
import threading
import queue
import shutil
from zipfile import ZipFile

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
formats={
    'epub':lambda x:MakeEpub(x),
    'html':lambda x:MakeHTML(x),
    'txt' :lambda x:MakeText(x),
    'EPUB':lambda x:MakeEpub(x),
    'HTML':lambda x:MakeHTML(x),
    'TXT' :lambda x:MakeText(x),
}

#function for making text files
def MakeText(site):
    if type(site) is not Nhentai.Nhentai:
        published=open(wd+site.title+'.txt', 'w', encoding="utf-8")
        published.write(site.title+'\n')
        published.write('by '+site.author+'\n\n')
        published.write(site.story)
        published.close()
    
def MakeHTML(site):
    if (type(site) is Chyoa.Chyoa or type(site) is Nhentai.Nhentai) and site.hasimages:
        published=open(wd+site.title+'/'+site.title+'.html', 'w', encoding="utf-8")
    else:
        published=open(wd+site.title+'.html', 'w', encoding="utf-8")
    published.write('<!DOCTYPE html>\n')
    published.write('<html lang="en">\n')
    published.write('<style>\n'+styleSheet+'\n</style>')
    published.write('<head>\n<title>'+site.title+' by '+site.author+'</title>\n</head>\n')
    published.write('<h1>'+site.title+'</h1><h3>by '+site.author+'</h3><br /><a href='+site.url+'>'+site.url+'</a>\n')
    if type(site) not in (Nhentai.Nhentai, Literotica.Literotica):
        published.write('<h2>Table of Contents</h2>\n')
        if not type(site) is Chyoa.Chyoa:
            for i in range(len(site.rawstoryhtml)):
                published.write('<p><a href="#Chapter '+str(i)+'">'+site.chapters[i]+'</a></p>\n')
        elif not site.backwards:
            for i in range(len(site.rawstoryhtml)):
                if i!=0:
                    published.write('<p><a href="#'+str(site.depth[i-1])+'">'+str(' _'*int((len(site.depth[i-1])/2)+1))+' '+str(int((len(site.depth[i-1])/2)+2))+'.'+site.depth[i-1].split('.')[-1]+' '+site.chapters[i]+'</a></p>\n')
                else:
                    published.write('<p><a href="#Chapter '+str(i)+'">'+'1.1 '+site.chapters[i]+'</a></p>\n')
        else:
            for i in range(len(site.rawstoryhtml)):
                published.write('<p><a href="#Chapter '+str(i)+'">'+site.chapters[i]+'</a></p>\n')
    for i in range(len(site.rawstoryhtml)):
        if type(site) is Nhentai.Nhentai:
            published.write(site.truestoryhttml[i])
        elif type(site) is Literotica.Literotica:
            published.write(site.storyhtml)
            break
        else:
            if type(site) is Chyoa.Chyoa and not site.backwards:
                if i !=0:
                    published.write('<h2 id = "'+site.depth[i-1]+'">'+site.chapters[i]+'\n</h2>\n'+str(site.rawstoryhtml[i]))
                else:
                    published.write('<h2 id="Chapter '+str(i)+'">\n'+site.chapters[i]+'\n</h2>\n'+str(site.rawstoryhtml[i]))
            else:    
                published.write('<h2 id="Chapter '+str(i)+'">\n'+site.chapters[i]+'\n</h2>\n'+str(site.rawstoryhtml[i]))
    published.write('</html>')
    
    
    published.close()
    
#def GetImage(url):
    #req = urllib.request.Request(url, headers={'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'})
    #return urllib.request.urlopen(req).read()
            
    
#This function is basically all magic from the docs of EpubMaker
def MakeEpub(site):
    book=epub.EpubBook()
    book.set_identifier(site.url)
    titlepage=epub.EpubHtml(title='Title Page', file_name='Title.xhtml', lang='en')
    titlepage.content='<h1>'+site.title+'</h1><h3>by '+site.author+'</h3><br /><a href='+site.url+'</a>'
    #add summary information
    if hasattr(site, 'summary'):
        titlepage.content+='<br /><p>'+site.summary+'</p>'
    book.add_item(titlepage)
    book.spine=[titlepage]
    book.set_title(site.title)
    book.set_language('en')
    book.add_author(site.author)
    book.add_style_sheet(styleSheet)
    c=[]

    if type(site) is not Literotica.Literotica and type(site) is not Nhentai.Nhentai:
        toc=[]
        for i in range(len(site.rawstoryhtml)):
            if type(site) is Chyoa.Chyoa and not site.backwards:
                if i == 0:
                    c.append(epub.EpubHtml(title=site.chapters[i], file_name='Chapter '+str(i+1)+'.xhtml', lang='en'))
                else:
                    c.append(epub.EpubHtml(title=site.chapters[i], file_name=str(site.depth[i-1])+'.xhtml', lang='en', tocTitle=str(' _'*int((len(site.depth[i-1])/2)+1))+' '+str(int((len(site.depth[i-1])/2)+2))+'.'+site.depth[i-1].split('.')[-1]+' '+site.chapters[i]))
                c[i].content='<h2>\n'+site.chapters[i]+'\n</h2>\n'+str(site.epubrawstoryhtml[i])
            elif type(site) is Nhentai.Nhentai:
                c.append(epub.EpubHtml(title=site.chapters[i], file_name='Chapter '+str(i+1)+'.xhtml', lang='en'))
                c[i].content=site.truestoryhttml[i]
            else:
                c.append(epub.EpubHtml(title=site.chapters[i], file_name='Chapter '+str(i+1)+'.xhtml', lang='en'))
                c[i].content='<h2>\n'+site.chapters[i]+'\n</h2>\n'+str(site.rawstoryhtml[i])
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
    
    if type(site) is Nhentai.Nhentai:
        if site.hasimages == True:
            with ZipFile(wd+site.title+'.epub', 'a') as myfile:
                i=1
                for url in site.images:
                    zeros = '0' * (len(str(len(site.images)))-1)
                    if len(zeros)>1 and i > 9:
                        zeros='0'
                    elif len(zeros)==1 and i > 9:
                        zeros = ''
                    if i > 99:
                        zeros = ''
                    with myfile.open('EPUB/'+zeros+str(i)+'.jpg', 'w') as myimg:
                        myimg.write(Common.GetImage(url))
                    i=i+1
    elif type(site) is Chyoa.Chyoa:
        if site.hasimages == True:
            with ZipFile(wd+site.title+'.epub', 'a') as myfile:
                i=1
                for num in Common.urlDict[site.url]:
                    try:
                        i=i+1
                        with myfile.open('EPUB/img'+str(i-1)+'.jpg', 'w') as myimg:
                            myimg.write(Common.GetImage(Common.urlDict[site.url][num]))
                    except urllib.error.HTTPError as FE:
                        continue
    

def MakeClass(url):
    #getting url
    domain=urllib.parse.urlparse(url)[1]
    if domain == 'nhentai.net' and args.t:
        #TODO the lock should be in the Nhentai class definitions
        with lock:
            site=sites[domain](url)
    else:
        try:
            site=sites[domain](url)
        except KeyError as e:
            print('Unsupported site: '+domain)
            return
    #site=sites[domain](url)
    if args.t:
        if not site.duplicate:
            for ft in ftype:
                formats[ft](site)
            q.put(site)
        else:
            return
    return site

#grabs all of the urls if the argument is a file, or assumes the argument is a single URL
def ListURLs(url):
    if os.path.isfile(os.path.join(cwd,url)):
        with open(cwd+'/'+url, 'r') as fi:
            return fi.read().splitlines()
    else:
        return (url,)
def getCSS():
    if os.path.isfile(os.path.join(cwd,args.css)):
        with open(cwd+'/'+args.css, 'r') as fi:
            return fi.read()
    else:
        return args.css


#setting up commandline argument parser
parser=argparse.ArgumentParser()
parser.add_argument('url', help='The URL of the story you want', nargs='*')
parser.add_argument('-o','--output-type', help='The file type you want', choices=['txt', 'epub', 'html', 'TXT', 'EPUB', 'HTML'], action='append')
#parser.add_argument('-f','--file', help="Does nothing! Previously denoted the use of a text file containing a list of URLs instead of single URL", action='store_true')
parser.add_argument('-d','--directory', help="Directory to place output files. Default ./")
parser.add_argument('-q','--quiet', help="Turns off most terminal output", action='store_true')
parser.add_argument('-t', help="Turns on multithreading mode. Recommend also enabling --quiet", action='store_true')
parser.add_argument('-i', '--insert-images', help="Downloads and inserts images for Chyoa stories", action='store_true')
parser.add_argument('-n', '--no-duplicates', help='Skips stories if they have already been downloaded', action='store_true') 
parser.add_argument('-s', '--css', '--style-sheet', help='either a CSS string or a .css file to use for formatting', default='')
parser.add_argument('--chyoa-force-forwards', help='Force Chyoa stories to be scraped forwards if not given page 1', action='store_true')
args=parser.parse_args()

#print(args.output_type)

if args.quiet:
    Common.quiet=True
    #sys.stdout=open(os.devnull, 'w')
    #print('quiet enabled')
if args.insert_images:
    Common.images=True
args.file=True
stdin=False
if not sys.stdin.isatty():
    stdin=True
elif not args.url:
    #print(args.url)
    parser.error('No input')

if args.no_duplicates:
    Common.dup = True
    
if args.chyoa_force_forwards:
    Common.chyoa_force_forwards=True


if args.directory is None:
    wd='./'
else:
    wd=args.directory
Common.wd = wd

Common.opf = args.output_type
if Common.opf == None:
    Common.opf = ['txt']



Common.mt = args.t

cwd=os.getcwd()
#TODO should use non-relative path
wd=os.path.join(cwd, wd)
if not os.path.exists(wd):
    os.makedirs(wd)
    

styleSheet=getCSS()

ftype=args.output_type
if ftype == None:
    ftype = ['txt']
q=queue.Queue()


if args.file:
    
    urls=[]
    #gets the list of urls
    if not stdin:
        for arg in args.url:
            urls.extend(ListURLs(arg))
    else:
        stdinput=sys.stdin.read()
        urls=stdinput.split()
    
    urls=list(set(urls))
    
    for url in urls:
        Common.urlDict[url]={}

    threads=0
    #the multithreaded variant
    if args.t:
        lock = threading.Lock()
        threads = len(urls)
        for i in urls:
            t=threading.Thread(target=MakeClass, args=(i,), daemon=False)
            t.start()

    else:
        for i in urls:
            clas=MakeClass(i)
            if clas is not None:
                if not clas.duplicate:
                    for ft in ftype:
                        formats[ft](clas)

    while threads>1:
        q.get()
        threads-=1
