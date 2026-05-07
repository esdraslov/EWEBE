'''
 * Esdraslov's Style Sheet Interpreter (ESSI)
 Interprets CSS for EWEBE
'''
import curses

color_cache = {}
def _approx_color(HSV: list[int], clist: dict[int, int]) -> int:
    if color_cache.get(HSV):
        return color_cache[HSV]

    if HSV[1] <= 25 and HSV[2] >= 75:
        return clist.get(curses.COLOR_WHITE, 0)
    if HSV[2] <= 25:
        return clist.get(curses.COLOR_BLACK, 0)
    
    if HSV[1] >= 75 and HSV[2] >= 75:
        if HSV[0] < 8 or HSV[0] > 350:
            return clist.get(curses.COLOR_RED, 0)
        if 8 < HSV[0] < 67:
            return clist.get(curses.COLOR_YELLOW, 0)
        if 67 < HSV[0] < 136:
            return clist.get(curses.COLOR_GREEN, 0)
        if 136 < HSV[0] < 209:
            return clist.get(curses.COLOR_CYAN, 0)
        if 209 < HSV[0] < 270:
            return clist.get(curses.COLOR_BLUE, 0)
        if 270 < HSV[0] < 350:
            return clist.get(curses.COLOR_MAGENTA, 0)
        
    return 0

import re

def parse_hsl(css_value):
    # This regex looks for 'hsl', ignores spaces/brackets, and grabs the numbers
    # It matches: hsl(1, 2, 3), hsl( 100, 50%, 20% ), etc.
    match = re.search(r'hsl\(\s*(\d+)\s*,\s*(\d+)%?\s*,\s*(\d+)%?\s*\)', css_value)
    
    if match:
        # Convert the three found groups into integers
        h, s, l = map(int, match.groups())
        return [h, s, l]
    return None

def _interpret_inline_css(css: str, clist):
    # 1. Clean the string and split by semicolon
    declarations = [d.strip() for d in css.split(";") if ":" in d]
    styles = {"color": 0} # Default

    for decl in declarations:
        prop, val = decl.split(":", 1)
        prop = prop.strip().lower()
        val = val.strip().lower()

        if prop == "color":
            hsl_values = parse_hsl(val)
            if hsl_values:
                # Now you have [H, S, L] as clean integers
                styles["color"] = _approx_color(hsl_values, clist)
                
    return styles

def style_tag(style, clist):
    return _interpret_inline_css(style, clist)["color"]
