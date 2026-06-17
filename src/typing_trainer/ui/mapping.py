"""
ui/mapping.py — Touch-Typing Key-to-Finger Data
================================================
Pure data module: no Qt imports.  Every other UI module imports from
here so finger assignments, colours, and layout are defined in one place.
"""


# ── Finger colours ────────────────────────────────────────────────────────────
FINGER_COLORS: dict[str, str] = {
    "Left Pinky":   "#9b59b6",
    "Left Ring":    "#3498db",
    "Left Middle":  "#2ecc71",
    "Left Index":   "#e67e22",
    "Right Index":  "#f1c40f",
    "Right Middle": "#1abc9c",
    "Right Ring":   "#e74c3c",
    "Right Pinky":  "#e84393",
    "Left Thumb":   "#64b5f6",
    "Right Thumb":  "#64b5f6",
}

# ── Home key for each finger (resting position) ───────────────────────────────
HOME_KEYS: dict[str, str] = {
    "Left Pinky":   "A",
    "Left Ring":    "S",
    "Left Middle":  "D",
    "Left Index":   "F",
    "Right Index":  "J",
    "Right Middle": "K",
    "Right Ring":   "L",
    "Right Pinky":  ";",
    "Left Thumb":   "Space",
    "Right Thumb":  "Space",
}

# ── Ordered list of all finger names ──────────────────────────────────────────
FINGER_ORDER: list[str] = [
    "Left Pinky", "Left Ring", "Left Middle", "Left Index",
    "Right Index", "Right Middle", "Right Ring", "Right Pinky",
    "Left Thumb", "Right Thumb",
]

# ── Key → finger mapping (keys stored uppercase for lookup) ───────────────────
KEY_TO_FINGER: dict[str, str] = {
    # Number row
    "`": "Left Pinky",  "1": "Left Pinky",
    "2": "Left Ring",   "3": "Left Middle",
    "4": "Left Index",  "5": "Left Index",
    "6": "Right Index", "7": "Right Index",
    "8": "Right Middle","9": "Right Ring",
    "0": "Right Pinky", "-": "Right Pinky",
    "=": "Right Pinky",
    # QWERTY row
    "Q": "Left Pinky",  "W": "Left Ring",
    "E": "Left Middle", "R": "Left Index",
    "T": "Left Index",  "Y": "Right Index",
    "U": "Right Index", "I": "Right Middle",
    "O": "Right Ring",  "P": "Right Pinky",
    "[": "Right Pinky", "]": "Right Pinky",
    "\\": "Right Pinky",
    # Home row
    "A": "Left Pinky",  "S": "Left Ring",
    "D": "Left Middle", "F": "Left Index",
    "G": "Left Index",  "H": "Right Index",
    "J": "Right Index", "K": "Right Middle",
    "L": "Right Ring",  ";": "Right Pinky",
    "'": "Right Pinky",
    # Bottom row
    "Z": "Left Pinky",  "X": "Left Ring",
    "C": "Left Middle", "V": "Left Index",
    "B": "Left Index",  "N": "Right Index",
    "M": "Right Index", ",": "Right Middle",
    ".": "Right Ring",  "/": "Right Pinky",
    # Special keys
    "TAB":       "Left Pinky",
    "CAPS":      "Left Pinky",
    "LSHIFT":    "Left Pinky",
    "RSHIFT":    "Right Pinky",
    "BACKSPACE": "Right Pinky",
    "ENTER":     "Right Pinky",
    "SPACE":     "Left Thumb",
}

# ── Home-row visual highlight set ─────────────────────────────────────────────
HOME_ROW_KEYS: set[str] = {"A", "S", "D", "F", "J", "K", "L", ";"}

# ── Guide-bump keys (F and J have physical bumps on real keyboards) ───────────
GUIDE_BUMP_KEYS: set[str] = {"F", "J"}

# ── Full keyboard row layout ──────────────────────────────────────────────────
ROWS: list[list[str]] = [
    ["`","1","2","3","4","5","6","7","8","9","0","-","=","Backspace"],
    ["Tab","Q","W","E","R","T","Y","U","I","O","P","[","]","\\"],
    ["Caps","A","S","D","F","G","H","J","K","L",";","'","Enter"],
    ["LShift","Z","X","C","V","B","N","M",",",".","/","RShift"],
    ["LCtrl","LWin","LAlt","Space","RAlt","RWin","Menu","RCtrl"],
]

# ── Shift character maps ───────────────────────────────────────────────────────
SHIFT_MAP: dict[str, str] = {
    "`": "~",  "1": "!", "2": "@", "3": "#", "4": "$", "5": "%",
    "6": "^",  "7": "&", "8": "*", "9": "(", "0": ")", "-": "_",
    "=": "+",  "[": "{", "]": "}", "\\": "|", ";": ":",
    "'": '"',  ",": "<", ".": ">", "/": "?",
}
UNSHIFT_MAP: dict[str, str] = {v: k for k, v in SHIFT_MAP.items()}

# ── Finger band abbreviations for QSS property matching ──────────────────────
FINGER_BAND: dict[str, str] = {
    "Left Pinky":   "lp",
    "Left Ring":    "lr",
    "Left Middle":  "lm",
    "Left Index":   "li",
    "Right Index":  "ri",
    "Right Middle": "rm",
    "Right Ring":   "rr",
    "Right Pinky":  "rp",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_finger(char: str) -> tuple[str | None, str | None]:
    """Return (finger_name, hex_color) for a typed character, or (None, None)."""
    if not char:
        return None, None
    if char == " ":
        return "Left Thumb", FINGER_COLORS["Left Thumb"]
    upper = char.upper()
    name  = KEY_TO_FINGER.get(upper)
    if not name:
        return None, None
    return name, FINGER_COLORS.get(name)


def resolve_key_id(char: str) -> str | None:
    """
    Map a typed character to the button key_id used in ROWS.
    Returns uppercase single-char for letter/number/symbol keys,
    or a multi-char id like 'Space', 'Backspace', etc.
    """
    if not char:
        return None
    if char == " ":
        return "Space"
    upper = char.upper()
    if upper in KEY_TO_FINGER:
        return upper
    base = UNSHIFT_MAP.get(char)
    if base:
        return base.upper() if base.isalpha() else base
    return None
