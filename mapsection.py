from PIL import Image, ImageDraw
import numpy as np
from numba import jit
from helper import (free_direction,
                    adj_positions,
                    direction_offset)

RS_HEIGHT = 12800
RS_LENGTH = 6400

class MapSection:

    def __init__(self, floor: int, x_start: int, x_end: int, y_start: int, y_end: int, move_data: np.array, bd_data: np.array, se_data: np.array, cell_size: int = 5):
        self.floor = floor
        self.x_start = x_start
        self.x_end = x_end
        self.y_start = y_start
        self.y_end = y_end
        self.move_data = move_data
        self.bd_data = bd_data
        self.se_data = se_data
        self.cell_size = cell_size
        self.image = self.create_image()

    def bd_range(self, x: int, y: int):
        bd_data = self.bd_data[x - self.x_start, y - self.y_start]
        # bd_data_array = self.bd_data
        # for i in range(7):
        #     bd_data += int(bd_data_array[x - self.x_start, y - self.y_start, i]) << (64 * i)
        tiles = []
        for i in range(21):
            for j in range(21):
                if bd_data & (2 ** (j + i * 21)):
                    u = x - 10 + j
                    v = y - 10 + i
                    tiles.append((u, v))
        directions = []
        for tile in tiles:
            x_diff = tile[0] - x
            y_diff = tile[1] - y
            if x_diff == 0:
                if y_diff > 0:
                    directions.append(0)
                else:
                    directions.append(4)
            elif y_diff == 0:
                if x_diff > 0:
                    directions.append(2)
                else:
                    directions.append(6)
            elif (abs(x_diff) + 0.5) / (abs(y_diff) + 0.5) > 7.5 / 3.5:
                if x_diff > 0:
                    directions.append(2)
                else:
                    directions.append(6)
            elif (abs(y_diff) + 0.5) / (abs(x_diff) + 0.5) > 7.5 / 3.5:
                if y_diff > 0:
                    directions.append(0)
                else:
                    directions.append(4)
            elif x_diff > 0:
                if y_diff > 0:
                    directions.append(1)
                else:
                    directions.append(3)
            elif x_diff < 0:
                if y_diff > 0:
                    directions.append(7)
                else:
                    directions.append(5)
        return tiles, directions

    def surge_range(self, x: int, y: int, direction: int):
        offset = self.se_data[x - self.x_start, y - self.y_start, direction] & 15
        dir_offset = direction_offset(direction)
        x_diff = dir_offset[0] * offset
        y_diff = dir_offset[1] * offset
        return x + x_diff, y + y_diff

    def escape_range(self, x: int, y: int, direction: int):
        offset = self.se_data[x - self.x_start, y - self.y_start, direction] >> 4
        dir_offset = direction_offset(direction)
        x_diff = dir_offset[0] * offset
        y_diff = dir_offset[1] * offset
        return x - x_diff, y - y_diff

    def walk_range(self, x: int, y: int):
        tiles = []
        directions = []
        start = self.move_data[x - self.x_start, y - self.y_start]
        adj = adj_positions(x, y)
        visited = {(x, y)}
        queue = []
        for i in range(8):
            j = (2 * i + i // 4) % 8
            if free_direction(start, j):
                tiles.append(adj[j])
                directions.append(j)
                visited.add(adj[j])
                queue.append(adj[j])
        while queue:
            current = queue.pop(0)
            move = self.move_data[current[0] - self.x_start, current[1] - self.y_start]
            temp_adj = adj_positions(current[0], current[1])
            for i in range(8):
                if free_direction(move, i):
                    if temp_adj[i] not in visited:
                        tiles.append(temp_adj[i])
                        directions.append(i)
                        visited.add(temp_adj[i])
        return tiles, directions

    def create_image(self):
        length = self.x_end - self.x_start + 1
        height = self.y_end - self.y_start + 1
        cell_size = self.cell_size
        move_data = self.move_data
        img = Image.new("RGBA", size=(length * (cell_size + 1) - 1, height * (cell_size + 1) - 1),
                        color=(255, 255, 255, 150))
        draw = ImageDraw.Draw(img)
        for x in range(length):
            draw.line([((cell_size + 1) * (x + 1) - 1, 0), ((cell_size + 1) * (x + 1) - 1, img.size[1] - 1)],
                      fill=(0, 0, 0, 255))
        for y in range(height):
            draw.line([(0, (cell_size + 1) * (y + 1) - 1), (img.size[0] - 1, (cell_size + 1) * (y + 1) - 1)],
                      fill=(0, 0, 0, 255))
        for x in range(len(move_data)):
            for y in range(len(move_data[x])):
                if not free_direction(move_data[x][y], 0) and y < len(move_data[x]) - 1:
                    draw.line([(x*(cell_size+1)-1, (height-y-1)*(cell_size+1)-1), (x*(cell_size+1)+cell_size, (height-y-1)*(cell_size+1)-1)], fill=(255, 0, 0, 255))
                if not free_direction(move_data[x][y], 2) and x < len(move_data) - 1:
                    draw.line([((x+1)*(cell_size+1)-1, (height-y)*(cell_size+1)-1), ((x+1)*(cell_size+1)-1, (height-y)*(cell_size+1)-cell_size-2)], fill=(255, 0, 0, 255))
                if not free_direction(move_data[x][y], 4) and y > 0:
                    draw.line([(x*(cell_size+1)-1, (height-y)*(cell_size+1)-1), (x*(cell_size+1)+cell_size, (height-y)*(cell_size+1)-1)], fill=(255, 0, 0, 255))
                if not free_direction(move_data[x][y], 6) and x > 0:
                    draw.line([(x*(cell_size+1)-1, (height-y)*(cell_size+1)-1), (x*(cell_size+1)-1, (height-y)*(cell_size+1)-cell_size-2)], fill=(255, 0, 0, 255))
        return img

    def color_tiles(self, tiles: list, color: tuple):
        img = self.image
        x_start = self.x_start
        y_start = self.y_start
        cell_size = self.cell_size
        draw = ImageDraw.Draw(img)
        for tile in tiles:
            draw.rectangle((((tile[0] - x_start) * (cell_size + 1), img.size[1] - (tile[1] - y_start + 1) * (cell_size + 1) + 1), ((tile[0] - x_start) * (cell_size + 1) + (cell_size - 1), img.size[1] - ((tile[1] - y_start) + 1) * (cell_size + 1) + (cell_size - 1) + 1)), fill=color)
        self.image = img

    def arrow_tiles(self, tiles: list, directions: list):
        img = self.image
        cell_size = self.cell_size
        x_start = self.x_start
        y_start = self.y_start
        draw = ImageDraw.Draw(img)
        for i in range(len(tiles)):
            x = tiles[i][0] - x_start
            y = tiles[i][1] - y_start
            if directions[i] == 0:
                offset = [0, -1, 1, 0, -1, 0]
                points = [((cell_size + 1) * x + cell_size / 2 + offset[0],
                           img.size[1] - (cell_size + 1) * y - cell_size / 2 + offset[1]), (
                              (cell_size + 1) * x + cell_size / 2 + offset[2],
                              img.size[1] - (cell_size + 1) * y - cell_size / 2 + offset[3]), (
                              (cell_size + 1) * x + cell_size / 2 + offset[4],
                              img.size[1] - (cell_size + 1) * y - cell_size / 2 + offset[5])]
                draw.point(points, fill=(0, 0, 255, 255))
            if directions[i] == 1:
                offset = [1, -1, 0, -1, 1, 0]
                points = [((cell_size + 1) * x + cell_size / 2 + offset[0],
                           img.size[1] - (cell_size + 1) * y - cell_size / 2 + offset[1]), (
                              (cell_size + 1) * x + cell_size / 2 + offset[2],
                              img.size[1] - (cell_size + 1) * y - cell_size / 2 + offset[3]), (
                              (cell_size + 1) * x + cell_size / 2 + offset[4],
                              img.size[1] - (cell_size + 1) * y - cell_size / 2 + offset[5])]
                draw.point(points, fill=(0, 0, 255, 255))
            if directions[i] == 2:
                offset = [1, 0, 0, -1, 0, 1]
                points = [((cell_size + 1) * x + cell_size / 2 + offset[0],
                           img.size[1] - (cell_size + 1) * y - cell_size / 2 + offset[1]), (
                              (cell_size + 1) * x + cell_size / 2 + offset[2],
                              img.size[1] - (cell_size + 1) * y - cell_size / 2 + offset[3]), (
                              (cell_size + 1) * x + cell_size / 2 + offset[4],
                              img.size[1] - (cell_size + 1) * y - cell_size / 2 + offset[5])]
                draw.point(points, fill=(0, 0, 255, 255))
            if directions[i] == 3:
                offset = [1, 1, 1, 0, 0, 1]
                points = [((cell_size + 1) * x + cell_size / 2 + offset[0],
                           img.size[1] - (cell_size + 1) * y - cell_size / 2 + offset[1]), (
                              (cell_size + 1) * x + cell_size / 2 + offset[2],
                              img.size[1] - (cell_size + 1) * y - cell_size / 2 + offset[3]), (
                              (cell_size + 1) * x + cell_size / 2 + offset[4],
                              img.size[1] - (cell_size + 1) * y - cell_size / 2 + offset[5])]
                draw.point(points, fill=(0, 0, 255, 255))
            if directions[i] == 4:
                offset = [0, 1, 1, 0, -1, 0]
                points = [((cell_size + 1) * x + cell_size / 2 + offset[0],
                           img.size[1] - (cell_size + 1) * y - cell_size / 2 + offset[1]), (
                              (cell_size + 1) * x + cell_size / 2 + offset[2],
                              img.size[1] - (cell_size + 1) * y - cell_size / 2 + offset[3]), (
                              (cell_size + 1) * x + cell_size / 2 + offset[4],
                              img.size[1] - (cell_size + 1) * y - cell_size / 2 + offset[5])]
                draw.point(points, fill=(0, 0, 255, 255))
            if directions[i] == 5:
                offset = [-1, 1, 0, 1, -1, 0]
                points = [((cell_size + 1) * x + cell_size / 2 + offset[0],
                           img.size[1] - (cell_size + 1) * y - cell_size / 2 + offset[1]), (
                              (cell_size + 1) * x + cell_size / 2 + offset[2],
                              img.size[1] - (cell_size + 1) * y - cell_size / 2 + offset[3]), (
                              (cell_size + 1) * x + cell_size / 2 + offset[4],
                              img.size[1] - (cell_size + 1) * y - cell_size / 2 + offset[5])]
                draw.point(points, fill=(0, 0, 255, 255))
            if directions[i] == 6:
                offset = [-1, 0, 0, 1, 0, -1]
                points = [((cell_size + 1) * x + cell_size / 2 + offset[0],
                           img.size[1] - (cell_size + 1) * y - cell_size / 2 + offset[1]), (
                              (cell_size + 1) * x + cell_size / 2 + offset[2],
                              img.size[1] - (cell_size + 1) * y - cell_size / 2 + offset[3]), (
                              (cell_size + 1) * x + cell_size / 2 + offset[4],
                              img.size[1] - (cell_size + 1) * y - cell_size / 2 + offset[5])]
                draw.point(points, fill=(0, 0, 255, 255))
            if directions[i] == 7:
                offset = [-1, -1, -1, 0, 0, -1]
                points = [((cell_size + 1) * x + cell_size / 2 + offset[0],
                           img.size[1] - (cell_size + 1) * y - cell_size / 2 + offset[1]), (
                              (cell_size + 1) * x + cell_size / 2 + offset[2],
                              img.size[1] - (cell_size + 1) * y - cell_size / 2 + offset[3]), (
                              (cell_size + 1) * x + cell_size / 2 + offset[4],
                              img.size[1] - (cell_size + 1) * y - cell_size / 2 + offset[5])]
                draw.point(points, fill=(0, 0, 255, 255))
        self.image = img

    def save_map_section(self, name: str):
        info = np.asarray([self.floor, self.x_start, self.x_end, self.y_start, self.y_end])
        np.save("MapData/SavedMaps/info-" + name + "MapSection.npy", info)
        np.save("MapData/SavedMaps/move-" + name + "MapSection.npy", self.move_data)
        np.save("MapData/SavedMaps/bd-" + name + "MapSection.npy", self.bd_data)
        np.save("MapData/SavedMaps/se-" + name + "MapSection.npy", self.se_data)

    @classmethod
    def load_map_section(cls, name: str):
        info = np.load("MapData/SavedMaps/info-" + name + "MapSection.npy")
        move_data = np.load("MapData/SavedMaps/move-" + name + "MapSection.npy")
        bd_data = np.load("MapData/SavedMaps/bd-" + name + "MapSection.npy")
        se_data = np.load("MapData/SavedMaps/se-" + name + "MapSection.npy")
        return cls(info[0], info[1], info[2], info[3], info[4], move_data, bd_data, se_data)

    @classmethod
    def create_map_section(cls, floor: int, x_start: int, x_end: int, y_start: int, y_end: int):
        move_data = cls.build_movement_array(floor, x_start, x_end, y_start, y_end)
        bd_data = cls.build_bd_array(floor, x_start, x_end, y_start, y_end)
        se_data = cls.build_se_array(floor, x_start, x_end, y_start, y_end)
        return cls(floor, x_start, x_end, y_start, y_end, move_data, bd_data, se_data)

    @staticmethod
    def build_movement_array(floor: int, x_start: int, x_end: int, y_start: int, y_end: int):
        chunk_size = 1280
        chunk_x = x_start//chunk_size, x_end//chunk_size
        chunk_y = y_start//chunk_size, y_end//chunk_size
        rows = []
        for j in range(chunk_y[1]-chunk_y[0]+1):
            row = []
            for i in range(chunk_x[1]-chunk_x[0]+1):
                arr = np.load("MapData/Map/move-" + str(chunk_x[0] + i) + "-" + str(chunk_y[0] + j) + "-" + str(floor) + ".npy")
                x_1 = max((x_start % chunk_size)-i*chunk_size, 0)
                x_2 = x_end-x_start+(x_start % chunk_size)+1
                y_1 = max((y_start % chunk_size)-j*chunk_size, 0)
                y_2 = y_end-y_start+(y_start % chunk_size)-j*chunk_size+1
                row.append(arr[x_1:x_2, y_1:y_2])
            rows.append(np.concatenate(row, axis=0))
        move_data = np.concatenate(rows, axis=1)
        return move_data.astype('int32')

    @staticmethod
    def build_bd_array(floor: int, x_start: int, x_end: int, y_start: int, y_end: int):
        chunk_x = x_start // 640, x_end // 640
        chunk_y = y_start // 640, y_end // 640
        rows = []
        for j in range(chunk_y[1] - chunk_y[0] + 1):
            row = []
            for i in range(chunk_x[1] - chunk_x[0] + 1):
                arr = np.load(
                    "MapData/BD/bd-" + str(chunk_x[0] + i) + "-" + str(chunk_y[0] + j) + "-" + str(floor) + ".npy")
                x_1 = max((x_start % 640) - i * 640, 0)
                x_2 = x_end - x_start + (x_start % 640) + 1
                y_1 = max((y_start % 640) - j * 640, 0)
                y_2 = y_end - y_start + (y_start % 640) - j * 640 + 1
                row.append(arr[x_1:x_2, y_1:y_2])
            rows.append(np.concatenate(row, axis=0))
        bd_data = np.concatenate(rows, axis=1)
        new_bd_data = np.zeros((bd_data.shape[0], bd_data.shape[1]), dtype=object)
        for x in range(bd_data.shape[0]):
            for y in range(bd_data.shape[1]):
                sum = 0
                for i in range(7):
                    sum += int(bd_data[x][y][i]) << (64 * i)
                new_bd_data[x][y] = sum
        return new_bd_data

    @staticmethod
    def build_se_array(floor: int, x_start: int, x_end: int, y_start: int, y_end: int):
        chunk_x = x_start // 640, x_end // 640
        chunk_y = y_start // 640, y_end // 640
        rows = []
        for j in range(chunk_y[1] - chunk_y[0] + 1):
            row = []
            for i in range(chunk_x[1] - chunk_x[0] + 1):
                arr = np.load(
                    "MapData/SE/se-" + str(chunk_x[0] + i) + "-" + str(chunk_y[0] + j) + "-" + str(floor) + ".npy")
                x_1 = max((x_start % 640) - i * 640, 0)
                x_2 = x_end - x_start + (x_start % 640) + 1
                y_1 = max((y_start % 640) - j * 640, 0)
                y_2 = y_end - y_start + (y_start % 640) - j * 640 + 1
                row.append(arr[x_1:x_2, y_1:y_2])
            rows.append(np.concatenate(row, axis=0))
        se_data = np.concatenate(rows, axis=1)
        return se_data.astype('int32')


