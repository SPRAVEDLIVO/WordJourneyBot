from dataclasses import dataclass

@dataclass
class Rect:
    __slots__ = "x", "y", "x2", "y2", "w", "h", "x1", "y1", "left", "right", "top", "bottom"
    x: int
    y: int
    x2: int
    y2: int

    def __init__(self, x=0, y=0, x2=0, y2=0) -> None:
        if hasattr(x, "width") and hasattr(x, "left"): # pyautogui rect
            self.x = x.left
            self.y = x.top
            self.x2 = x.left+x.width
            self.y2 = x.top+x.height
            x = self.x
        else:
            self.x = x
            self.y = y
            self.x2 = x2
            self.y2 = y2
        self.w = abs(x2 - x)
        self.h = abs(y2 - y)

        self.define_property("x1", "x")
        self.define_property("y1", "y")
        self.define_property("left", "x")
        self.define_property("right", "x2")
        self.define_property("top", "y")
        self.define_property("bottom", "y2")

    def define_property(self, name, proxy):
        setattr(type(self), name, property(lambda self: getattr(self, proxy), lambda self, value: setattr(self, proxy, value)))

    def to_pyautogui(self):
        return self.x, self.y, self.w, self.h

    def __add__(self, other):
        return Rect(self.x + other.x, self.y + other.y, self.x2 + other.x2, self.y2+self.y2)
    
    def __iter__(self):
        return (self.x, self.y, self.x2, self.y2).__iter__()

    def __getitem__(self, x):
        return list(self)[x]