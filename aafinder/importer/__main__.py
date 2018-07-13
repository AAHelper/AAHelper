# from .downloader import download_all
# download_all()
from .parser import Parser
p = Parser()
p.parse_all()

# url = '/Users/mrfunyon/virtualenvs/aasandiego/aasandiego/downloads/Meetings.html'
# from lxml import html
# with open(url) as fp:
#     contents = fp.read()
# dom = html.fromstring(contents)
# from .downloader import BASE_URL
# dom.make_links_absolute(BASE_URL)
# import ipdb; ipdb.set_trace()