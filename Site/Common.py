import sys, urllib, os

#Module contains common functions needed by sites

quiet = False

images = False

wd = './'

opf = 'txt'

dup = False

mt = False
def prnt(out, f=False):
    if not quiet and not f:
        print(out)

def imageDL(title, url, num,  size=0, pbar=None):
    if not os.path.exists(wd+title):
        try:
            os.makedirs(wd+title)
        except FileExistsError as fee:
            pass
    zeros = '0' * (len(str(size))-1)
    #print(zeros)
    if len(zeros)>1 and num > 9:
        zeros='0'
    elif len(zeros)==1 and num > 9:
        zeros = ''
    if num > 99:
        zeros = ''
    if pbar is None:
        zeros = 'img' #TODO fix this for Chyoa stories so that image files don't have to be prepended with 'img' and no zeros
    #print(zeros)
    with open(wd+title+'/'+zeros+str(num)+'.jpg', 'wb') as myimg:
        myimg.write(GetImage(url))
    if pbar is not None:
        pbar.Update()
    #queue.put()


def CheckDuplicate(title):
    if opf == 'epub':
        return os.path.isfile(wd+title+'.epub')
    elif opf == 'txt':
        return os.path.isfile(wd+title+'.txt') or os.path.exists(wd+title)
    elif opf == 'html':
        return os.path.isfile(wd+title+'.html') or os.path.exists(wd+title)
    
    
def GetImage(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'})
        return urllib.request.urlopen(req).read()
    except:
        if url[-4:]=='.jpg':
            req = urllib.request.Request(url[:-4]+'.png', headers={'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'})
        elif url[-4:]=='.png':
            req = urllib.request.Request(url[:-4]+'.jpg', headers={'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'})
        return urllib.request.urlopen(req).read()
class Progress:
    
    #toolbar_width=40
    size=0
    point=0
    step=0
    
    def __init__(self, size):
        if quiet:
            return
        self.size=size
        sys.stdout.write("[%s]" % (" " *  self.size))
        sys.stdout.flush()
        sys.stdout.write("\b" * (self.size+1))
        
    def Update(self):
        if quiet:
            return
        sys.stdout.write("=")
        sys.stdout.flush()
        
    def End(self):
        if quiet:
            return
        sys.stdout.write('\n')

