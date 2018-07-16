import os


def get_or_create_downloads_folder():
    abspath = os.path.dirname(os.path.abspath(__file__))
    download_folder = os.path.join(abspath, 'downloads')
    os.makedirs(download_folder, exist_ok=True)
    return download_folder
