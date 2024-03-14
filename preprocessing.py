import numpy as np
import zlib
import time
from helper import (free_direction,
                    adj_positions,
                    direction_offset)

"""
rs map dimensions
"""

RS_HEIGHT = 12800
RS_LENGTH = 6400


class ProcessData:
    def __init__(self, f: int):
        self.movement_data = dict()
        self.bd_data = dict()
        self.floor = f

    def bd_range(self, x: int, y: int) -> list:
        tiles = set()
        self.bd_range_recursion(x, y, 1, 2, 0, tiles, 0, 0)
        self.bd_range_recursion(x, y, 3, 2, 4, tiles, 0, 0)
        self.bd_range_recursion(x, y, 5, 6, 4, tiles, 0, 0)
        self.bd_range_recursion(x, y, 7, 6, 0, tiles, 0, 0)
        return [*tiles]

    def bd_range_recursion(self, x: int, y: int, direction: int, horizontal: int, vertical: int, tiles: set,
                           dist_x: int, dist_y: int):
        if dist_x > 0 or dist_y > 0:
            tiles.add((x, y))
        curr_move = self.get_movement_data(x, y)
        if dist_x < 10 and dist_y < 10 and free_direction(curr_move, direction):
            new_tile = adj_positions(x, y)[direction]
            self.bd_range_recursion(new_tile[0], new_tile[1], direction, horizontal, vertical, tiles, dist_x + 1,
                                    dist_y + 1)
        elif dist_x < 10 and free_direction(curr_move, horizontal):
            new_tile = adj_positions(x, y)[horizontal]
            self.bd_range_recursion(new_tile[0], new_tile[1], direction, horizontal, vertical, tiles, dist_x + 1,
                                    dist_y)
            dist_x = 10
        elif dist_y < 10 and free_direction(curr_move, vertical):
            new_tile = adj_positions(x, y)[vertical]
            self.bd_range_recursion(new_tile[0], new_tile[1], direction, horizontal, vertical, tiles, dist_x,
                                    dist_y + 1)
            dist_y = 10
        dist = [dist_x, dist_y]
        for i, direction in enumerate([horizontal, vertical]):
            d = dist[i]
            curr_tile = (x, y)
            curr_move = self.get_movement_data(x, y)
            while d < 10 and free_direction(curr_move, direction):
                curr_tile = adj_positions(curr_tile[0], curr_tile[1])[direction]
                curr_move = self.get_movement_data(curr_tile[0], curr_tile[1])
                tiles.add(curr_tile)
                d += 1

    def process_bd_data(self, x: int, y: int):
        bd_data = 0
        bd = self.bd_range(x, y)
        for tile in bd:
            u = x - 10
            v = y - 10
            tile_x = tile[0]
            tile_y = tile[1]
            if 0 <= tile_x < RS_LENGTH and 0 <= tile_y < RS_HEIGHT:
                bd_data += 2 ** (tile_x - u + (tile_y - v) * 21)
        return bd_data

    def get_movement_data(self, x: int, y: int):
        chunk_size = 1280
        chunk = (x // chunk_size, y // chunk_size)
        if chunk in self.movement_data:
            return self.movement_data[chunk][x % chunk_size, y % chunk_size]
        elif 0 <= x < RS_LENGTH and 0 <= y < RS_HEIGHT:
            data = np.load("MapData/Map/move-" + str(chunk[0]) + "-" + str(chunk[1]) + "-" + str(self.floor) + ".npy")
            self.movement_data[chunk] = data
            return data[x % chunk_size, y % chunk_size]
        else:
            return 0

    def build_bd_array(self, chunk_x: int, chunk_y: int):
        bd_array = np.zeros(shape=(409600, 7), dtype=np.uint64)
        start_x = chunk_x * 640
        start_y = chunk_y * 640
        for i in range(640):
            for j in range(640):
                bd_data = self.process_bd_data(start_x + j, start_y + i)
                index = j + i * 640
                for k in range(7):
                    bd_array[index, k] = bd_data >> (64 * k) & (2 ** 64 - 1)
        return bd_array.reshape((640, 640, 7), order='F')

    def surge_offset(self, x: int, y: int, direction: int):
        bd_data = self.get_bd_data(x, y)
        d_x, d_y = direction_offset(direction)
        start = 220
        offset = 0
        for i in range(10):
            start += d_x + d_y * 21
            if bd_data & (2 ** start):
                offset = i + 1
        return offset

    def escape_offset(self, x: int, y: int, direction: int):
        bd_data = self.get_bd_data(x, y)
        d_x, d_y = direction_offset(direction)
        d_x = -d_x
        d_y = -d_y
        start = 220
        offset = 0
        for i in range(7):
            start += d_x + d_y * 21
            if bd_data & (2 ** start):
                offset = i + 1
        return offset

    def get_bd_data(self, x: int, y: int):
        chunk = (x // 640, y // 640)
        if chunk in self.bd_data:
            bd_data_array = self.bd_data[chunk]
            bd_data = 0
            for i in range(7):
                bd_data += int(bd_data_array[x % 640, y % 640, i]) << (64*i)
            return bd_data
        elif 0 <= x < RS_LENGTH and 0 <= y < RS_HEIGHT:
            bd_data_array = np.load(
                "MapData/BD/bd-" + str(x // 640) + "-" + str(y // 640) + "-" + str(self.floor) + ".npy")
            self.bd_data[chunk] = bd_data_array
            bd_data = 0
            for i in range(7):
                bd_data += int(bd_data_array[x % 640, y % 640, i]) << (64*i)
            return bd_data
        else:
            return 0

    def build_se_array(self, chunk_x: int, chunk_y: int):
        se_array = np.zeros(shape=(640, 640, 8), dtype=np.uint8)
        start_x = chunk_x * 640
        start_y = chunk_y * 640
        for i in range(640):
            for j in range(640):
                for direction in range(8):
                    s_data = self.surge_offset(start_x + j, start_y + i, direction)
                    e_data = self.escape_offset(start_x + j, start_y + i, direction)
                    se_array[j, i, direction] = s_data + 16 * e_data
        return se_array


def inflate(data):
    decompress = zlib.decompressobj(
        0
    )
    inflated = decompress.decompress(data)
    inflated += decompress.flush()
    return inflated


if __name__ == '__main__':
    st = time.time()
    for floor in range(0, 1):
        for a in range(0, 5):
            for b in range(0, 10):
                file = open("MapData/Map/collision-"+str(a)+"-"+str(b)+"-"+str(floor)+".bin", "rb")
                file_data = file.read()
                file_data = inflate(file_data)
                array = np.frombuffer(file_data, dtype=np.uint8)
                array = array.reshape((1280, 1280), order='F')
                file.close()
                # np.save("MapData/Map/move-"+str(a)+"-"+str(b)+"-"+str(floor)+".npy", array)
                # process = ProcessData(floor)
                # array = process.build_se_array(a, b)
                # np.save("MapData/SE/se-" + str(a) + "-" + str(b) + "-" + str(floor) + ".npy", array)
    et = time.time()
    print(et-st)
