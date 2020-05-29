import re
from urllib.parse import urlparse, ParseResult

url_regex = re.compile(
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]'
        r'{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)


def validate_redirect(url):
    """Basically converts www.example.com to http://www.example.com"""
    pars = urlparse(url.decode(), 'http')
    netloc = pars.netloc or pars.path
    path = pars.path if pars.netloc else ''
    if not netloc.startswith('www.'):
        netloc = 'www.' + netloc

    return ParseResult('http', netloc, path, *pars[3:]).geturl()


def validate_url(url):
    """Checks if is a url"""
    return re.match(url_regex, url)
