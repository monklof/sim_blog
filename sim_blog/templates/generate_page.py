#! /usr/bin/env python3
"""Generate page, currently support geeks/about page
./generage_page.py [pagename]
pagename - geeks/about page, default "about"
"""

import os,sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from libs.utils import render_gfm


def main(page_name):
    htmltext = render_gfm(open("%s.md" % page_name, "r").read())
    f = open("%s-content.html" % page_name, "w")
    f.write(htmltext)
    f.close()

if __name__ == "__main__":
    main((len(sys.argv) > 1 and sys.argv[1]) or "about")
