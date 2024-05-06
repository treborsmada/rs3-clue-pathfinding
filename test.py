import numpy as np

import preprocessing
import mapsection
import oldmapsection
import time

if __name__ == '__main__':
    floor = 0
    rs_x = 3200 + 20
    rs_y = 3200 + 131
    print(rs_x)
    print(rs_y)
    newmap_section = mapsection.MapSection.create_map_section(0, rs_x-50, rs_x+50, rs_y-50, rs_y+50)
    newmap_section.color_tiles([(rs_x, rs_y)], (255, 0, 255, 255))
    tiles = newmap_section.escape_range(rs_x, rs_y, 0)
    print(tiles)
    arr = np.load("MapData/SE/se-5-6-0.npy")
    print("{0:b}".format(arr[112, 75, 3]))
    newmap_section.arrow_tiles([tiles], [0])
    newmap_section.image.show()

