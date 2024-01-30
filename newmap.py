from PIL import Image, ImageDraw
import numpy as np

RS_HEIGHT = 12800
RS_LENGTH = 6400


class MapSection:

    def __init__(self, floor: int, x_start: int, x_end: int, y_start: int, y_end: int, move_data: np.array, bd_data: np.array, se_data: np.array, cell_size: int = 4):
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
        pass

    def create_image(self):
        length = self.x_end - self.x_start + 1
        print(length)
        height = self.y_end - self.y_start + 1
        print(height)
        cell_size = self.cell_size
        move_data = self.move_data
        img = Image.new("RGBA", size=(length * (cell_size + 1) - 1, height * (cell_size + 1) - 1),
                        color=(255, 255, 255, 255))
        draw = ImageDraw.Draw(img)
        for x in range(length):
            draw.line([((cell_size + 1) * (x + 1) - 1, 0), ((cell_size + 1) * (x + 1) - 1, img.size[1] - 1)],
                      fill=(0, 0, 0, 255))
        for y in range(height):
            draw.line([(0, (cell_size + 1) * (y + 1) - 1), (img.size[0] - 1, (cell_size + 1) * (y + 1) - 1)],
                      fill=(0, 0, 0, 255))
        for x in range(len(move_data)):
            for y in range(len(move_data[x])):
                if not self.free_direction(move_data[x][y], 0) and y < len(move_data[x]) - 1:
                    draw.line([(x*(cell_size+1)-1, (height-y-1)*(cell_size+1)-1), (x*(cell_size+1)+cell_size, (height-y-1)*(cell_size+1)-1)], fill=(255, 0, 0, 255))
                if not self.free_direction(move_data[x][y], 2) and x < len(move_data) - 1:
                    draw.line([((x+1)*(cell_size+1)-1, (height-y)*(cell_size+1)-1), ((x+1)*(cell_size+1)-1, (height-y)*(cell_size+1)-cell_size-2)], fill=(255, 0, 0, 255))
                if not self.free_direction(move_data[x][y], 4) and y > 0:
                    draw.line([(x*(cell_size+1)-1, (height-y)*(cell_size+1)-1), (x*(cell_size+1)+cell_size, (height-y)*(cell_size+1)-1)], fill=(255, 0, 0, 255))
                if not self.free_direction(move_data[x][y], 6) and x > 0:
                    draw.line([(x*(cell_size+1)-1, (height-y)*(cell_size+1)-1), (x*(cell_size+1)-1, (height-y)*(cell_size+1)-cell_size-2)], fill=(255, 0, 0, 255))
        return img

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
        chunk_x = x_start//640, x_end//640
        chunk_y = y_start//640, y_end//640
        rows = []
        for j in range(chunk_y[1]-chunk_y[0]+1):
            row = []
            for i in range(chunk_x[1]-chunk_x[0]+1):
                arr = np.load("MapData/Map/move-" + str(chunk_x[0] + i) + "-" + str(chunk_y[0] + j) + "-" + str(floor) + ".npy")
                x_1 = max((x_start % 640)-i*640, 0)
                x_2 = x_end-x_start+(x_start % 640)+1
                y_1 = max((y_start % 640)-j*640, 0)
                y_2 = y_end-y_start+(y_start % 640)-j*640+1
                row.append(arr[x_1:x_2, y_1:y_2])
            rows.append(np.concatenate(row, axis=0))
        move_data = np.concatenate(rows, axis=1)
        return move_data

    @staticmethod
    def build_bd_array(floor: int, x_start: int, x_end: int, y_start: int, y_end: int):
        return None

    @staticmethod
    def build_se_array(floor: int, x_start: int, x_end: int, y_start: int, y_end: int):
        return None

    @staticmethod
    def free_direction(data: int, direction: int):
        t = [2, 32, 4, 64, 8, 128, 1, 16]
        return data // t[direction] % 2 != 0
