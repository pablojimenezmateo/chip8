from random import randint

class Cpu(object):

    debug_memory = False
    debug_instructions = False

    screen = None
    input_handler = None

    timers = None
    registers = None
    offset = 0x200

    memory = [0]*4096
    stack = []

    opcode = 0
    vx = 0
    vy = 0

    def __init__(self, screen, input_handler):
        self.screen = screen
        self.input_handler = input_handler

        self.function_map = {
            0x0: self.cycle_zero_functions,                 # 0nnn / 00E0 / 00EE
            0x1: self.jump_to_location,                     # 1nnn
            0x2: self.call_subroutine,                      # 2nnn
            0x3: self.skip_instruction_if_vx_equal_kk,      # 3xkk
            0x4: self.skip_instruction_if_vx_notequal_kk,   # 4xkk
            0x5: self.skip_instruction_if_vx_equal_vy,      # 5xy0
            0x6: self.set_vx,                               # 6xkk
            0x7: self.increment_vx_kk_units,                # 7xkk
            0x8: self.cycle_eight_function,
            0x9: self.skip_instruction_if_vx_not_equal_vy,  # 9xy0
            0xA: self.set_I_to_nnn,                         # Annn
            0xB: self.jump_to_nnn_sum_v0,                   # Bnnn
            0xC: self.set_vx_random_and_kk,                 # Cxkk
            0xD: self.draw_sprite,                          # Dxyn
            0xE: self.cycle_e_function,                     # Ex9E / ExA1
            0xF: self.cycle_f_function,
        }

        self.eight_functions = {
            0x0: self.set_vx_equal_vy,              # 8xy0
            0x1: self.set_vx_bitwise_or_vx_vy,      # 8xy1
            0x2: self.set_vx_bitwise_and_vx_vy,     # 8xy2
            0x3: self.set_vx_bitwise_xor_vx_vy,     # 8xy3
            0x4: self.set_vx_sum_vx_vy,             # 8xy4
            0x5: self.set_vx_substraction_vx_vy,    # 8xy5
            0x6: self.set_vx_vx_divided_by_two,     # 8xy6
            0x7: self.set_vx_substraction_vy_vx,    # 8xy7
            0xE: self.set_vx_vx_multiplied_by_two,  # 8xyE
        }

        self.f_functions = {
            0x07: self.set_vx_to_delay_timer,                    # Fx07
            0x0A: self.wait_for_keypress,                        # Fx0A
            0x15: self.set_delay_timer_to_vx,                    # Fx15
            0x18: self.set_sound_timer_to_vx,                    # Fx18
            0x1E: self.set_I_I_sum_vx,                           # Fx1E
            0x29: self.set_I_to_sprite_location_of_value_of_vx,  # Fx29
            0x33: self.store_number_in_memory,                   # Fx33
            0x55: self.store_registers_in_memory,                # Fx55
            0x65: self.load_registers_from_memory,               # Fx65
        }

        self.fonts = [0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
           0x20, 0x60, 0x20, 0x20, 0x70,  # 1
           0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
           0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
           0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
           0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
           0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
           0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
           0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
           0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
           0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
           0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
           0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
           0xE0, 0x90, 0x90, 0x90, 0xE0,  # D
           0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
           0xF0, 0x80, 0xF0, 0x80, 0x80   # F
        ]

        self.initialize()

    # Initialize / reset all variables
    def initialize(self):
        self.timers = {
            'delay': 0,
            'sound': 0,
        }

        self.registers = {
            'pc': self.offset,
            'I': 0,
            'v': [0]*16,
        }

        self.opcode = 0
        self.vx = 0
        self.vy = 0

        i = 0
        while i < 80:
            # load 80-char font set
            self.memory[i] = self.fonts[i]
            i += 1
        
    # Load the rom
    def load_rom(self, filename):
        
        data = open(filename, 'rb').read()
        for i, part in enumerate(data):
            self.memory[self.offset + i] = part
                    
        if self.debug_memory:
            print("ROM length: " + str(len(data)))
            
            
    # CPU cycle
    def cycle(self):
        
        if self.debug_memory:
            
            for reg in range(16):
                print("Register v" + str(reg) + ": %X" % self.registers['v'][reg])
                
            print("PC:" + str(self.registers['pc']))
            
            print("--------MEMORY--------")
            
            for index, value in enumerate(self.memory):
                
                if value:
                    
                    if index % 2 == 0:
                        print("Index: " + str(index) + ": %X" % value + " OPCODE: 0x%X%X" %(value, self.memory[index+1]))
                    
                    else:
                        print("Index: " + str(index) + ": %X" % value)
            
        self.opcode = int(self.memory[self.registers['pc']])
        self.opcode = self.opcode << 8
        self.opcode += int(self.memory[self.registers['pc'] + 1])
        self.registers['pc'] += 2

        # Pointers to specific registers
        self.vx = (self.opcode & 0x0f00) >> 8
        self.vy = (self.opcode & 0x00f0) >> 4

        # Execute opcode
        function = (self.opcode & 0xF000) >> 12
        # try:
        # print("opcode: %X" % self.opcode, " -- function %X" % function)
        self.function_map[function]()
        # except KeyError:
        #     print("Unknown instruction: %X" % function)

        # Decrement timers
        if self.timers['delay'] > 0:
            self.timers['delay'] -= 1

        if self.timers['sound'] > 0:
            self.timers['sound'] -= 1

            if self.timers['sound'] == 0:
                print("Beep")

    # Opcodes
    def cycle_zero_functions(self):
        function = self.opcode & 0x00FF

        # 00E0 - CLS
        # Clear the display.
        if (function == 0x0E0):
            self.screen.clear_buffer()
            
            if self.debug_instructions:
                print("Clear screen")

        # 00EE - RET
        # The interpreter sets the program counter to the address at the top of the stack, then subtracts 1 from
        # the stack pointer.
        elif (function == 0x0EE):
            self.registers['pc'] = self.stack.pop()
            
            if self.debug_instructions:
                print("Pop stack")

    # 1nnn - JP addr
    def jump_to_location(self):
        # The interpreter sets the program counter to nnn.
        self.registers['pc'] = self.opcode & 0x0fff
        
        if self.debug_instructions:
            print("Jump location")
                
    # 2nnn - CALL addr
    def call_subroutine(self):
        # The interpreter increments the stack pointer, then puts the current PC on the top of the stack. The PC
        # is then set to nnn.
        self.stack.append(self.registers['pc'])
        self.registers['pc'] = self.opcode & 0x0fff
        
        if self.debug_instructions:
            print("Call subrutine")
            
    # 3xkk - SE Vx, byte
    def skip_instruction_if_vx_equal_kk(self):
        # The interpreter compares register Vx to kk, and if they are equal, increments the program counter by 2.
        kk = self.opcode & 0x00ff
        if(self.registers['v'][self.vx] == kk):
            self.registers['pc'] += 2
        
        if self.debug_instructions:
            print("Skip if vx = kk")
            
    # 4xkk - SNE Vx, byte
    def skip_instruction_if_vx_notequal_kk(self):
        # The interpreter compares register Vx to kk, and if they are not equal, increments the program counter by 2.
        kk = self.opcode & 0x00ff
        if(self.registers['v'][self.vx] != kk):
            self.registers['pc'] += 2
        
        if self.debug_instructions:
            print("Skip if vx != kk")
            
    # 5xy0 - SE Vx, Vy
    def skip_instruction_if_vx_equal_vy(self):
        # The interpreter compares register Vx to register Vy, and if they are equal, increments the program
        # counter by 2.
        if(self.registers['v'][self.vx] == self.registers['v'][self.vy]):
            self.registers['pc'] += 2
        
        if self.debug_instructions:
            print("Skip if vx != vy")
            
    # 6xkk - LD Vx, byte
    def set_vx(self):
        # The interpreter puts the value kk into register Vx.
        kk = self.opcode & 0x00ff
        self.registers['v'][self.vx] = kk
        
        if self.debug_instructions:
            print("Set vx")
            
    # 7xkk - ADD Vx, byte
    def increment_vx_kk_units(self):
        # Adds the value kk to the value of register Vx, then stores the result in Vx.
        kk = self.opcode & 0x00ff
        self.registers['v'][self.vx] = (kk + self.registers['v'][self.vx]) % 256
        
        if self.debug_instructions:
            print("Increment vx kk units")
            
    def cycle_eight_function(self):
        function = self.opcode & 0x000F
        # try:
        self.eight_functions[function]()
        # except KeyError:
        #     print("Unknown eight instruction: %X" % function)

    # 8xy0 - LD Vx, Vy
    def set_vx_equal_vy(self):
        # Stores the value of register Vy in register Vx.
        self.registers['v'][self.vx] = self.registers['v'][self.vy]
        
        if self.debug_instructions:
            print("Set vx = vy")
            
    # 8xy1 - OR Vx, Vy
    def set_vx_bitwise_or_vx_vy(self):
        # Performs a bitwise OR on the values of Vx and Vy, then stores the result in Vx. A bitwise OR compares
        # the corresponding bits from two values, and if either bit is 1, then the same bit in the result is
        # also 1. Otherwise, it is 0.
        self.registers['v'][self.vx] |= self.registers['v'][self.vy]
        
        if self.debug_instructions:
            print("Set vx |=vy")
            
    # 8xy2 - AND Vx, Vy
    def set_vx_bitwise_and_vx_vy(self):
        # Performs a bitwise AND on the values of Vx and Vy, then stores the result in Vx. A bitwise AND
        # compares the corresponding bits from two values, and if both bits are 1, then the same bit in the
        # result is also 1. Otherwise, it is 0.
        self.registers['v'][self.vx] &= self.registers['v'][self.vy]
        
        if self.debug_instructions:
            print("Set vx &=vy")
               
    # 8xy3 - XOR Vx, Vy
    def set_vx_bitwise_xor_vx_vy(self):
        # Performs a bitwise exclusive OR on the values of Vx and Vy, then stores the result in Vx. An exclusive
        # OR compares the corresponding bits from two values, and if the bits are not both the same, then the
        # corresponding bit in the result is set to 1. Otherwise, it is 0.
        self.registers['v'][self.vx] ^= self.registers['v'][self.vy]
        
        if self.debug_instructions:
            print("Set vx ^=vy")
            
    # 8xy4 - ADD Vx, Vy
    def set_vx_sum_vx_vy(self):
        # The values of Vx and Vy are added together. If the result is greater than 8 bits (i.e., > 255,)
        # VF is set to 1, otherwise 0. Only the lowest 8 bits of the result are kept, and stored in Vx.

        # Set the parity bit
        if(self.registers['v'][self.vx] + self.registers['v'][self.vy] > 0xff):
            self.registers['v'][0xF] = 1
        else:
            self.registers['v'][0xF] = 0

        self.registers['v'][self.vx] = (self.registers['v'][self.vx] + self.registers['v'][self.vy]) % 256
        
        if self.debug_instructions:
            print("Set vx +=vy")
            
    # 8xy5 - SUB Vx, Vy
    def set_vx_substraction_vx_vy(self):
        # If Vx > Vy, then VF is set to 1, otherwise 0. Then Vy is subtracted from Vx, and the results stored in Vx.
        if (self.registers['v'][self.vx] > self.registers['v'][self.vy]):
            self.registers['v'][0xF] = 1
        else:
            self.registers['v'][0xF] = 0
        self.registers['v'][self.vx] = (self.registers['v'][self.vx] - self.registers['v'][self.vy]) % 256
        
        if self.debug_instructions:
            print("Set vx = vx - vy")
            
    # 8xy6 - SHR Vx {, Vy}
    def set_vx_vx_divided_by_two(self):
        # If the least-significant bit of Vx is 1, then VF is set to 1, otherwise 0. Then Vx is divided by 2.
        self.registers['v'][0xF] = self.registers['v'][self.vx] & 0x01
        self.registers['v'][self.vx] = (self.registers['v'][self.vx] >> 1) % 256
        
        if self.debug_instructions:
            print("Set vx = vx/2")
            
    # 8xy7 - SUBN Vx, Vy
    def set_vx_substraction_vy_vx(self):
        # If Vy > Vx, then VF is set to 1, otherwise 0. Then Vx is subtracted from Vy, and the results stored in Vx.
        if (self.registers['v'][self.vy] > self.registers['v'][self.vx]):
            self.registers['v'][0xF] = 1
        else:
            self.registers['v'][0xF] = 0
        self.registers['v'][self.vx] = (self.registers['v'][self.vy] - self.registers['v'][self.vx]) % 256
        
        if self.debug_instructions:
            print("Set vx = vy - vx")
            
    # 8xyE - SHL Vx {, Vy}
    def set_vx_vx_multiplied_by_two(self):
        # If the most-significant bit of Vx is 1, then VF is set to 1, otherwise to 0. Then Vx is multiplied by 2.
        most_significant_bit = self.registers['v'][self.vx] >> 7 & 0x01
               
        self.registers['v'][0xF] = most_significant_bit
        self.registers['v'][self.vx] = (self.registers['v'][self.vx] << 1) % 256
        
        if self.debug_instructions:
            print("Set vx = vx*2")
            
    # 9xy0 - SNE Vx, Vy
    def skip_instruction_if_vx_not_equal_vy(self):
        # The values of Vx and Vy are compared, and if they are not equal, the program counter is increased by 2.
        if(self.registers['v'][self.vx] != self.registers['v'][self.vy]):
            self.registers['pc'] += 2
        
        if self.debug_instructions:
            print("Skip if vx != vy")
            
    # Annn - LD I, addr
    def set_I_to_nnn(self):
        # The value of register I is set to nnn.
        self.registers['I'] = self.opcode & 0x0fff
        
        if self.debug_instructions:
            print("Set I to nnn")
            
    # Bnnn - JP V0, addr
    def jump_to_nnn_sum_v0(self):
        # The program counter is set to nnn plus the value of V0.
        self.registers['pc'] = self.opcode & 0x0fff + self.registers['v'][0]
        
        if self.debug_instructions:
            print("Jump to nnn sum v0")
            
    # Cxkk - RND Vx, byte
    def set_vx_random_and_kk(self):
        # The interpreter generates a random number from 0 to 255, which is then ANDed with the value kk.
        # The results are stored in Vx.
        self.registers['v'][self.vx] = randint(0, 255) & (self.opcode & 0xff)
        
        if self.debug_instructions:
            print("Set vx random & kk")
            
    # Dxyn - DRW Vx, Vy, nibble
    def draw_sprite(self):
        # The interpreter reads n bytes from memory, starting at the address stored in I.
        # These bytes are then displayed as sprites on screen at coordinates (Vx, Vy).
        # Sprites are XORed onto the existing screen. If this causes any pixels to be erased,
        # VF is set to 1, otherwise it is set to 0. If the sprite is positioned so part of it is
        # outside the coordinates of the display, it wraps around to the opposite side of the screen.
        bytes_to_read = int(self.opcode & 0x00f)
        
        #Clear the register
        self.registers['v'][0xF] = 0

        # Read the bytes
        for offset in range(bytes_to_read):
            mask = 0x80

            byte_to_draw = self.memory[self.registers['I'] + offset]

            for index in range(7, -1, -1):
                xpos = (self.registers['v'][self.vx] + (7 - index)) % 64
                ypos = (self.registers['v'][self.vy] + offset) % 32

                previous_pixel_value = self.screen.get_pixel(xpos, ypos)
                self.screen.set_pixel(xpos, ypos, previous_pixel_value ^ ((byte_to_draw & mask) >> index))
                new_pixel_value = self.screen.get_pixel(xpos, ypos)

                #Move the mask
                mask = mask >> 1

                # A pixel has been erased
                if(previous_pixel_value == 1 and new_pixel_value == 0):
                    self.registers['v'][0xF] = 1

        # Do draw?
        self.screen.render_once()
        
        if self.debug_instructions:
            print("Draw")
            

    def cycle_e_function(self):
        function = self.opcode & 0x00FF

        # Ex9E - SKP Vx
        # Checks the keyboard, and if the key corresponding to the value of Vx is currently in the down position, PC is
        # increased by 2.
        if (function == 0x09E and self.input_handler.is_pressed(self.registers['v'][self.vx])):
            self.registers['pc'] += 2
       
            if self.debug_instructions:
                print("If key pressed, skip")
            

        # ExA1 - SKNP Vx
        # Checks the keyboard, and if the key corresponding to the value of Vx is currently in the up position, PC is
        # increased by 2.
        elif(function == 0x0A1 and not self.input_handler.is_pressed(self.registers['v'][self.vx])):
            self.registers['pc'] += 2
            
            if self.debug_instructions:
                print("If not key pressed, skip")
    # F Functions
    def cycle_f_function(self):
        function = self.opcode & 0x00FF
        # try:
        self.f_functions[function]()
        # except KeyError:
        #     print("Unknown f instruction: %X" % function)

    # Fx07 - LD Vx, DT
    def set_vx_to_delay_timer(self):
        # print("Fx07", self.vx, self.timers['delay'])
        # The value of DT is placed into Vx.
        self.registers['v'][self.vx] = self.timers['delay']
        
        if self.debug_instructions:
            print("Set vx = delay timer")
            
    # Fx0A - LD Vx, K
    def wait_for_keypress(self):
        print("Fx0A")
        # All execution stops until a key is pressed, then the value of that key is stored in Vx.
        pressed = -1

        while(pressed == -1):
            print("Loop")
            #Check keys
            self.screen.check_keys()
            
            for key_index in range(16):
                if (self.input_handler.is_pressed(key_index)):
                    pressed = key_index

        self.registers['v'][self.vx] = pressed

        if self.debug_instructions:
            print("Wait for keypress")
            
    # Fx15 - LD DT, Vx
    def set_delay_timer_to_vx(self):
        # DT is set equal to the value of Vx.
        self.timers['delay'] = self.registers['v'][self.vx]
        
        if self.debug_instructions:
            print("Set delay timer to vx")
            
    # Fx18 - LD ST, Vx
    def set_sound_timer_to_vx(self):
        # ST is set equal to the value of Vx.
        self.timers['sound'] = self.registers['v'][self.vx]
        
        if self.debug_instructions:
            print("Set sound timer to vx")
            
    # Fx1E - ADD I, Vx
    def set_I_I_sum_vx(self):
        # The values of I and Vx are added, and the results are stored in I.
        self.registers['I'] += self.registers['v'][self.vx]
        
        if self.debug_instructions:
            print("Set I += vx")
            
    # Fx29 - LD F, Vx
    def set_I_to_sprite_location_of_value_of_vx(self):
        # The value of I is set to the location for the hexadecimal sprite corresponding to the value of Vx.
        self.registers['I'] = self.registers['v'][self.vx] * 5
        
        if self.debug_instructions:
            print("Set I to sprite location of vx")
            
    # Fx33 - LD B, Vx
    def store_number_in_memory(self):
        # The interpreter takes the decimal value of Vx, and places the hundreds digit in memory at location in I,
        # the tens digit at location I+1, and the ones digit at location I+2.
        number_to_store = "{0:0=3d}".format(int(self.registers['v'][self.vx]))
        for index, char in enumerate(number_to_store):
            self.memory[self.registers['I'] + index] = int(char)

        if self.debug_instructions:
            print("Store number in memory")
            
    # Fx55 - LD [I], Vx
    def store_registers_in_memory(self):
        # print("Fx55")

        # The interpreter copies the values of registers V0 through Vx into memory, starting at the address in I.
        for i in range(self.vx + 1):
            self.memory[self.registers['I'] + i] = self.registers['v'][i]

        if self.debug_instructions:
            print("Store registers in memory")
            
    # Fx65 - LD Vx, [I]
    def load_registers_from_memory(self):
        # print("Fx65")

        # The interpreter reads values from memory starting at location I into registers V0 through Vx.
        for i in range(self.vx + 1):
            self.registers['v'][i] = self.memory[self.registers['I'] + i]
            

        if self.debug_instructions:
            print("Load number from memory")
            