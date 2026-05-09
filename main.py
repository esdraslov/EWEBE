import sys, os
import curses
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup, Comment, Tag
from engines import essi

def set_wname(name):
    if os.name == "nt":
        os.system(f"title {name}")
    elif os.name == "posix":
        sys.stdout.write(f"\033]0;{name}\a")
        sys.stdout.flush()

def get_content(uri):
    parsed = urlparse(uri)

    if parsed.scheme == "file":
        path = parsed.path
        if os.path.exists(path):
            if os.path.isfile(path):
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
    global colors

    set_wname("EWEBE")
    # For now, I'll assume the terminal supports colors
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    cl = {}
    for i in range(1, curses.COLORS):
        curses.init_pair(i+1, i, curses.COLOR_BLACK)
        cl[i+1] = i
    colors = True
    h, w = stdscr.getmaxyx()
    rerender = True # This ensures the first render

    stdscr.nodelay(True)

    if mode == "html":
        try:

            y = 1
            page = []
            scroll_y = 0
            max_y = 0
            def walk(tag: Tag):
                nonlocal y
                nonlocal max_y
                style = {}
                if tag.attrs.get("style"):
                    style = essi.style_tag(tag.get("style"), cl)
                for node in tag.children:
                    if y >= h - 1:
                        break
                    if isinstance(node, Comment):
                        continue
                    if isinstance(node, str):
                        shown = str(node)[:w-1].strip()
                        if shown == "": continue
                        if style["positioning"] == "absolute":
                            info = {
                                "x": style["x"],
                                "y": style["y"],
                                "t": shown,
                                "l": "",
                                "s": style,
                                "z": 0,
                                "b": False
                            }
                            page.append(info)
                        else:
                            info = {
                                "x": 0,
                                "y": y,
                                "t": shown,
                                "l": "",
                                "s": style,
                                "z": 0,
                                "b": False
                            }
                            page.append(info)
                            y += 1
                            max_y += 1
                    else:
                        walk(node)

            def draw():
                for info in page:
                    relative_y = info["y"] - scroll_y
                    if 1 <= relative_y < h - 1:
                        stdscr.addstr(relative_y, info["x"], info["t"], curses.color_pair(info["s"].get("color", 0)))

            def process_key(k):
                nonlocal scroll_y
                nonlocal soup
                if k == curses.KEY_UP:
                    scroll_y -= 1
                if k == curses.KEY_DOWN:
                    scroll_y += 1
                if k == 18:
                    soup = BeautifulSoup(ans, "html.parser")

            soup = BeautifulSoup(ans, "html.parser")

            running = True
            while running:
                if rerender:
                    stdscr.clear()
                    h, w = stdscr.getmaxyx()
                    for invis in soup(["script", "style"]):
                        invis.decompose()

                    body = soup.body
                    if body:
                        walk(body)
                    draw()

                    rerender = False
                draw_topbar(stdscr)

                stdscr.refresh()
                k = stdscr.getch()

                if k != -1:
                    process_key(k)
                    rerender = True
        except KeyboardInterrupt:
            pass


url = input("Insert URL/URI here: ")

text, status, format = get_content(url)
print(status, format)
match format:
    case "text/html":
        curses.wrapper(view, text, "html")
