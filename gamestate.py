import mapsection


class GameState:
    def __init__(self, pos: tuple, direction: int, secd: int = 0, scd: int = 0, ecd: int = 0, bdcd: int = 0,
                 wait_time: int = 0, can_pulse: int = 0, goals: int = 0):
        self.pos = pos
        self.direction = direction
        self.secd = secd
        self.scd = scd
        self.ecd = ecd
        self.bdcd = bdcd
        self.wait_time = wait_time
        self.can_pulse = can_pulse
        self.goals = goals

    def __eq__(self, other):
        if isinstance(other, GameState):
            return self.pos == other.pos and self.direction == other.direction and self.secd == other.secd and\
                self.scd == other.scd and self.ecd == other.ecd and self.bdcd == other.bdcd and\
                self.wait_time == other.wait_time and self.can_pulse == other.can_pulse and self.goals == other.goals
        return False

    def update(self):
        new_secd = self.secd
        new_scd = self.scd
        new_ecd = self.ecd
        new_bdcd = self.bdcd
        new_wait_time = self.wait_time
        new_can_pulse = self.can_pulse
        if not new_secd == 0:
            new_secd = new_secd - 1
        if not new_scd == 0:
            new_scd = new_scd - 1
        if not new_ecd == 0:
            new_ecd = new_ecd - 1
        if not new_bdcd == 0:
            new_bdcd = new_bdcd - 1
        if not new_wait_time == 0:
            new_wait_time = new_wait_time - 1
        new_can_pulse = (new_can_pulse + 1) % 2
        return GameState(self.pos, self.direction, new_secd, new_scd, new_ecd, new_bdcd, new_wait_time,
                         new_can_pulse, self.goals)

    def move(self, x: int, y: int, direction: int):
        return GameState((x, y), direction, self.secd, self.scd, self.ecd, self.bdcd, self.wait_time,
                         self.can_pulse, self.goals)

    def surge(self, x: int, y: int):
        new_pos = (x, y)
        if self.secd == 0:
            if self.scd < 2:
                return GameState(new_pos, self.direction, 17, 2, 17, self.bdcd, self.wait_time, self.can_pulse,
                                 self.goals)
            else:
                return GameState(new_pos, self.direction, 17, self.scd, 17, self.bdcd, self.wait_time, self.can_pulse,
                                 self.goals)
        elif self.scd == 0:
            if self.secd < 2:
                return GameState(new_pos, self.direction, 2, 17, 2, self.bdcd, self.wait_time, self.can_pulse,
                                 self.goals)
            else:
                return GameState(new_pos, self.direction, self.secd, 17, self.ecd, self.bdcd, self.wait_time,
                                 self.can_pulse, self.goals)
        else:
            print(self.pos)
            raise Exception("Surge is on cooldown")

    def escape(self, map_section: mapsection.MapSection):
        new_pos = map_section.escape_range(self.pos[0], self.pos[1], self.direction)
        if new_pos is None:
            return None
        if self.secd == 0:
            if new_pos == self.pos:
                return GameState(self.pos, self.direction, self.secd, self.scd, self.ecd, self.bdcd,
                                 self.wait_time, self.can_pulse, self.goals)
            if self.ecd < 2:
                return GameState(new_pos, self.direction, 17, 17, 2, self.bdcd, self.wait_time, self.can_pulse,
                                 self.goals)
            else:
                return GameState(new_pos, self.direction, 17, 17, self.ecd, self.bdcd, self.wait_time, self.can_pulse,
                                 self.goals)
        elif self.ecd == 0:
            if new_pos == self.pos:
                return GameState(self.pos, self.direction, self.secd, self.scd, self.ecd, self.bdcd,
                                 self.wait_time, self.can_pulse, self.goals)
            if self.secd < 2:
                return GameState(new_pos, self.direction, 2, 2, 17, self.bdcd, self.wait_time, self.can_pulse,
                                 self.goals)
            else:
                return GameState(new_pos, self.direction, self.secd, self.scd, 17, self.bdcd, self.wait_time,
                                 self.can_pulse, self.goals)
        else:
            print(self.pos)
            raise Exception("Escape is on cooldown")

    def bd(self, x: int, y: int, direction: int):
        if self.bdcd == 0:
            return GameState((x, y), direction, self.secd, self.scd, self.ecd, 17, self.wait_time, self.can_pulse,
                             self.goals)

    def can_bd(self):
        return self.bdcd == 0

    def can_surge(self):
        return self.secd == 0 or self.scd == 0

    def can_escape(self):
        return self.secd == 0 or self.ecd == 0

    def min_cd(self):
        cds = [(self.secd, "se"), (self.scd, "s"), (self.ecd, "e"), (self.bdcd, "bd")]
        cds = sorted(cds, key=lambda tup: tup[0])
        return cds[0]
