class Point(object):
    def __init__(self,x,y):
        self.x=x
        self.y=y

class Box(object):
    def __init__(self,p1,p2):

        self.left=min(p1.x, p2.x)
        self.right=max(p1.x, p2.x)
        self.bottom=min(p1.y, p2.y)
        self.top=max(p1.y, p2.y)

def is_intersecting(r1,r2):
     return range_overlap(r1.left, r1.right, r2.left, r2.right) and range_overlap(r1.bottom, r1.top, r2.bottom, r2.top)


def range_overlap(a_min, a_max, b_min, b_max):
    return (a_min <= b_max) and (b_min <= a_max)