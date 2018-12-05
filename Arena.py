"""
Author: Kevin Rojer & Ali Almoshawah
Version: 1.0
Date: 30 November 2018
"""

class Arena:

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def draw_grid(self):
        for y in range(self.height):
            for x in range(self.width):
                 #("%%-%ds" % 2 % '.', end="")
                 print("{}{}".format(".", 2 * " " ), end="")
            print()


if __name__ == '__main__':
    g = Arena(25,25)
    g.draw_grid()
