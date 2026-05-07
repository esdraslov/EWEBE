import sys, os
import curses
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup, NavigableString, Tag
from engines import essi

def get_content(uri):
    parsed = urlparse(uri)

    if parsed.scheme == "file":
        path = parsed.path
        if os.path.exists(path):
            with open(path, 'r', encoding="utf-8") as f:
                return f.read(), 200, "text/html"
        else:
            return "<html><body>404 file not found</body></html>", 404, "text/html"
    else:
        re = requests.get(uri)
        return re.text, re.status_code, re.headers.get("content-type", "").split(";")[0]

colors = False
def draw_topbar(stdscr):
    wsize = stdscr.getmaxyx()
    stdscr.addstr(0, 0, " FILE" + (" " * (wsize[1] - 6)), curses.color_pair(1))

def view(stdscr, ans, mode):
    # For now, I'll assume the terminal supports colors
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    cl = {}
    for i in range(1, curses.COLORS):
        curses.init_pair(i+1, i, curses.COLOR_BLACK)
        cl[i+1] = i
    colors = True
    h, w = stdscr.getmaxyx()
    rerender = True

    if mode == "html":
        try:
            while True:
                if rerender:
                    stdscr.clear()
                    soup = BeautifulSoup(ans, "html.parser")
                    for invis in soup(["script", "style"]):
                        invis.decompose()

                    body = soup.body
                    if body:
                        y = 1
                        for node in body.descendants:
                            if y < h - 1:
                                s = 0
                                if isinstance(node, Tag):
                                    s = essi.style_tag(node.get("style"), cl)
                                    stdscr.addstr(y, 0, node.text[:w-1], s)
                                    y += 1

                    rerender = False
                draw_topbar(stdscr)

                stdscr.refresh()
        except KeyboardInterrupt:
            pass


url = input("Insert URL/URI here: ")

text, status, format = get_content(url)
print(status, format)
if 300 > status > 199:
    match format:
        case "text/html":
            curses.wrapper(view, text, "html")
