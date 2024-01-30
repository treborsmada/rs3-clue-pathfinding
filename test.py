import numpy as np

import preprocessing
from mapsection import *
import newmap

if __name__ == '__main__':
    floor = 0
    x = 108
    y = 42
    rs_x = 38*64 + x
    rs_y = 51*64 + y
    name = "WestArdy"
    map_section = create_map_section(name)
    map_section.create_image()
    map_section.color_tiles([(x, y)], (255, 0, 255, 255))
    newmap_section = newmap.MapSection.create_map_section(0, 2500, 2550, 3290, 3340)
    newmap_section.image.show()
    print(newmap_section.move_data)
    move_data = np.fromfile("MapData/Map/collision-3-5-0.bin", dtype=np.uint8)
    print(move_data.shape)
    move_data = move_data.reshape((640, 640), order='F')
    print(bin(move_data[rs_x % 640][rs_y % 640]))
    bd_data_array = np.load("MapData/BD/bd-3-5-0.npy")
    se_data_array = np.load("MapData/SE/se-3-5-0.npy")
    process = preprocessing.ProcessData(floor)
    surge_offset = int(se_data_array[rs_x % 640][rs_y % 640][0]) & 15
    escape_offset = int(se_data_array[rs_x % 640][rs_y % 640][4]) >> 4
    print(surge_offset)
    print(escape_offset)
    bd_data = 0
    for i in range(7):
        bd_data += int(bd_data_array[rs_x % 640][rs_y % 640][i]) * ((2 ** 64) ** i)
    # tiles = []
    # for i in range(21):
    #     for j in range(21):
    #         if bd_data & (2 ** (j + i * 21)):
    #             u = x - 10 + j
    #             v = y - 10 + i
    #             tiles.append((u, v))
    # directions = []
    # for tile in tiles:
    #     x_diff = tile[0] - x
    #     y_diff = tile[1] - y
    #     if x_diff == 0:
    #         if y_diff > 0:
    #             directions.append(0)
    #         else:
    #             directions.append(4)
    #     elif y_diff == 0:
    #         if x_diff > 0:
    #             directions.append(2)
    #         else:
    #             directions.append(6)
    #     elif (abs(x_diff) + 0.5) / (abs(y_diff) + 0.5) > 7.5 / 3.5:
    #         if x_diff > 0:
    #             directions.append(2)
    #         else:
    #             directions.append(6)
    #     elif (abs(y_diff) + 0.5) / (abs(x_diff) + 0.5) > 7.5 / 3.5:
    #         if y_diff > 0:
    #             directions.append(0)
    #         else:
    #             directions.append(4)
    #     elif x_diff > 0:
    #         if y_diff > 0:
    #             directions.append(1)
    #         else:
    #             directions.append(3)
    #     elif x_diff < 0:
    #         if y_diff > 0:
    #             directions.append(7)
    #         else:
    #             directions.append(5)
    # map_section.arrow_tiles(tiles, directions)
    # map_section.image.show()
