from numba import jit, uint8, uint16


@jit(nopython=True, signature_or_function=uint8(uint16, uint16))
def free_direction(data: int, direction: int):
    t = [2, 32, 4, 64, 8, 128, 1, 16]
    return data & t[direction] != 0


@jit(nopython=True)
def direction_offset(direction: int) -> tuple:
    offsets = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
    return offsets[direction]


@jit(nopython=True)
def adj_positions(x: int, y: int) -> list:
    return [(x, y + 1), (x + 1, y + 1), (x + 1, y), (x + 1, y - 1), (x, y - 1), (x - 1, y - 1), (x - 1, y),
            (x - 1, y + 1)]
