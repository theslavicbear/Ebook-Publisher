from bs4 import BeautifulSoup
import requests
from time import sleep
import sys
from Site import *
import urllib.parse
from ebooklib import epub
import zipfile

#Master array of supported sites
sites=['www.literotica.com', 'www.fanfiction.net']

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
    book.set_identifier(urllib.parse.urlparse(url)[2])
    book.set_title(site.title)
    book.set_language('en')
    book.add_author(site.author)
    c=[]
    #print(str(type(site)))
    if type(site) is Fanfiction.Fanfiction:
        for i in range(len(site.rawstoryhtml)):
            c.append(epub.EpubHtml(title=site.chapters[i], file_name='Chapter '+str(i+1)+'.xhtml', lang='en'))
            c[i].content='<h2>\n'+site.chapters[i]+'\n</h2>\n'+site.rawstoryhtml[i].prettify()
            book.add_item(c[i])
    #elif type(site) is Literotica:
    #fallback method
    else:
        c.append(epub.EpubHtml(title=site.title, file_name='Story.xhtml', lang='en'))
        c[0].content=site.storyhtml
        book.add_item(c[0])
    #more ebooklib space magic
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine=['nav']
    for i in c:
        book.spine.append(i)
    epub.write_epub(site.title+'.epub', book, {})
    
    
#specified URL. Asks for URL if no URL specified
try:
    url=str(sys.argv[1])
except:
    print("Input URL for story")
    url=input()
    
domain=urllib.parse.urlparse(url)[1]
#returns www.site.extension
    
#Gets webpage, waits and tries again ad infinitum #TODO make a maximum number of attemps before release
page=requests.get(url)
while page.status_code!=200:
    print("Error getting page, trying again: status code: "+str(page.status_code))
    time.sleep(5)
#parses the document, and sends it to the relevant class    
soup = BeautifulSoup(page.content, 'html.parser')


if sites[0]==domain:
    site=Literotica.Literotica(soup)
elif sites[1]==domain:
    site=Fanfiction.Fanfiction(soup)
else:
    print('Unsupported website, terminating program')
    sys.exit()

try:
    a=sys.argv[2]
except:
    print('Select preferred output format: (1. txt) (2. epub)')
    a=input()

if a in ('epub', 'Epub', '.epub', 'EPUB', '2'):
    MakeEpub(site)
elif a in ('txt', 'text', '.txt', 'TXT', '1'):
    MakeText(site)
else:
    print('No format provided, defaulting to .txt')
    MakeText(site)
