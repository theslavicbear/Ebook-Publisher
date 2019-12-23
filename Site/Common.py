import sys, urllib, os

#Module contains common functions needed by sites

quiet = False

images = False

wd = './'

opf = 'txt'

def prnt(out, f=False):
    if not quiet and not f:
        print(out)

def imageDL(title, url, size, num, pbar):
    if not os.path.exists(wd+title):
        os.makedirs(wd+title)
    zeros = '0' * (len(str(size))-1)
    #print(zeros)
    if len(zeros)>1 and num > 9:
        zeros='0'
    elif len(zeros)==1 and num > 9:
        zeros = ''
    if num > 99:
        zeros = ''
    #print(zeros)
    with open(wd+title+'/'+zeros+str(num)+'.jpg', 'wb') as myimg:
        myimg.write(GetImage(url))
    pbar.Update()


def GetImage(url):
    req = urllib.request.Request(url, headers={'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'})
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

