# Ebook-Publisher
A Python tool for converting online stories into portable formats

**Download Ebook-Publisher by cloning the git repository `git clone https://github.com/theslavicbear/Ebook-Publisher.git` or downloading the zip of the latest release (generally more stable, as I tend to push directly to master) and running the Ebook-Publisher.py file. At a minimum, you must supply one URL from a supported site as a command line argument. With no other options, you will receive a text file with the story contents. Please see the below help message for a list of possible options to improve your experience, e.g. multiple URL inputs, concurrent downloads, and/or EPUB formatted output files.**

Ebook-Publisher is my pet project, and the project that I currently have spent the most time and effort on. As such, I welcome criticism, requests for improvement, and bug reports. Please open an issue for any of the preceding.

## Currently supported sites:
* fanfiction.net
* fictionpress.com
* literotica.com
* classicreader.com (The site does not appear to be working as of 11/30/19)
* chyoa.com (rudimentary support: Input the last page you wish to include, and the code will work backwards towards the beginning of the story. You will be asked to input customizable names if they are found)
* wattpad.com
* nhentai.net (alpha support):  ~~Seems to have issues with multithreading multiple nhentai galleries.~~  **Multithreading now works for default gallery downloads!** Also may have issues with your epub reader if you grabbed it in epub format (i.e. low quality images in Okular).
  
## Currently supported file types:
* plain text files
* epub ebook files
* html files (For nhentai galleries, it will have the same output as with default/.txt output, but with an html file in the folder that easily allows viewing the gallery via a web browser. Chyoa stories don't currently grab images yet)
  
Want more sites supported? Open an Issue and ask for its support or add support for the site yourself! 

## Usage:

Ebook-Publisher requires the following:
* Python3

As of Release 2.0, Ebook-Publisher should not require any external libraries, other than python3. Everything needed is either included in the repository or in python3's standard library.

To run Ebook-Publisher, use the terminal or command prompt to execute Python3 and pass in Ebook-Publisher.py and the URL for the story you want. You can add several other arguments. Try `python3 Ebook-Publisher.py --help` for the detailed readout, or see below:

```
usage: ebook-publisher [-h] [-o {txt,epub}] [-f] [-d DIRECTORY] [-q] [-t] [-i]
                       [url]

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
  -q, --quiet           Turns off most terminal output
  -t                    Turns on multithreading mode. Recommend also enabling
                        --quiet
  -i, --insert-images   Downloads and inserts images for Chyoa stories
```  

                        
### Sample Usage:

`python3 Ebook-Publisher.py www.some.website/stories/my-story -o epub -d ~/Documents/My\ Books/`

`./Ebook-Publisher.py -o txt -f to-download.txt`

### Using standard input:

`cat list.txt | python3 Ebook-Publisher.py -d ./output`

`echo www.some.website/stories/my-story | ./Ebook-Publisher.py -o epub -d ~/Documents/My\ Books/`
