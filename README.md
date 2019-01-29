# Ebook-Publisher
A Python tool for converting online stories into portable formats

## Currently supported sites:
* fanfiction.net
* fictionpress.com
* literotica.com
* classicreader.com
* chyoa.com (rudimentary support: Input the last page you wish to include, and the code will work backwards towards the beginning of the story. You will be asked to input customizable names if they are found)
  
## Currently supported file types:
* plain text files
* epub ebook files
  
Want more sites supported? Open an Issue and ask for its support or add support for the site yourself! 

## Usage:
Ebook-Publisher requires the following:
* Python3
* Beautiful Soup 4 (Python3 edition)
* ebooklib (for creating epub files)

Both external libraries can be installed with pip `pip3 install beautifulsoup4 && pip3 install ebooklib`

To run Ebook-Publisher, use the terminal or command prompt to execute Python3 and pass in Ebook-Publisher.py and the URL for the story you want. You can add several other arguments. Try `python3 Ebook-Publisher.py --help` for the detailed readout, or see below:


    usage: Ebook-Publisher.py [-h] [-o {txt,epub}] [-f] [-d DIRECTORY] url

    positional arguments:
      url                   The URL of the story you want

    optional arguments:
      -h, --help            show this help message and exit
      -o {txt,epub}, --output-type {txt,epub}
                            The file type you want
      -f, --file            Use text file containing a list of URLs instead of
                            single URL
      -d DIRECTORY, --directory DIRECTORY
                            Directory to place output files. Default ./

                        
Sample Usage:

`python3 Ebook-Publisher.py www.some.website/stories/my-story -o epub -d ~/Documents/My\ Books/`

`./Ebook-Publisher.py -f -o txt to-download.txt`
