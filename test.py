import numpy as np

import preprocessing
import mapsection
import oldmapsection
import time

if __name__ == '__main__':
    floor = 0
    rs_x = 3200 + 12
    rs_y = 3200 + 131
    print(rs_x)
    print(rs_y)
    newmap_section = mapsection.MapSection.create_map_section(0, rs_x-50, rs_x+50, rs_y-50, rs_y+50)
    newmap_section.color_tiles([(rs_x, rs_y)], (255, 0, 255, 255))
    st = time.time()
    for i in range(128):
        for j in range(128):
            surge_range = newmap_section.walk_range(rs_x, rs_y)
    et = time.time()
    print(et - st)
    escape_range = newmap_section.escape_range(rs_x, rs_y, 0)
    print(surge_range)
    print(escape_range)
    tiles, directions = newmap_section.bd_range(rs_x, rs_y)
    print(tiles)
    newmap_section.arrow_tiles(tiles, directions)
    newmap_section.image.show()

