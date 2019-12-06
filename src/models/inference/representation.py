class Point:
    """
    Data model used for storing the point in coordinate space

    Arguments:
        x (int): x coordinate
        y (int): y coordinate
    """

    def __init__(self, x, y):
        self._y = y
        self._x = x

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    def __eq__(self, other):
        return self.x == other.x and \
            self.y == other.y


class BoundingBox:
    """
    Data model used for storing bounding box

    Arguments:
        top_left (Point): Top left point of the bounding box
        bottom_right (Point): Bottom right point of the bounding box

    """

    def __init__(self, top_left: Point, bottom_right: Point):
        self._bottom_right = bottom_right
        self._top_left = top_left

    @property
    def bottom_right(self):
        return self._bottom_right

    @property
    def top_left(self):
        return self._top_left

    def __eq__(self, other):
        return self.bottom_right == other.bottom_right and \
            self.top_left == other.top_left
