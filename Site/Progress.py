import sys

class Progress:
    
    #toolbar_width=40
    size=0
    point=0
    step=0
    
    def __init__(self, size):
        self.size=size
        sys.stdout.write("[%s]" % (" " *  self.size))
        sys.stdout.flush()
        sys.stdout.write("\b" * (self.size+1))
        
    def Update(self):
        sys.stdout.write("=")
        sys.stdout.flush()
        
    def End(self):
        sys.stdout.write('\n')
