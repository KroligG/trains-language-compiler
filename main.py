import re, sys, time


class language:
    def __init__(self):
        self.statements = []

    def compile(self, command):
        for statement, function in self.statements:
            regex = re.compile(statement)
            match = regex.match(command)
            if match:
                return function(*match.groups())
        raise Exception("No such command " + command)

    def command(self, regex):
        def add_command(fun):
            self.statements.append((regex, fun))
            return fun

        return add_command


def itself(fun):
    def wrap(*args):
        return lambda (self): fun(self, *args)

    return wrap


class Train:
    train_language = language()

    def __init__(self, position, station, firmware):
        self.position = position
        self.station = station
        self.load(firmware)

    def load(self, firmware):
        self.commands = []
        for statement in (s.strip() for s in firmware.split("\n") if s.strip()):
            self.commands.append(self.train_language.compile(statement))
        self.code_pointer = 0

    def tick(self):
        self.commands[self.code_pointer](self)
        self.code_pointer += 1
        return self.code_pointer == len(self.commands)

    @train_language.command(r"L")
    @itself
    def left(self):
        self.position -= 1

    @train_language.command(r"R")
    @itself
    def right(self):
        self.position += 1

    @train_language.command(r"goto (\d+)")
    @itself
    def goto(self, pointer):
        pointer = int(pointer) - 1
        if pointer >= len(self.commands):
            raise Exception("Invalid goto")
        self.code_pointer = pointer


@Train.train_language.command(r"if c: (.+)")
def if_precompile(command):
    result = Train.train_language.compile(command)

    def if_fun(train):
        if train.position == train.station:
            result(train)

    return if_fun

def simulation():
    firmware = """
        R
        if c: goto 3
        goto 0
        R
        goto 3
    """
    station = 0
    train1 = Train(-5, station, firmware)
    train2 = Train(5, station, firmware)
    draw(train1, train2, station)
    program_ended = False
    iteration_count = 0
    while train1.position != train2.position and not program_ended and iteration_count < 100:
        program_ended = train1.tick() or train2.tick()
        draw(train1, train2, station)
        time.sleep(0.1)

def draw(train1, train2, station):
    min_pos = min(train1.position, train2.position, station) - 5
    max_pos = max(train1.position, train2.position, station) + 5
    result = ['\r']
    for i in xrange(min_pos, max_pos):
        if i == train1.position == train2.position:
            result.append('X')
        elif i == train1.position or i == train2.position:
            result.append('o')
        elif i == station:
            result.append('A')
        else:
            result.append('_')
        sys.stdout.write("".join(result))

simulation()