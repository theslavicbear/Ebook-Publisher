# Ebook-Publisher
A Python tool for converting online stories into portable formats

## Currently supported sites:
* fanfiction.net
* fictionpress.com
* literotica.com
  
## Currently supported file types:
* plain text files
* epub ebook files
  
Want more sites supported? Open an Issue and ask for its support or add support for the site yourself! Guidelines for adding support for a new site below.

## Usage:
Ebook-Publisher requires the following:
* Python3
* Beautiful Soup 4 (Python3 edition)
* ebooklib (for creating epub files)

Both external libraries can be installed with pip `pip3 install beautifulsoup4 && pip3 install ebooklib`

To run Ebook-Publisher, use the terminal or command prompt to execute Python3 and pass in Ebook-Publisher.py as well as the URL for the story and the preferred format:

`python3 Ebook-Publisher.py www.some.website/stories/my-story txt`

**The second argument must be the URL and the third argument must be the preferred file type. If you do not provide a preferred file type the code will default to .txt**

## Adding support for sites:

Coming soon
