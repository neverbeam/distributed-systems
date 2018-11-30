"""
Author: Kevin Rojer & Ali Almoshawah
Version: 1.0
Date: 30 November 2018
"""

class Arena:

    def __init__(self, width, height):
        self.width = width
        self.height = height

def draw_grid(graph, width=2):
    for y in range(graph.height):
        for x in range(graph.width):
             print("%%-%ds" % width % '.', end="")
        print()

def main():
    g = Arena(25,25)
    draw_grid(g)

if __name__ == '__main__':
    main()
