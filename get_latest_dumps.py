import requests
import re
import sys
from datetime import date
from xml.dom import minidom
from os import path


year = date.today().year
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_2) AppleWebKit/534.51.22 (KHTML, like Gecko) Version/5.1.1 Safari/534.51.22"
ACCEPT = "Accept-Encoding: gzip, deflate"
URL_LIST = "http://discogs-data.s3-us-west-2.amazonaws.com/?delimiter=/&prefix=data/{0}/".format(year)
URL_DIR = "http://discogs-data.s3-us-west-2.amazonaws.com/{0}"
TMP = "discogs-{0}.urls".format(year)
PATTERN = r"discogs_[0-9]{8}_(artists|labels|masters|releases).xml.gz"


def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)


def get_list():
    r = requests.get(URL_LIST)
    return r.text


def xml_extract_latest(text):
    dom = minidom.parseString(text)
    file_nodes = [getText(n.childNodes) for n in dom.getElementsByTagName('Key')]
    files = sorted(file_nodes, reverse=True)
    last4 = []
    for f in files:
        if re.search(PATTERN, f) is not None:
            last4.append(f)
        if len(last4) == 4:
            break

    return last4


def make_url(*chunks):
    for chunk in chunks:
        yield URL_DIR.format(chunk)


if __name__ == "__main__":
    xml = ''
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        with open(path.realpath("./tmp/ListBucketResult.xml")) as fxml:
            xml = fxml.read()
    else:
        xml = get_list()
    print('\n'.join(make_url(*xml_extract_latest(xml))))
