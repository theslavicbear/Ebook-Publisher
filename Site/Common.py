import sys

#Module contains common functions needed by all sites

quiet = False

images = False

def prnt(out, f=False):
    if not quiet and not f:
        print(out)

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

