import pygame as pg


class MouseButtons:
    """Maps names to mouse_button IDs"""

    left = 1
    right = 3
    middle = 2


class MouseButtonStates:
    """Namespace for storing the current mouse button states"""

    left = False
    right = False
    middle = False

    @property
    def any(self):
        """bool: if any mouse buttons are pressed"""
        return self.left or self.right or self.middle

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "<MouseButtonStates left={} right={} middle={}>".format(
            self.left, self.right, self.middle
        )


class KeyModifiers:
    """Namespace for storing key modifiers"""

    shift = False
    ctrl = False
    alt = False

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "<KeyModifiers shift={} ctrl={} alt={}>".format(
            self.shift, self.ctrl, self.alt
        )


class Keys:
    """Namespace for mapping key constants"""

    ACTION_PRESS = pg.KEYDOWN
    ACTION_RELEASE = pg.KEYUP

    ESCAPE = pg.K_ESCAPE
    SPACE = pg.K_SPACE
    ENTER = pg.K_RETURN
    PAGE_UP = pg.K_PAGEUP
    PAGE_DOWN = pg.K_PAGEDOWN
    LEFT = pg.K_LEFT
    RIGHT = pg.K_RIGHT
    UP = pg.K_UP
    DOWN = pg.K_DOWN

    TAB = pg.K_TAB
    COMMA = pg.K_COMMA
    MINUS = pg.K_MINUS
    PERIOD = pg.K_PERIOD
    SLASH = pg.K_SLASH
    SEMICOLON = pg.K_SEMICOLON
    EQUAL = pg.K_EQUALS
    LEFT_BRACKET = pg.K_LEFTBRACKET
    RIGHT_BRACKET = pg.K_RIGHTBRACKET
    BACKSLASH = pg.K_BACKSLASH
    BACKSPACE = pg.K_BACKSPACE
    INSERT = pg.K_INSERT
    DELETE = pg.K_DELETE
    HOME = pg.K_HOME
    END = pg.K_END
    CAPS_LOCK = pg.K_CAPSLOCK

    F1 = pg.K_F1
    F2 = pg.K_F2
    F3 = pg.K_F3
    F4 = pg.K_F4
    F5 = pg.K_F5
    F6 = pg.K_F6
    F7 = pg.K_F7
    F8 = pg.K_F8
    F9 = pg.K_F9
    F10 = pg.K_F10
    F11 = pg.K_F11
    F12 = pg.K_F12

    NUMBER_0 = pg.K_0
    NUMBER_1 = pg.K_1
    NUMBER_2 = pg.K_2
    NUMBER_3 = pg.K_3
    NUMBER_4 = pg.K_4
    NUMBER_5 = pg.K_5
    NUMBER_6 = pg.K_6
    NUMBER_7 = pg.K_7
    NUMBER_8 = pg.K_8
    NUMBER_9 = pg.K_9

    NUMPAD_0 = pg.K_KP_0
    NUMPAD_1 = pg.K_KP_1
    NUMPAD_2 = pg.K_KP_2
    NUMPAD_3 = pg.K_KP_3
    NUMPAD_4 = pg.K_KP_4
    NUMPAD_5 = pg.K_KP_5
    NUMPAD_6 = pg.K_KP_6
    NUMPAD_7 = pg.K_KP_7
    NUMPAD_8 = pg.K_KP_8
    NUMPAD_9 = pg.K_KP_9
    NUMPAD_ENTER = pg.K_KP_ENTER

    A = pg.K_a
    B = pg.K_b
    C = pg.K_c
    D = pg.K_d
    E = pg.K_e
    F = pg.K_f
    G = pg.K_g
    H = pg.K_h
    I = pg.K_i
    J = pg.K_j
    K = pg.K_k
    L = pg.K_l
    M = pg.K_m
    N = pg.K_n
    O = pg.K_o
    P = pg.K_p
    Q = pg.K_q
    R = pg.K_r
    S = pg.K_s
    T = pg.K_t
    U = pg.K_u
    V = pg.K_v
    W = pg.K_w
    X = pg.K_x
    Y = pg.K_y
    Z = pg.K_z
