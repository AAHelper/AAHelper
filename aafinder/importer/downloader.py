# import sqlite3
import os
import pathlib
import requests
from urllib.parse import urlparse
from lxml import html
from .utils import get_or_create_downloads_folder

BASE_URL = "http://www.aasandiego.org/"


def download_and_save_page(page):
    print(f"Attempting to download page {page}")
    fname = urlparse(page).path.split("/")[-1]
    path = pathlib.Path(os.path.join(get_or_create_downloads_folder(), fname))
    resp = None

    if not path.exists():
        print(f'Page {page} does not exist, downloading and saving the page.')
        resp = requests.get(page)
        resp.raise_for_status()
        with path.open(mode="w") as fp:
            fp.write(resp.text)
    else:
        print(f'Page {page} already downloaded, delete {path} to re-download.')

    return resp


def get_anchors(content):
    this_page = html.fromstring(content)
    this_page.make_links_absolute(BASE_URL)

    for a in this_page.iterlinks():
        element, attribute, link, pos = a
        print(attribute, link.startswith(BASE_URL), link.endswith(".html"))
        if attribute == 'href' and\
                link.startswith(BASE_URL) and link.endswith(".html"):
            print(f'Found anchor to {link}.')
            yield link

def download_page_if_any(url):
    download_dir = get_or_create_downloads_folder()
    resp = download_and_save_page(url)
    if not resp:
        path = pathlib.Path(
            os.path.join(download_dir, 'legend.html'))
        with path.open() as fp:
            content = fp.read()

    for anchor in get_anchors(content):
        download_and_save_page(anchor)

def download_all():
    start_page = "http://www.aasandiego.org/legend.html"
    downloads_folder = get_or_create_downloads_folder()
    resp = download_and_save_page(start_page)
    if not resp:
        path = pathlib.Path(
            os.path.join(downloads_folder, 'legend.html'))
        with path.open() as fp:
            content = fp.read()
    else:
        content = resp.content

    for anchor in get_anchors(content):
        download_and_save_page(anchor)
    looked_at = []
    for path in pathlib.Path(downloads_folder).iterdir():
        if path not in looked_at:
            if path.name != 'legend.html':
                content = path.read_text()
            for anchor in get_anchors(content):
                download_and_save_page(anchor)