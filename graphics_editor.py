"""
=============================================================================
  2D Graphics Editor  —  Python / Windows Console Edition
  Canvas: 78 x 38 characters  |  Palette: * (outline)  _ (base)
  Shapes: Circle · Rectangle · Line · Triangle
  Operations: Add · Delete · Modify · Clear · Save
  Controls: A / D / M / C / S / V / Q  (or arrow-keys in sub-menus)
=============================================================================
"""

import sys, os, math, msvcrt, ctypes, ctypes.wintypes

# ── Windows Console API structs ───────────────────────────────────────────
kernel32 = ctypes.windll.kernel32
STD_OUTPUT_HANDLE = ctypes.c_ulong(-11)
hOut = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

class COORD(ctypes.Structure):
    _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]

class SMALL_RECT(ctypes.Structure):
    _fields_ = [("Left",ctypes.c_short),("Top",ctypes.c_short),
                ("Right",ctypes.c_short),("Bottom",ctypes.c_short)]

class CONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):
    _fields_ = [("dwSize", COORD),("dwCursorPosition", COORD),
                ("wAttributes",ctypes.c_ushort),("srWindow",SMALL_RECT),
                ("dwMaximumWindowSize",COORD)]

class CONSOLE_CURSOR_INFO(ctypes.Structure):
    _fields_ = [("dwSize",ctypes.c_ulong),("bVisible",ctypes.c_bool)]

# ── Colour constants ──────────────────────────────────────────────────────
FG_BLACK=0; FG_BLUE=1; FG_GREEN=2; FG_CYAN=3; FG_RED=4
FG_MAGENTA=5; FG_YELLOW=6; FG_WHITE=7; BRIGHT=8
BG_BLUE=0x10; BG_GREEN=0x20; BG_RED=0x40; BG_WHITE=0x70; BG_BRIGHT=0x80

COL_NORMAL  = FG_WHITE
COL_BRIGHT  = FG_WHITE | BRIGHT
COL_CYAN    = FG_CYAN  | BRIGHT
COL_YELLOW  = FG_YELLOW| BRIGHT
COL_GREEN   = FG_GREEN | BRIGHT
COL_RED     = FG_RED   | BRIGHT
COL_MAGENTA = FG_MAGENTA|BRIGHT
COL_BLUE    = FG_BLUE  | BRIGHT
COL_MENU_HL = BG_BLUE | BG_BRIGHT | FG_WHITE | BRIGHT

# ── Canvas dimensions ─────────────────────────────────────────────────────
CANVAS_W = 78
CANVAS_H = 38
MAX_OBJ  = 64
CH_OUTLINE = '*'
CH_BASE    = '_'
CH_EMPTY   = ' '

# ── Console helpers ───────────────────────────────────────────────────────
def set_color(attr):
    kernel32.SetConsoleTextAttribute(hOut, attr)

def move_to(col, row):
    kernel32.SetConsoleCursorPosition(hOut, COORD(col, row))

def hide_cursor():
    ci = CONSOLE_CURSOR_INFO(1, False)
    kernel32.SetConsoleCursorInfo(hOut, ctypes.byref(ci))

def show_cursor():
    ci = CONSOLE_CURSOR_INFO(10, True)
    kernel32.SetConsoleCursorInfo(hOut, ctypes.byref(ci))

def set_console_size(w, h):
    size   = COORD(w, h)
    rect   = SMALL_RECT(0, 0, w-1, h-1)
    kernel32.SetConsoleScreenBufferSize(hOut, size)
    kernel32.SetConsoleWindowInfo(hOut, True, ctypes.byref(rect))

def clear_screen():
    csbi = CONSOLE_SCREEN_BUFFER_INFO()
    kernel32.GetConsoleScreenBufferInfo(hOut, ctypes.byref(csbi))
    cells = csbi.dwSize.X * csbi.dwSize.Y
    home  = COORD(0, 0)
    written = ctypes.c_ulong(0)
    kernel32.FillConsoleOutputCharacterA(hOut, ord(' '), cells, home, ctypes.byref(written))
    kernel32.FillConsoleOutputAttribute(hOut, csbi.wAttributes, cells, home, ctypes.byref(written))
    kernel32.SetConsoleCursorPosition(hOut, home)

def write(text, col=None, row=None):
    """Print text at optional position."""
    if col is not None and row is not None:
        move_to(col, row)
    sys.stdout.write(text)
    sys.stdout.flush()

def getch():
    """Read a single keypress; returns (is_special, code)."""
    ch = msvcrt.getch()
    if ch in (b'\x00', b'\xe0'):
        ch2 = msvcrt.getch()
        return (True, ch2[0])   # special key
    return (False, ch[0])

def read_int(prompt, lo, hi, row):
    """Read an integer in [lo..hi] from the user at given row."""
    show_cursor()
    while True:
        move_to(2, row)
        set_color(COL_YELLOW)
        sys.stdout.write(f"  {prompt} [{lo}-{hi}]: ")
        sys.stdout.flush()
        set_color(COL_BRIGHT)
        try:
            line = input()
            val  = int(line.strip())
            if lo <= val <= hi:
                hide_cursor()
                return val
        except (ValueError, EOFError):
            pass
        set_color(COL_RED)
        move_to(2, row+1)
        sys.stdout.write("  Value out of range, try again.   ")
        sys.stdout.flush()

def clear_rows(start_row, count=10):
    for r in range(start_row, start_row+count):
        move_to(0, r)
        sys.stdout.write(" " * 110)
    sys.stdout.flush()

# ── Canvas ────────────────────────────────────────────────────────────────
canvas = [[CH_EMPTY]*CANVAS_W for _ in range(CANVAS_H)]

def canvas_clear():
    for r in range(CANVAS_H):
        for c in range(CANVAS_W):
            canvas[r][c] = CH_EMPTY

def canvas_put(x, y, ch):
    if 0 <= x < CANVAS_W and 0 <= y < CANVAS_H:
        canvas[y][x] = ch

# ═══════════════════════════════════════════════════════════════════════════
#  Drawing functions
# ═══════════════════════════════════════════════════════════════════════════

def draw_line(x1, y1, x2, y2):
    """Bresenham's line algorithm."""
    dx, dy = abs(x2-x1), abs(y2-y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy
    while True:
        canvas_put(x1, y1, CH_OUTLINE)
        if x1 == x2 and y1 == y2:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy;  x1 += sx
        if e2 <  dx:
            err += dx;  y1 += sy

def draw_rect(x, y, w, h):
    """Rectangle: * sides, _ top/bottom."""
    for i in range(w):
        canvas_put(x+i, y,     CH_BASE)
        canvas_put(x+i, y+h-1, CH_BASE)
    for j in range(1, h-1):
        canvas_put(x,     y+j, CH_OUTLINE)
        canvas_put(x+w-1, y+j, CH_OUTLINE)
    # corners
    for cx, cy in [(x,y),(x+w-1,y),(x,y+h-1),(x+w-1,y+h-1)]:
        canvas_put(cx, cy, CH_OUTLINE)

def draw_circle(cx, cy, r):
    """Midpoint (Bresenham) circle algorithm."""
    x, y, d = 0, r, 1 - r
    while x <= y:
        for px, py in [( cx+x,cy+y),(cx-x,cy+y),(cx+x,cy-y),(cx-x,cy-y),
                        (cx+y,cy+x),(cx-y,cy+x),(cx+y,cy-x),(cx-y,cy-x)]:
            canvas_put(px, py, CH_OUTLINE)
        if d < 0:
            d += 2*x + 3
        else:
            d += 2*(x-y) + 5;  y -= 1
        x += 1

def draw_triangle(x1,y1,x2,y2,x3,y3):
    """Three Bresenham lines; bottom row gets _ chars."""
    draw_line(x1,y1,x2,y2)
    draw_line(x2,y2,x3,y3)
    draw_line(x3,y3,x1,y1)
    max_y = max(y1, y2, y3)
    for c in range(CANVAS_W):
        if canvas[max_y][c] == CH_OUTLINE:
            canvas[max_y][c] = CH_BASE

# ═══════════════════════════════════════════════════════════════════════════
#  Object list
# ═══════════════════════════════════════════════════════════════════════════
CIRCLE   = 'Circle'
RECT     = 'Rectangle'
LINE     = 'Line'
TRIANGLE = 'Triangle'

objects = []   # list of dicts: {type, params, label}

def rebuild_canvas():
    canvas_clear()
    for obj in objects:
        t, p = obj['type'], obj['params']
        if   t == CIRCLE:   draw_circle  (p[0],p[1],p[2])
        elif t == RECT:     draw_rect    (p[0],p[1],p[2],p[3])
        elif t == LINE:     draw_line    (p[0],p[1],p[2],p[3])
        elif t == TRIANGLE: draw_triangle(p[0],p[1],p[2],p[3],p[4],p[5])

# ═══════════════════════════════════════════════════════════════════════════
#  Display
# ═══════════════════════════════════════════════════════════════════════════
CANVAS_COL = 1
CANVAS_ROW = 2
PANEL_COL  = 81
PANEL_ROW  = 2
INPUT_ROW  = 43

def display_canvas():
    # Top border
    set_color(COL_CYAN)
    move_to(CANVAS_COL-1, CANVAS_ROW-1)
    sys.stdout.write('+' + '-'*CANVAS_W + '+')
    # Rows
    for r in range(CANVAS_H):
        move_to(CANVAS_COL-1, CANVAS_ROW+r)
        set_color(COL_CYAN)
        sys.stdout.write('|')
        for c in range(CANVAS_W):
            ch = canvas[r][c]
            if   ch == CH_OUTLINE: set_color(COL_YELLOW)
            elif ch == CH_BASE:    set_color(COL_GREEN)
            else:                  set_color(COL_NORMAL)
            sys.stdout.write(ch)
        set_color(COL_CYAN)
        sys.stdout.write('|')
    # Bottom border
    move_to(CANVAS_COL-1, CANVAS_ROW+CANVAS_H)
    sys.stdout.write('+' + '-'*CANVAS_W + '+')
    sys.stdout.flush()

def display_object_list():
    set_color(COL_MAGENTA)
    move_to(PANEL_COL, PANEL_ROW)
    sys.stdout.write('+----- Object List -----+')
    for i, obj in enumerate(objects[:12]):
        move_to(PANEL_COL, PANEL_ROW+1+i)
        set_color(COL_BRIGHT)
        lbl = obj['label'][:8].ljust(8)
        typ = obj['type'][:8].ljust(8)
        sys.stdout.write(f'| {i:2d}. {typ} {lbl} |')
    for j in range(len(objects[:12]), 12):
        move_to(PANEL_COL, PANEL_ROW+1+j)
        set_color(COL_NORMAL)
        sys.stdout.write('|                        |')
    move_to(PANEL_COL, PANEL_ROW+13)
    set_color(COL_MAGENTA)
    sys.stdout.write('+------------------------+')
    if len(objects) > 12:
        move_to(PANEL_COL, PANEL_ROW+14)
        set_color(COL_CYAN)
        sys.stdout.write(f'  ...+{len(objects)-12} more')
    sys.stdout.flush()

def display_status():
    set_color(COL_BLUE | BRIGHT)
    move_to(0, 0)
    sys.stdout.write(f'  2D Graphics Editor   [*=outline] [_=base]   Objects: {len(objects)}/{MAX_OBJ}   ')
    move_to(0, CANVAS_ROW+CANVAS_H+1)
    set_color(COL_CYAN)
    sys.stdout.write('  A)dd   D)elete   M)odify   C)lear   S)ave   V)iew   Q)uit  ')
    set_color(COL_NORMAL)
    sys.stdout.flush()

def full_refresh():
    rebuild_canvas()
    display_canvas()
    display_object_list()
    display_status()

# ═══════════════════════════════════════════════════════════════════════════
#  Menu helper
# ═══════════════════════════════════════════════════════════════════════════
def show_menu(title, items, col, row):
    """Arrow-key navigable menu. Returns selected index or -1 on ESC."""
    sel = 0
    hide_cursor()
    while True:
        set_color(COL_CYAN)
        move_to(col, row)
        sys.stdout.write(f'+== {title} ==+')
        for i, item in enumerate(items):
            move_to(col, row+1+i)
            if i == sel:
                set_color(COL_MENU_HL)
            else:
                set_color(COL_NORMAL)
            sys.stdout.write(f'  {item:<26}  ')
        move_to(col, row+1+len(items))
        set_color(COL_CYAN)
        sys.stdout.write('  [UP/DOWN+ENTER or 1-{}]  '.format(len(items)))
        sys.stdout.flush()

        special, code = getch()
        if special:
            if code == 72 and sel > 0:            sel -= 1   # UP
            elif code == 80 and sel < len(items)-1: sel += 1 # DOWN
        else:
            if code == 13:                return sel          # ENTER
            if code == 27:                return -1           # ESC
            if ord('1') <= code <= ord('0')+len(items):
                return code - ord('1')

# ═══════════════════════════════════════════════════════════════════════════
#  Shape input helpers
# ═══════════════════════════════════════════════════════════════════════════
def _label_for(t):
    prefix = {'Circle':'C','Rectangle':'R','Line':'L','Triangle':'T'}
    count  = sum(1 for o in objects if o['type'] == t)
    return f"{prefix.get(t,'X')}{count}"

def input_circle():
    move_to(2, INPUT_ROW-1); set_color(COL_YELLOW)
    sys.stdout.write(f'  Draw CIRCLE on canvas ({CANVAS_W}x{CANVAS_H}):')
    cx = read_int('Center X', 0, CANVAS_W-1, INPUT_ROW)
    cy = read_int('Center Y', 0, CANVAS_H-1, INPUT_ROW+2)
    r  = read_int('Radius  ', 1, 18,          INPUT_ROW+4)
    return {'type':CIRCLE,'params':[cx,cy,r],'label':_label_for(CIRCLE)}

def input_rect():
    move_to(2, INPUT_ROW-1); set_color(COL_YELLOW)
    sys.stdout.write(f'  Draw RECTANGLE on canvas ({CANVAS_W}x{CANVAS_H}):')
    x = read_int('Top-Left X', 0, CANVAS_W-2, INPUT_ROW)
    y = read_int('Top-Left Y', 0, CANVAS_H-2, INPUT_ROW+2)
    w = read_int('Width     ', 2, CANVAS_W-x,  INPUT_ROW+4)
    h = read_int('Height    ', 2, CANVAS_H-y,  INPUT_ROW+6)
    return {'type':RECT,'params':[x,y,w,h],'label':_label_for(RECT)}

def input_line():
    move_to(2, INPUT_ROW-1); set_color(COL_YELLOW)
    sys.stdout.write(f'  Draw LINE on canvas ({CANVAS_W}x{CANVAS_H}):')
    x1 = read_int('Start X', 0, CANVAS_W-1, INPUT_ROW)
    y1 = read_int('Start Y', 0, CANVAS_H-1, INPUT_ROW+2)
    x2 = read_int('End X  ', 0, CANVAS_W-1, INPUT_ROW+4)
    y2 = read_int('End Y  ', 0, CANVAS_H-1, INPUT_ROW+6)
    return {'type':LINE,'params':[x1,y1,x2,y2],'label':_label_for(LINE)}

def input_triangle():
    move_to(2, INPUT_ROW-1); set_color(COL_YELLOW)
    sys.stdout.write(f'  Draw TRIANGLE on canvas ({CANVAS_W}x{CANVAS_H}):')
    x1 = read_int('Point-1 X', 0, CANVAS_W-1, INPUT_ROW)
    y1 = read_int('Point-1 Y', 0, CANVAS_H-1, INPUT_ROW+2)
    x2 = read_int('Point-2 X', 0, CANVAS_W-1, INPUT_ROW+4)
    y2 = read_int('Point-2 Y', 0, CANVAS_H-1, INPUT_ROW+6)
    x3 = read_int('Point-3 X', 0, CANVAS_W-1, INPUT_ROW+8)
    y3 = read_int('Point-3 Y', 0, CANVAS_H-1, INPUT_ROW+10)
    return {'type':TRIANGLE,'params':[x1,y1,x2,y2,x3,y3],'label':_label_for(TRIANGLE)}

# ═══════════════════════════════════════════════════════════════════════════
#  Actions
# ═══════════════════════════════════════════════════════════════════════════
def action_add():
    if len(objects) >= MAX_OBJ:
        set_color(COL_RED); move_to(2,INPUT_ROW)
        sys.stdout.write(f'  Canvas full ({MAX_OBJ} objects). Delete some first.')
        sys.stdout.flush(); msvcrt.getch(); return

    items = ['1. Circle     (midpoint algorithm)',
             '2. Rectangle  (outline with */_ )',
             '3. Line       (Bresenham)',
             '4. Triangle   (3 vertices)      ']
    choice = show_menu(' Add Shape ', items, 2, INPUT_ROW-1)
    clear_rows(INPUT_ROW-1)

    obj = None
    if   choice == 0: obj = input_circle()
    elif choice == 1: obj = input_rect()
    elif choice == 2: obj = input_line()
    elif choice == 3: obj = input_triangle()

    clear_rows(INPUT_ROW-1, 14)
    if obj:
        objects.append(obj)
    full_refresh()

def action_delete():
    if not objects:
        set_color(COL_RED); move_to(2,INPUT_ROW)
        sys.stdout.write('  No objects to delete.'); sys.stdout.flush()
        msvcrt.getch(); return

    show_cursor()
    move_to(2,INPUT_ROW); set_color(COL_YELLOW)
    sys.stdout.write('  Delete object index (see list on right, ESC=cancel): ')
    set_color(COL_BRIGHT); sys.stdout.flush()
    try:
        idx = int(input().strip())
        if 0 <= idx < len(objects):
            del objects[idx]
            move_to(2,INPUT_ROW+1); set_color(COL_GREEN)
            sys.stdout.write(f'  Object {idx} deleted.'); sys.stdout.flush()
            import time; time.sleep(0.5)
        else:
            move_to(2,INPUT_ROW+1); set_color(COL_RED)
            sys.stdout.write('  Index out of range.'); sys.stdout.flush()
            import time; time.sleep(0.8)
    except (ValueError, EOFError):
        pass
    clear_rows(INPUT_ROW, 3)
    full_refresh()

def action_modify():
    if not objects:
        set_color(COL_RED); move_to(2,INPUT_ROW)
        sys.stdout.write('  No objects to modify.'); sys.stdout.flush()
        msvcrt.getch(); return

    show_cursor()
    move_to(2,INPUT_ROW); set_color(COL_YELLOW)
    sys.stdout.write('  Modify object index: ')
    set_color(COL_BRIGHT); sys.stdout.flush()
    try:
        idx = int(input().strip())
        if not (0 <= idx < len(objects)):
            raise ValueError
    except (ValueError, EOFError):
        clear_rows(INPUT_ROW, 3); full_refresh(); return

    old_type  = objects[idx]['type']
    old_label = objects[idx]['label']
    clear_rows(INPUT_ROW-1, 14)

    input_fn = {CIRCLE:input_circle, RECT:input_rect,
                LINE:input_line,     TRIANGLE:input_triangle}[old_type]
    new_obj = input_fn()
    clear_rows(INPUT_ROW-1, 14)
    if new_obj:
        new_obj['label'] = old_label   # keep same label
        objects[idx] = new_obj
    full_refresh()

def action_clear():
    move_to(2,INPUT_ROW); set_color(COL_RED)
    sys.stdout.write('  Clear ALL objects? [Y/N]: ')
    sys.stdout.flush(); show_cursor()
    ch = msvcrt.getch()
    if ch.lower() == b'y':
        objects.clear()
    clear_rows(INPUT_ROW, 2)
    full_refresh()

def action_save():
    fname = 'picture.txt'
    try:
        with open(fname, 'w') as f:
            for row in canvas:
                f.write(''.join(row) + '\n')
        move_to(2,INPUT_ROW); set_color(COL_GREEN)
        sys.stdout.write(f'  Canvas saved to {fname}')
    except Exception as e:
        move_to(2,INPUT_ROW); set_color(COL_RED)
        sys.stdout.write(f'  Error: {e}')
    sys.stdout.flush()
    import time; time.sleep(1)
    clear_rows(INPUT_ROW, 2)

# ═══════════════════════════════════════════════════════════════════════════
#  Splash screen
# ═══════════════════════════════════════════════════════════════════════════
def splash():
    clear_screen()
    lines = [
        (10, 8,  COL_CYAN,    "  ╔══════════════════════════════════════════╗"),
        (10, 9,  COL_CYAN,    "  ║      2 D   G r a p h i c s   E d i t o r  ║"),
        (10, 10, COL_CYAN,    "  ╚══════════════════════════════════════════╝"),
        (10, 12, COL_YELLOW,  "   Canvas : 78 × 38 characters"),
        (10, 13, COL_GREEN,   "   *  →  shape outline   (Bresenham / midpoint)"),
        (10, 14, COL_GREEN,   "   _  →  base / bottom edges"),
        (10, 16, COL_MAGENTA, "   Shapes : Circle · Rectangle · Line · Triangle"),
        (10, 17, COL_CYAN,    "   Ops    : Add · Delete · Modify · Clear · Save"),
        (10, 19, COL_BRIGHT,  "   Press any key to start …"),
    ]
    for col, row, color, text in lines:
        set_color(color)
        move_to(col, row)
        sys.stdout.write(text)
    sys.stdout.flush()
    getch()
    clear_screen()

# ═══════════════════════════════════════════════════════════════════════════
#  Main loop
# ═══════════════════════════════════════════════════════════════════════════
KEY_MAP = {
    ord('a'): action_add,    ord('A'): action_add,
    ord('d'): action_delete, ord('D'): action_delete,
    ord('m'): action_modify, ord('M'): action_modify,
    ord('c'): action_clear,  ord('C'): action_clear,
    ord('s'): action_save,   ord('S'): action_save,
    ord('v'): full_refresh,  ord('V'): full_refresh,
}

def main():
    # Resize console
    set_console_size(112, 58)
    kernel32.SetConsoleTitleW("2D Graphics Editor  [ * and _ ]")
    hide_cursor()

    splash()
    full_refresh()

    while True:
        hide_cursor()
        special, code = getch()
        if special:
            continue
        if code in (ord('q'), ord('Q')):
            clear_screen()
            set_color(COL_CYAN)
            move_to(10, 5)
            sys.stdout.write("  2D Graphics Editor — Goodbye!\n\n")
            set_color(COL_NORMAL)
            show_cursor()
            break
        fn = KEY_MAP.get(code)
        if fn:
            fn()
        else:
            move_to(2, INPUT_ROW)
            set_color(COL_NORMAL)
            sys.stdout.write("  Keys:  A=Add  D=Delete  M=Modify  C=Clear  S=Save  V=Refresh  Q=Quit  ")
            sys.stdout.flush()
            import time; time.sleep(1.2)
            clear_rows(INPUT_ROW, 1)

if __name__ == '__main__':
    main()
