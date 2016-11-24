from pyglet.window import key


class InputHandler(key.KeyStateHandler):
    inputs = [0]*16

    keys = {
        key.Q: 0x0,
        key.W: 0x1,
        key.E: 0x2,
        key.R: 0x3,
        key.T: 0x4,
        key.Y: 0x5,
        key.U: 0x6,
        key.I: 0x7,
        key.O: 0x8,
        key.P: 0x9,
        key.A: 0xA,
        key.S: 0xB,
        key.D: 0xC,
        key.F: 0xD,
        key.G: 0xE,
        key.H: 0xF
    }

    def __init__(self, screen):
        screen.push_handlers(self)

    def on_key_press(self, symbol, modifiers):
        if (symbol in self.keys):
            self.inputs[self.keys[symbol]] = True

    def on_key_release(self, symbol, modifiers):
        if (symbol in self.keys):
            self.inputs[self.keys[symbol]] = False

    def is_pressed(self, key):
        return self.inputs[key]