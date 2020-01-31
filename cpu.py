"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # register - 256 bytes of memory & 8 general purpose registers
        self.pc = 0
        self.running = True
        self.ram = [0] * 256
        self.reg = [0, 0, 0, 0, 0, 0, 0, 0xF4]
        self.fl = [0] * 8

    def load(self, filename):
        """Load a program into memory."""

        address = 0
        program = []

        # Read each binary line into program
        with open(filename) as f:
            for line in f:
                # Ignore comments
                comment_split = line.split("#")
                value = comment_split[0].strip()

                # Ignore blank lines
                if value == "":
                    continue

                program.append(value)

        for instruction in program:
            self.ram_write(instruction, address)
            address += 1

    def binary_string_to_decimal(self, binary_string):
        return int(binary_string, 2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            # Equal
            if self.reg[reg_a] == self.reg[reg_b]:
                self.fl[7] = 1
            # Less than
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.fl[5] = 1
            # Greater than
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl[6] = 1
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, address):
        """
        Accepts a RAM address and returns the value stored there
        """
        return str(self.ram[address])

    def ram_write(self, value, address):
        """
        Accepts a value and RAM address, then overwrites the value at that address
        """
        self.ram[address] = value

    def run(self):
        """Run the CPU."""
        # Run until it halts
        while self.running:

            # Find the number of arguments
            # Looks like from source files, I'll get strings,
            # but hard-coded program has real binary values
            command = self.ram_read(self.pc)

            # Instantiate Instruction Register
            ir = [command]

            # Do we need more arguments from memory?
            if command[:2] == "00":
                # No arguments are needed
                # Just change the PC
                self.pc += 1
            elif command[:2] == "01":
                # One argument needed
                operand_a = self.ram_read(self.pc + 1)
                # Add to ir
                ir.append(operand_a)
                # Change the PC
                self.pc += 2
            elif command[:2] == "10":
                # Two arguments needed
                operand_a = self.ram_read(self.pc + 1)
                operand_b = self.ram_read(self.pc + 2)
                # Add to ir
                ir.append(operand_a)
                ir.append(operand_b)
                # Change the PC
                self.pc += 3

            else:
                print("INVALID COMMAND")

            """Now everything for this operation is in ir"""

            # print("")
            # print(f"Command: {ir[0]}")
            # print("")

            # Execute Instructions

            # HLT
            if ir[0] == "00000001":
                # Change running to false
                self.running = False

            # LDI
            elif ir[0] == "10000010":
                # Get the vars
                register_address_binary_string = ir[1]
                value_binary_string = ir[2]

                # Convert vars to decimal value
                register_address = self.binary_string_to_decimal(register_address_binary_string)
                value = self.binary_string_to_decimal(value_binary_string)

                # Set register at address to specified value
                self.reg[register_address] = value

            # PRN
            elif ir[0] == "01000111":
                # Get the var
                register_address_binary_string = ir[1]

                # Convert vars to decimal value
                register_address = self.binary_string_to_decimal(register_address_binary_string)

                # Print value at register address
                print(self.reg[register_address])

            # ADD
            elif ir[0] == "10100000":
                # Get the register addresses
                reg_a = self.binary_string_to_decimal(ir[1])
                reg_b = self.binary_string_to_decimal(ir[2])

                # Call ALU MUL function
                self.alu("ADD", reg_a, reg_b)

            # MUL
            elif ir[0] == "10100010":
                # Get the register addresses
                reg_a = self.binary_string_to_decimal(ir[1])
                reg_b = self.binary_string_to_decimal(ir[2])

                # Call ALU MUL function
                self.alu("MUL", reg_a,reg_b)

            # PUSH
            elif ir[0] == "01000101":
                # Get the value to push
                register_address = int(self.binary_string_to_decimal(ir[1]))
                value = self.reg[register_address]

                # Decrement the SP
                self.reg[7] -= 1

                # Send the value to the address in RAM
                self.ram_write(value, self.reg[7])

            # POP
            elif ir[0] == "01000110":
                # Get the value SP is pointing to from RAM
                value = int(self.ram_read(self.reg[7]))
                
                # Get the register address to send it to
                address = self.binary_string_to_decimal(ir[1])
                
                # Write the value into register[address]
                self.reg[address] = value
                
                # Increment SP
                self.reg[7] += 1

            # CALL
            elif ir[0] == "01010000":
                # Push address of next command to stack
                value = self.pc
                # Decrement SP
                self.reg[7] -= 1
                # Send to Stack in RAM
                self.ram_write(value, self.reg[7])

                # Get the subroutine address
                reg_address = self.binary_string_to_decimal(ir[1])
                subroutine_address = self.reg[reg_address]

                # Jump to that location in RAM
                self.pc = subroutine_address

            # RET
            elif ir[0] == "00010001":
                # Get the value SP is pointing to in RAM
                value = int(self.ram_read(self.reg[7]))
                # Set PC back to that address
                self.pc = value

                # Increment SP
                self.reg[7] += 1

            # CMP
            elif ir[0] == "10100111":
                # Reset LGE flags??

                # Get register addresses
                reg_a = self.binary_string_to_decimal(ir[1])
                reg_b = self.binary_string_to_decimal(ir[2])

                # Call ALU MUL function
                self.alu("CMP", reg_a,reg_b)

            # JMP
            elif ir[0] == "01010100":
                # Convert register address
                reg_address = self.binary_string_to_decimal(ir[1])

                # Get new value
                value = self.reg[reg_address]

                # Set PC to that value
                self.pc = value

            # JEQ
            elif ir[0] == "01010101":
                # Check if `equal` flag is True
                if self.fl[7] == 1:
                    # Convert register address
                    reg_address = self.binary_string_to_decimal(ir[1])

                    # Get new value
                    value = self.reg[reg_address]

                    # Set PC to that value
                    self.pc = value

            # JNE
            elif ir[0] == "01010110":
                # Check if `equal` flag is clear
                if self.fl[7] == 0:
                    # Convert register address
                    reg_address = self.binary_string_to_decimal(ir[1])

                    # Get new value
                    value = self.reg[reg_address]

                    # Set PC to that value
                    self.pc = value

            else:
                print("INVALID COMMAND")