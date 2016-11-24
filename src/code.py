# import pyglet
# import sys
# from random import randint
#
#
# class Chip8(pyglet.window.Window):
#
#     def __init__(self):
#
#         # General use registers
#         self.vx = 0x00
#         self.vy = 0x00
#         self.vz = 0x00
#         self.v0 = 0x00
#
#         # Register used as a flag
#         self.vf = 0x00
#
#         # Used for memory addresses, we only use its 12 lowest bits
#         self.I = 0x00
#
#         self.key_inputs = [0] * 16
#         self.display_buffer = [0] * 64 * 32
#
#         self.memory = [0] * 4096
#
#         self.sound_timer = 0
#         self.delay_timer = 0
#
#         self.index = 0
#         self.pc = 0
#
#         self.stack = []
#
#         self.fonts = [0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
#            0x20, 0x60, 0x20, 0x20, 0x70,  # 1
#            0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
#            0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
#            0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
#            0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
#            0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
#            0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
#            0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
#            0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
#            0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
#            0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
#            0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
#            0xE0, 0x90, 0x90, 0x90, 0xE0,  # D
#            0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
#            0xF0, 0x80, 0xF0, 0x80, 0x80   # F
#         ]
#
#     def main(self):
#         self.initialize()
#         self.load_rom(sys.argv[1])
#
#         while not self.has_exit:
#             self.dispatch_events()
#             self.cycle()
#             self.draw()
#
#     def initialize(self):
#         # That should clear pyglet screen
#         self.clear()
#
#         # General use registers
#         self.vx = 0x00 # 8bit register
#         self.vy = 0x00 # 8bit register
#         self.vz = 0x00 # 8bit register
#         self.v0 = 0x00 # 8bit register
#
#         # Register used as a flag
#         self.vf = 0x00
#
#         # Used for memory addresses, we only use its 12 lowest bits
#         self.I = 0x00  # 16bit register
#
#         # RAM memory 4KB
#         self.memory = [0]*4096  # max 4096
#
#         # Screen
#         self.display_buffer = [0]*64*32  # 64*32
#
#         self.stack = []
#         self.key_inputs = [0]*16
#         self.opcode = 0
#         self.index = 0
#
#         self.delay_timer = 0
#         self.sound_timer = 0
#
#         self.pc = 0x200
#
#         i = 0
#         while i < 80:
#             # load 80-char font set
#             self.memory[i] = self.fonts[i]
#             i += 1
#
#     def load_rom(self, rom_path):
#         data = open(rom_path, 'rb').read()
#         for i, part in enumerate(data):
#             self.memory[0x200 + i] = part
#             print(hex(part))
#
#     def draw(self):
#         print("draw")
#
#     def cycle(self):
#         # Extract opcode from memory
#         self.opcode = self.memory[self.pc]
#
#         # Extract the parameters
#         self.vx = (self.opcode & 0x0f00) >> 8
#         self.vy = (self.opcode & 0x00f0) >> 4
#
#         # Execute opcode
#         try:
#             self.funcmap[self.opcode]()
#         except:
#             print("Unknown instruction: %X" % self.opcode)
#
#         # Increment program counter
#         self.pc += 2
#
#         # Decrement timers
#         if self.delay_timer > 0:
#             self.delay_timer -= 1
#
#         if self.sound_timer > 0:
#             self.sound_timer -= 1
#
#             if self.sound_timer == 0:
#                 print("Beep")
#
#     # Opcode implementations
#     # 00E0 - CLS
#     def clear_screen(self):
#         # Clear the display.
#         self.screen = [0] * 64 * 32
#         self.clear()
#
#     # 00EE - RET
#     def return_from_subroutine(self):
#         # The interpreter sets the program counter to the address at the top of the stack, then subtracts 1 from the stack pointer.
#         self.pc = self.stack.pop()
#
#     #1nnn - JP addr
#     def jump_to_location(self):
#
#         #The interpreter sets the program counter to nnn.
#         jump_address = self.opcode & 0x0fff
#
#         self.pc = jump_address
#
#     #2nnn - CALL addr
#     def call_subroutine(self):
#
#         #The interpreter increments the stack pointer, then puts the current PC on the top of the stack. The PC is then set to nnn.
#         self.stack.append(self.pc)
#
#         jump_address = self.opcode & 0x0fff
#
#         self.pc = jump_address
#
#     #3xkk - SE Vx, byte
#     def skip_instruction_if_vx_equal_kk(self):
#
#         #The interpreter compares register Vx to kk, and if they are equal, increments the program counter by 2.
#         kk = self.opcode & 0x00ff
#
#         if(self.vx == kk):
#
#             self.pc += 2
#
#     #4xkk - SNE Vx, byte
#     def skip_instruction_if_vx_notequal_kk(self):
#
#         #The interpreter compares register Vx to kk, and if they are not equal, increments the program counter by 2.
#         kk = self.opcode & 0x00ff
#
#         if(self.vx != kk):
#
#             self.pc += 2
#
#     #5xy0 - SE Vx, Vy
#     def skip_instruction_if_vx_equal_vy(self):
#
#         #The interpreter compares register Vx to register Vy, and if they are equal, increments the program counter by 2.
#         if(self.vx == self.vy):
#
#             self.pc += 2
#
#     #6xkk - LD Vx, byte
#     def set_vx(self):
#
#         #The interpreter puts the value kk into register Vx.
#         kk = self.opcode & 0x00ff
#
#         self.vx = kk
#
#     #7xkk - ADD Vx, byte
#     def increment_vx_kk_units(self):
#
#         #Adds the value kk to the value of register Vx, then stores the result in Vx.
#         kk = self.opcode & 0x00ff
#
#         self.vx += kk
#
#     #8xy0 - LD Vx, Vy
#     def set_vx_equal_vy(self):
#
#         #Stores the value of register Vy in register Vx.
#         self.vx = self.vy
#
#
#     #8xy1 - OR Vx, Vy
#     def set_vx_bitwise_or_vx_vy(self):
#
#         #Performs a bitwise OR on the values of Vx and Vy, then stores the result in Vx. A bitwise OR compares the corrseponding bits from two values, and if either bit is 1, then the same bit in the result is also 1. Otherwise, it is 0.
#         self.vx = self.vx | self.vy
#
#
#     #8xy2 - AND Vx, Vy
#     def set_vx_bitwise_and_vx_vy(self):
#
#         #Performs a bitwise AND on the values of Vx and Vy, then stores the result in Vx. A bitwise AND compares the corrseponding bits from two values, and if both bits are 1, then the same bit in the result is also 1. Otherwise, it is 0.
#         self.vx = self.vx & self.vy
#
#
#     #8xy3 - XOR Vx, Vy
#     def set_vx_bitwise_xor_vx_vy(self):
#
#         #Performs a bitwise exclusive OR on the values of Vx and Vy, then stores the result in Vx. An exclusive OR compares the corrseponding bits from two values, and if the bits are not both the same, then the corresponding bit in the result is set to 1. Otherwise, it is 0.
#         self.vx = self.vx ^ self.vy
#
#     #8xy4 - ADD Vx, Vy
#     def set_vx_sum_vx_vy(self):
#
#         #The values of Vx and Vy are added together. If the result is greater than 8 bits (i.e., > 255,) VF is set to 1, otherwise 0. Only the lowest 8 bits of the result are kept, and stored in Vx.
#
#         #Set the parity bit
#         if(self.vx > 0xff):
#             self.vf = 1
#
#         else:
#             self.vf = 0
#
#         #We just keep the lowest 8 bits
#         self.vx = self.vx + self.vy
#         self.vx &= 0x00ff
#
#     #8xy5 - SUB Vx, Vy
#     def set_vx_substraction_vx_vy(self):
#
#         #If Vx > Vy, then VF is set to 1, otherwise 0. Then Vy is subtracted from Vx, and the results stored in Vx.
#         if(self.vx > self.vy):
#             self.vf = 1
#
#         else:
#             self.vf = 0
#
#         self.vx -= self.vy
#
#     #8xy6 - SHR Vx {, Vy}
#     def set_vx_vx_divided_by_two(self):
#
#         #If the least-significant bit of Vx is 1, then VF is set to 1, otherwise 0. Then Vx is divided by 2.
#         self.vf = self.vx & 0x0001
#
#         #Divide by 2
#         self.vx = self.vx >> 1
#
#     #8xy7 - SUBN Vx, Vy
#     def set_vx_substraction_vy_vx(self):
#
#         #If Vy > Vx, then VF is set to 1, otherwise 0. Then Vx is subtracted from Vy, and the results stored in Vx.
#         if(self.vy > self.vx):
#             self.vf = 1
#
#         else:
#             self.vf = 0
#
#         self.vx = self.vy - self.vx
#
#     #8xyE - SHL Vx {, Vy}
#     def set_vx_vx_multiplied_by_two(self):
#
#         #If the most-significant bit of Vx is 1, then VF is set to 1, otherwise to 0. Then Vx is multiplied by 2.
#         most_significant_bit = self.vx & 0x8000 >> 15
#
#         if(most_significant_bit == 1):
#             self.vf = 1
#
#         else:
#             self.vf = 0
#
#         self.vf = self.vf << 1
#
#
#     #9xy0 - SNE Vx, Vy
#     def skip_instruction_if_vx_not_equal_vy(self):
#
#         #The values of Vx and Vy are compared, and if they are not equal, the program counter is increased by 2.
#         if(self.vx == self.vy):
#
#             self.pc += 2
#
#     #Annn - LD I, addr
#     def set_I_to_nnn(self):
#
#         #The value of register I is set to nnn.
#         self.I = self.opcode & 0x0fff
#
#     #Bnnn - JP V0, addr
#     def jump_to_nnn_sum_v0(self):
#
#         #The program counter is set to nnn plus the value of V0.
#         self.pc = self.opcode & 0x0fff + self.v0
#
#     #Cxkk - RND Vx, byte
#     def set_vx_random_and_kk(self):
#
#         #The interpreter generates a random number from 0 to 255, which is then ANDed with the value kk.
#         #The results are stored in Vx.
#         self.vx = (randint() % 255) & (self.opcode & 0x00ff)
#
#
#     #Dxyn - DRW Vx, Vy, nibble
#     def draw_sprite(self):
#
#         #The interpreter reads n bytes from memory, starting at the address stored in I.
#         #These bytes are then displayed as sprites on screen at coordinates (Vx, Vy).
#         #Sprites are XORed onto the existing screen. If this causes any pixels to be erased,
#         #VF is set to 1, otherwise it is set to 0. If the sprite is positioned so part of it is
#         #outside the coordinates of the display, it wraps around to the opposite side of the screen.
#
#         bytes_to_read = int(self.opcode & 0x00f)
#
#         #Read the bytes
#         for offset in range(bytes_to_read):
#
#             mask = 0x80
#
#             byte_to_draw = self.memory[self.I + offset]
#
#             for index in range(8):
#
#                 xpos = (self.vx + index) % 64
#                 ypos = (self.vy + offset) % 32
#
#                 previous_pixel_value = self.screen[xpos][ypos]
#
#                 self.screen[xpos][ypos] ^= (byte_to_draw & mask) >> (8 - index)
#
#                 new_pixel_value = self.screen[xpos][ypos]
#
#                 #Move the mask
#                 mask = mask >> 1
#
#                 #A pixel has been erased
#                 if(previous_pixel_value == 1 and new_pixel_value == 0):
#                     self.vf = 1
#
#                 else:
#                     self.vf = 0
#
#
#     #Ex9E - SKP Vx
#     def skip_instruction_if_key_with_value_vx_pressed(self):
#
#         #Checks the keyboard, and if the key corresponding to the value of Vx is currently in the down position, PC is increased by 2.
#         if(self.key_inputs[self.vx] == 1):
#             self.pc +=2
#
#
#     #ExA1 - SKNP Vx
#     def skip_instruction_if_key_with_value_vx_not_pressed(self):
#
#         #Checks the keyboard, and if the key corresponding to the value of Vx is currently in the up position, PC is increased by 2.
#         if(self.key_inputs[self.vx] != 1):
#             self.pc +=2
#
#     #Fx07 - LD Vx, DT
#     def set_vx_to_delay_timer(self):
#
#         #The value of DT is placed into Vx.
#         self.vx = self.delay_timer
#
#
#     #Fx0A - LD Vx, K
#     def wait_for_keypress(self):
#
#         #All execution stops until a key is pressed, then the value of that key is stored in Vx.
#         pressed = -1
#
#         while(pressed == -1):
#             for key_index, key_value in zip(range(16), self.key_inputs):
#
#                 if(key_value == 1):
#
#                     pressed = key_index
#
#         self.vx = pressed
#
#     # Fx15 - LD DT, Vx
#     def set_delay_timer_to_vx(self):
#
#         # DT is set equal to the value of Vx.
#         self.delay_timer = self.vx
#
#
#     # Fx18 - LD ST, Vx
#     def set_sound_timer_to_vx(self):
#
#         # ST is set equal to the value of Vx.
#         self.sound_timer = self.vx
#
#     # Fx1E - ADD I, Vx
#     def set_I_I_sum_vx(self):
#
#         # The values of I and Vx are added, and the results are stored in I.
#         self.I += self.vx
#
#
#     # Fx29 - LD F, Vx
#     def set_I_to_sprite_location_of_value_of_vx(self):
#
#         # The value of I is set to the location for the hexadecimal sprite corresponding to the value of Vx.
#         self.I = int(self.vx) * 5
#
#     # Fx33 - LD B, Vx
#     def store_number_in_memory(self):
#
#         # The interpreter takes the decimal value of Vx, and places the hundreds digit in memory at location in I,
#         # the tens digit at location I+1, and the ones digit at location I+2.
#         number_to_store = str(int(self.vx))
#
#         for index, char in zip(range(3), number_to_store):
#
#             self.memory[self.I + index] = hex(int(char))
#
#     # Fx55 - LD [I], Vx
#     def store_registers_in_memory(self):
#
#         # The interpreter copies the values of registers V0 through Vx into memory, starting at the address in I.
#
#         # TODO: Refactor
#         self.memory[self.I]     = self.vx
#         self.memory[self.I + 1] = self.vy
#         self.memory[self.I + 2] = self.vz
#         self.memory[self.I + 3] = self.v0
#
#     # Fx65 - LD Vx, [I]
#     def load_registers_from_memory(self):
#
#         # The interpreter reads values from memory starting at location I into registers V0 through Vx.
#
#         #TODO: Refactor
#         self.vx = self.memory[self.I]
#         self.vy = self.memory[self.I + 1]
#         self.vz = self.memory[self.I + 2]
#         self.v0 = self.memory[self.I + 3]
#
# if __name__ == "__main__":
#     chip8 = Chip8()
#     chip8.main()