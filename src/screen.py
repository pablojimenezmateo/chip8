import pyglet


class Screen(pyglet.window.Window):
    display_buffer = None
    screen_width   = 64
    screen_height  = 32
    tile_size      = 10
    
    clock = None

    def __init__(self, width, height):
        super(Screen, self).__init__(width=width, height=height, visible=True, vsync=False)
        self.clear_buffer()
        
        pyglet.clock.set_fps_limit(30)

    def on_draw(self):
        self.clear()
        
        pixels_to_draw = pyglet.graphics.Batch()
        borders_to_draw = pyglet.graphics.Batch()

        for x in range(self.screen_width):
            for y in range(self.screen_height):
                if self.display_buffer[x][y]:
                    x_position = x * self.tile_size
                    y_position = ((self.screen_height*self.tile_size) - self.tile_size) - y * self.tile_size

                    pixel_list = ('v2f', [
                        x_position + 0, y_position + 0,
                        x_position + self.tile_size, y_position + 0,
                        x_position + self.tile_size, y_position + self.tile_size,
                        x_position + 0, y_position + self.tile_size
                    ])
                    
                    border_list = ('v2f', [
                        x_position + 0, y_position + 0,
                        x_position + self.tile_size, y_position + 0,
                        x_position + self.tile_size, y_position + 0,
                        x_position + self.tile_size, y_position + self.tile_size,
                        x_position + self.tile_size, y_position + self.tile_size,
                        x_position + 0, y_position + self.tile_size,
                        x_position + 0, y_position + self.tile_size,
                        x_position + 0, y_position + 0
                    ])

                    pixels_to_draw.add(4, pyglet.gl.GL_QUADS, None, pixel_list)
                    borders_to_draw.add(8, pyglet.gl.GL_LINES, None, border_list)

        pyglet.gl.glColor3f(1, 1, 1)
        pixels_to_draw.draw()
        
        pyglet.gl.glColor3f(0, 0, 0)
        borders_to_draw.draw()

    def clear_buffer(self):
        self.display_buffer = [[0 for y in range(self.screen_height)] for x in range(self.screen_width)]

    def get_pixel(self, x, y):
        return self.display_buffer[x][y]

    def set_pixel(self, x, y, val):
        self.display_buffer[x][y] = val

    def render_once(self):
        
        pyglet.clock.tick()
        
        self.switch_to()
        self.dispatch_events()
        self.dispatch_event('on_draw')
        self.flip()
    
    def check_keys(self):
        
        self.switch_to()
        self.dispatch_events()
        self.flip()