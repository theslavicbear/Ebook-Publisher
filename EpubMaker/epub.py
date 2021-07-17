from zipfile import ZipFile
#import datetime
version = 'Epub-Maker 0.2'
MIMETYPE = 'application/epub+zip'
container = '''<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0">
<rootfiles>
<rootfile media-type="application/oebps-package+xml" full-path="EPUB/content.opf"/>
</rootfiles>
</container>'''

class EpubBook():
   
    def __init__(self):
        self.item_list = []
        self.spine = [] #spine defines what goes in content.opf. 'nav' is the TOC page
        #self.authors = []
        self.toc = []
        self.author = ''
        #self.hasStyle=False
        self.styleString = ''
   
    def set_identifier(self, identifier):
        self.identifier=identifier
   
    def add_item(self, item):
        self.item_list.append(item)
   
    def set_title(self, title):
        self.title = title
   
    def set_language(self, lang):
        self.language=lang
   
    def add_author(self, author):
        self.author = author
   
    def add_style_sheet(self, styleString):
        self.styleString=styleString
   
   
class EpubHtml:
    
    def __init__(self, title='Title', file_name='file_name.xhtml', lang='lang', tocTitle=None):
        self.title = title
        self.file_name = file_name
        self.lang = lang
        self.content=''
        if tocTitle is None:
            self.tocTitle=self.title
        else:
            self.tocTitle=tocTitle
        
#These classes do nothing, but maintain compatibility with my current implementation
class EpubNcx:
    def __init__(self):
        pass
   
class EpubNav:
    def __init__(self):
        pass
   
def write_epub(title, book):
    with ZipFile(title, 'w') as Zip:
        opf_content = '<?xml version="1.0" encoding="utf-8"?>\n<package unique-identifier="id"\nversion="3.0" xmlns="http://www.idpf.org/2007/opf" prefix="rendition: http://www.idpf.org/vocab/rendition/#">\n  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">\n    <meta content="'+version+'" name="generator"/>\n    <dc:identifier id="id">'+book.identifier+'</dc:identifier>\n    <dc:title>'+book.title+'</dc:title>\n    <dc:language>'+book.language+'</dc:language>\n    <dc:creator id="creator">'+book.author+'</dc:creator>\n  </metadata>\n  <manifest>' #building the content.opf file as we iterate through items
        #add default files
        Zip.writestr('mimetype', MIMETYPE)
        Zip.writestr('META-INF/container.xml', container)
        if book.toc != []:
            isTOC = True
        else:
            isTOC = False
            #for adding nav.xhtml and toc.xhtml later
        i = 0
        for item in book.item_list:
            if type(item) is not EpubNav and type(item) is not EpubNcx:
                Zip.writestr('EPUB/'+item.file_name,'<?xml version="1.0" encoding="utf-8"?>\n                                        <!DOCTYPE html>\n                                        <html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" epub:prefix="z3998: http://www.daisy.org/z3998/2012/vocab/structure/#" lang="'+item.lang+'" xml:lang="'+item.lang+'">\n                                        <head>\n                                        <title>'+item.title+'</title>\n                                        <link rel="stylesheet" type="text/css" href="style.css" />\n                                        </head>\n                                        <body>'+item.content+'</body>\n                                        </html>''')
                opf_content +='<item href="'+item.file_name+'" id="chapter_'+str(i)+'" media-type="application/xhtml+xml"/>\n'
                i += 1
            elif type(item) is EpubNcx:
                opf_content +='<item href="toc.ncx" id="ncx" media-type="application/x-dtbncx+xml"/>\n'
                if not isTOC:
                    Zip.writestr('EPUB/toc.ncx','<?xml version="1.0" encoding="utf-8"?>\n                                <ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">\n                                <head>\n                                    <meta content="'+book.identifier+'" name="dtb:uid"/>\n                                    <meta content="0" name="dtb:depth"/>\n                                    <meta content="0" name="dtb:totalPageCount"/>\n                                    <meta content="0" name="dtb:maxPageNumber"/>\n                                </head>\n                                <docTitle>\n                                    <text>'+book.title+'</text>\n                                </docTitle>\n                                <navMap/>\n                                </ncx>') #TODO needs to update for TOC
                elif isTOC:
                    ncxstring = '<?xml version="1.0" encoding="utf-8"?>\n                                <ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">\n                                <head>\n                                    <meta content="'+book.identifier+'" name="dtb:uid"/>\n                                    <meta content="0" name="dtb:depth"/>\n                                    <meta content="0" name="dtb:totalPageCount"/>\n                                    <meta content="0" name="dtb:maxPageNumber"/>\n                                </head>\n                                <docTitle>\n                                    <text>'+book.title+'</text>\n                                </docTitle>\n<navMap>\n'
                    j = 1
                    for item in book.toc:
                        ncxstring += '<navPoint id="chapter_'+str(j)+'">\n<navLabel>\n<text>'+item.title+'</text>\n</navLabel>\n <content src="'+item.file_name+'" />\n</navPoint>'
                    ncxstring += '\n</navMap>\n</ncx>'
                    Zip.writestr('EPUB/toc.ncx', ncxstring)
            elif type(item) is EpubNav:
                opf_content += '<item href="nav.xhtml" id="nav" media-type="application/xhtml+xml" properties="nav"/>\n'
                if not isTOC:
                    Zip.writestr('EPUB/nav.xhtml', '<?xml version="1.0" encoding="utf-8"?>\n                                <!DOCTYPE html>\n                                <html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en" xml:lang="en">\n                                <head>\n                                    <title>'+book.title+'</title>\n <link rel="stylesheet" type="text/css" href="style.css" />\n                               </head>\n                                <body>\n                                    <nav id="id" role="doc-toc" epub:type="toc">\n                                    <h2>'+book.title+'</h2>\n                                    <ol/>\n                                    </nav>\n                                </body>\n                                </html>\n                                ')
                elif isTOC:
                    navstring = '<?xml version="1.0" encoding="utf-8"?>\n                                <!DOCTYPE html>\n                                <html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en" xml:lang="en">\n                                <head>\n                                    <title>'+book.title+'</title>\n  <link rel="stylesheet" type="text/css" href="style.css" />\n                              </head>\n                                <body>\n                                    <nav id="id" role="doc-toc" epub:type="toc">\n                                    <h2>'+book.title+'</h2>\n                                    <ol>\n'
                    for item in book.toc:
                        navstring += '<li>\n<a href="'+item.file_name+'">'+item.tocTitle+'</a>\n</li>\n'
                    navstring += '</ol>\n</nav>\n</body>\n</html>'
                    Zip.writestr('EPUB/nav.xhtml', navstring)
        opf_content +='</manifest>\n<spine toc="ncx">\n'
        i = 0
        for item in book.spine:
            if type(item) is not EpubHtml:
                if item == 'nav':
                    opf_content += '<itemref idref="nav"/>\n'
            else:
                opf_content += '<itemref idref="chapter_'+str(i)+'"/>\n'
                i+=1
        opf_content += '</spine>\n</package>'
        Zip.writestr('EPUB/style.css', book.styleString)
        Zip.writestr('EPUB/content.opf', opf_content)
        
if __name__ == '__main__':
    print('You have mistakenly run this file, epub.py. It is not meant to be run. It must be imported by another python file (or an implementation can be added to this __main__ section).')
