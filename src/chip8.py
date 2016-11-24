from cpu import Cpu
from screen import Screen
from input_handler import InputHandler
import sys


class Chip8:

    cpu = None
    screen = None
    input_handler = None

    #MAX_MEMORY = 4096

    def __init__(self):
        self.screen = Screen(640, 320)
        self.input_handler = InputHandler(self.screen)

        self.cpu = Cpu(self.screen, self.input_handler)

        self.loop()

    def loop(self):
        self.cpu.load_rom(sys.argv[1])

        while True:
            self.cpu.cycle()

if __name__ == "__main__":
    Chip8()