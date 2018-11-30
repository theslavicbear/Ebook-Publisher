#from bs4 import BeautifulSoup
#import requests
from time import sleep
import sys
from Site import *
import urllib.parse
from ebooklib import epub
import argparse

#Master array of supported sites
sites=['www.literotica.com', 'www.fanfiction.net', 'www.fictionpress.com','www.classicreader.com','chyoa.com']

#function for making text files
def MakeText(site):
    published=open(site.title+'.txt', 'w')
    published.write(site.title+'\n')
    published.write('by '+site.author+'\n\n')
    published.write(site.story)
    published.close()
    
#This function is basically all space magic from the docs of ebooklib
def MakeEpub(site):
    book=epub.EpubBook()
    book.set_identifier(url)
    titlepage=epub.EpubHtml(title='Title Page', file_name='Title.xhtml', lang='en')
    titlepage.content='<h1>'+site.title+'</h1><h3>by '+site.author+'</h3><br /><a href=\'url\'>'+url+'<a>'
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
    epub.write_epub(site.title+'.epub', book, {})
    
'''    
#specified URL. Asks for URL if no URL specified
try:
    url=str(sys.argv[1])
except:
    print("Input URL for story")
    url=input()
'''

parser=argparse.ArgumentParser()
parser.add_argument('url', help='The URL of the story you want')
parser.add_argument('-o','--output-type', help='The file type you want', choices=['txt', 'epub'])
parser.add_argument('-f','--file', help="Use text file containing a list of URLs instead of single URL", action='store_true')
args=parser.parse_args()


#getting url
url=args.url
domain=urllib.parse.urlparse(url)[1]
#returns www.site.extension


if not args.file:
    if sites[0]==domain:
        site=Literotica.Literotica(url)
    elif sites[1]==domain:
        site=Fanfiction.Fanfiction(url)
    elif sites[2]==domain:
        site=Fanfiction.Fanfiction(url)
    elif sites[3]==domain:
        site=Classicreader.Classicreader(url)
    elif sites[4]==domain:
        site=Chyoa.Chyoa(url)
    else:
        print('Unsupported website, terminating program')
        sys.exit()

#try:
    #a=sys.argv[2]
#except:
    #print('Select preferred output format: (1. txt) (2. epub)')
    #a=input()

ftype=args.output_type

if ftype in ('epub', 'Epub', '.epub', 'EPUB', '2'):
    MakeEpub(site)
elif ftype in ('txt', 'text', '.txt', 'TXT', '1'):
    MakeText(site)
else:
    print('No format provided, defaulting to .txt')
    MakeText(site)
