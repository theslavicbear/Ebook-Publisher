# Ebook-Publisher
A Python tool for converting online stories into portable formats

**Download Ebook-Publisher by cloning the git repository `git clone https://github.com/theslavicbear/Ebook-Publisher.git` or downloading the zip of the latest release (generally more stable, as I tend to push directly to master) and running the Ebook-Publisher.py file. At a minimum, you must supply one URL from a supported site as a command line argument. With no other options, you will receive a text file with the story contents. Please see the below help message for a list of possible options to improve your experience, e.g. multiple URL inputs, concurrent downloads, and/or EPUB/HTML formatted output files.**

Ebook-Publisher is my pet project, and the project that I currently have spent the most time and effort on. As such, I welcome criticism, requests for improvement, and bug reports. Please open an issue for any of the preceding.

## Currently supported sites:
* ~~fanfiction.net~~
* ~~fictionpress.com~~ (fanfiction and fictionpress currently cannot be scraped due to updates in the sites that I can't work around. Probably won't be fixed as honestly you can find better downloaders for the sites)
* literotica.com
* ~~classicreader.com~~ (Site seems to have been shut down)
* chyoa.com (You may either input the first page of a story, and Ebook-Publisher will grab the whole story, or input the last page you want included and Ebook-Publisher will work backwards and grab the story from the beginning to your input page. You will be asked for customizable names, etc. before the story is grabbed.)
* wattpad.com
* nhentai.net (Either grabs every image and dumps in a folder for TXT and HTML (HTML adds an HTML file for easy reading via web browser), or tries to add every image to an EPUB file)

Want more sites supported? Open an Issue and ask for its support or add support for the site yourself! 

  
## Currently supported file types:
* plain text files
* epub ebook files
* html files
  
Want more formats supported? Open an Issue or try using a tool like Pandoc to convert one of the already supported file types.
 
## Usage:

Ebook-Publisher requires the following:
* Python3

On the small amount of testing I have done under Windows 8.1, I did need to install the requests package, which only reqired a quick `C:\Python34\Scripts\pip.exe install requests` From there, if you do not have the python3 executable on your PATH, you can run like `C:\Python34\python.exe C:\Path\To\Ebook-Publisher.py` Obviously, use the folder name of your installed version of python3. 

To run Ebook-Publisher, use the terminal or command prompt to execute Python3 and pass in Ebook-Publisher.py and the URL for the story you want. The URL can either be one or more links to a story on a supported webpage, or one or more text files containing a list of webpage URLs. You do not need to distinguish between the two. You can add several other arguments. Try `python3 Ebook-Publisher.py --help` for the detailed readout, or see below:

```
usage: ebook-publisher [-h] [-o {txt,epub,html,TXT,EPUB,HTML}] [-d DIRECTORY]
                       [-q] [-t] [-i] [-n] [-s CSS]
                       [url [url ...]]

positional arguments:
  url                   The URL of the story you want

optional arguments:
  -h, --help            show this help message and exit
  -o {txt,epub,html,TXT,EPUB,HTML}, --output-type {txt,epub,html,TXT,EPUB,HTML}
                        The file type you want
  -d DIRECTORY, --directory DIRECTORY
                        Directory to place output files. Default ./
  -q, --quiet           Turns off most terminal output
  -t                    Turns on multithreading mode. Recommend also enabling
                        --quiet
  -i, --insert-images   Downloads and inserts images for Chyoa stories
  -n, --no-duplicates   Skips stories if they have already been downloaded
  -s CSS, --css CSS, --style-sheet CSS
                        either a CSS string or a .css file to use for
                        formatting

```  

                        
### Sample Usage:

`python3 Ebook-Publisher.py www.some.website/stories/my-story -o epub -o html -d ~/Documents/My\ Books/`

`./Ebook-Publisher.py -o txt to-download.txt`

### Using standard input:

`cat list.txt | python3 Ebook-Publisher.py -d ./output`

`echo www.some.website/stories/my-story | ./Ebook-Publisher.py -o epub -d ~/Documents/My\ Books/`

### Known Issues

* Image downloading can fail without alerting the user.
* Progress bar behaves poorly when there are a large number of chapters/pages in a story.
* Fanfiction and Fictionpress links currently do not work.
