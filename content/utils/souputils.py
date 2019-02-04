from pathlib import Path
from bs4 import BeautifulSoup

RESOURCE_DIR = Path(__file__).parent.parent.joinpath("resource")

def soup_from_file(path, absolute_path = False):
    if (absolute_path):
        url = path
    else:
        url = RESOURCE_DIR.joinpath(path)

    with open(url) as f:
        soup = BeautifulSoup(f, "html.parser")
    return soup

def soup_from_text(text):
    return BeautifulSoup(text, "html.parser")

def soup_to_bytes(soup):
    return soup.prettify().encode('UTF-8')