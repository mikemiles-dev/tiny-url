import re
from urllib.parse import urlparse, ParseResult

regex = re.compile(
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]'
        r'{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)


def validate_redirect(url):
    """Validates URL is valid before we do redirect"""
    p = urlparse(url.decode(), 'http')
    netloc = p.netloc or p.path
    path = p.path if p.netloc else ''
    if not netloc.startswith('www.'):
        netloc = 'www.' + netloc

    p = ParseResult('http', netloc, path, *p[3:])
    return p.geturl()


def validate_url(url):
    """Checks if is a url"""
    return re.match(regex, url)
