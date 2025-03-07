INSTRUCTIONS: dict = {
    0x00: "NOP",
    0x10: "BIPUSH",
    0x13: "LDCW",
    0x15: "ILOAD",
    0x36: "ISTORE",
    0x57: "POP",
    0x59: "DUP",
    0x5F: "SWAP",
    0x60: "IADD",
    0x64: "ISUB",
    0x7E: "IAND",
    0x80: "IOR",
    0x84: "IINC",
    0x99: "IFEQ",
    0x9B: "IFLT",
    0x9F: "IFICMPEQ",
    0xA7: "GOTO",
    0xAC: "IRETURN",
    0xB6: "INVOKEVIRTUAL",
    0xC4: "WIDE",
}


def extractData(bytecode: str) -> dict:
    """Extracts the data from the bytecode.

    Args:
        bytecode (str): Compiled IJVM bytecode.

    Returns:
        dict: A dictionary containing the starting address and the data.
    """

    splitedText: list = bytecode.split("\n")
    extractedData: dict = {"address": None, "addressOffset": 0, "data": []}
    for line in splitedText:
        splitedLine: list = line.split(" ")
        for byte in splitedLine:
            if not byte:
                continue
            val: int = toHex(byte)
            if not extractedData["address"]:
                i: int = 0
                while val >> i > 1:
                    i += 1
                extractedData["address"] = val
                extractedData["addressOffset"] = 1 << i
                continue
            if not (val & extractedData["addressOffset"]):
                extractedData["data"].append(val)
    
    return extractedData


def toHex(byte: str) -> int:
    """Takes a hex number written as a string and returns it as an integer.

    Args:
        byte (str): Input hex number.

    Returns:
        int: Integer representation of the hex number.
    """

    if "Ox" in byte:
        byte = byte.replace("Ox", "0x")

    return int(byte, 16)


def signed2c(byte0: int, byte1: int = None) -> int:
    """Convert bytes to a signed 2's complement number.

    Args:
        byte0 (int): First byte.
        byte1 (int): Second byte.

    Returns:
        int: Signed 2's complement number.
    """

    if byte1 is not None:
        byteCouple: int = (
            byte0 << 8 | byte1
        )  # Combining the two bytes into a single integer
        if byteCouple & 0x8000:
            return -(
                (byteCouple ^ 0xFFFF) + 1
            )  # If negative, return the 2's complement
    else:
        byteCouple: int = byte0
        if byteCouple & 0x80:
            return -((byteCouple ^ 0xFF) + 1)
    return byteCouple


def executeInstruction(instruction: int, stack: list, pointer: int, bytecode: dict, constantPool: dict) -> int:
    """Take an instruction and executes it.

    Args:
        instruction (int): Value corresponding to the instruction.
        stack (list): Actual state of the stack.
        pointer (int): Position of the pointer in the stack.
        constantPool (list): Constant pool of the IJVM bytecode.

    Returns:
        int: New position of the pointer.
    """

    match INSTRUCTIONS[instruction]:
        case "NOP":
            return pointer + 1
        case "BIPUSH":
            stack.append(signed2c(
                bytecode["data"][pointer + 1]
                ))
            return pointer + 2

        case "LDCW":
            stack.append(signed2c(
                constantPool["data"][
                    (bytecode["data"][pointer + 1] << 8) + bytecode["data"][pointer + 2]
                    ]
                ))
            return pointer + 3

        case "ILOAD":
            varPos: int = bytecode["data"][pointer + 1]
            varAddr: int = len(stack) - 1
            while stack[varAddr] != 0x2_000_000:
                varAddr -= 1
            varAddr -= 1
            while not (stack[varAddr] & 0x2_000_000):
                varAddr -= 1
            varAddr += varPos

            stack.append(stack[varAddr])
            return pointer + 2

        case "ISTORE":
            varPos: int = bytecode["data"][pointer + 1]
            varAddr: int = len(stack) - 1
            while stack[varAddr] != 0x2_000_000:
                varAddr -= 1
            varAddr -= 1
            while not (stack[varAddr] & 0x2_000_000):
                varAddr -= 1
            varAddr += varPos

            stack[varAddr] = stack.pop()
            return pointer + 2

        case "POP":
            stack.pop()
            return pointer + 1

        case "DUP":
            stack.append(stack[-1])
            return pointer + 1

        case "SWAP":
            stack[-1], stack[-2] = stack[-2], stack[-1]
            return pointer + 1

        case "IADD":
            stack[-2] += stack.pop()
            return pointer + 1

        case "ISUB":
            stack[-2] -= stack.pop()
            return pointer + 1

        case "IAND":
            stack[-2] &= stack.pop()
            return pointer + 1

        case "IOR":
            stack[-2] |= stack.pop()
            return pointer + 1

        case "IINC":
            varPos: int = bytecode["data"][pointer + 1]
            varAddr: int = len(stack) - 1
            while stack[varAddr] != 0x2_000_000:
                varAddr -= 1
            varAddr -= 1
            while not (stack[varAddr] & 0x2_000_000):
                varAddr -= 1
            varAddr += varPos

            stack[varAddr] += signed2c(bytecode["data"][pointer + 2])
            return pointer + 3

        case "IFEQ":
            if stack.pop() == 0:
                return pointer + signed2c(bytecode["data"][pointer + 1], bytecode["data"][pointer + 2])
            return pointer + 3

        case "IFLT":
            if stack.pop() < 0:
                return pointer + signed2c(bytecode["data"][pointer + 1], bytecode["data"][pointer + 2])
            return pointer + 3

        case "IFICMPEQ":
            if stack.pop() == stack.pop():
                return pointer + signed2c(bytecode["data"][pointer + 1], bytecode["data"][pointer + 2])
            return pointer + 3

        case "GOTO":
            return pointer + signed2c(bytecode["data"][pointer + 1], bytecode["data"][pointer + 2])

        case "IRETURN":
            returnValue: int = stack.pop()
            while stack[-1] != 0x2_000_000:
                stack.pop()
            methodAddr: int = (len(stack) - 2) | 0x2_000_000
            returnPointer: int = stack.pop() - bytecode["address"]
            while stack[-1] != methodAddr:
                stack.pop()
            stack[-1] = returnValue
            return returnPointer
        
        case "INVOKEVIRTUAL":
            raise NotImplementedError("INVOKEVIRTUAL instruction is not supported yet.")
        
        case "WIDE":
            raise NotImplementedError("WIDE instruction is not supported yet.")


def run(bytecode: str, constantPool: str = "", *, format: str = "addressed", outputFile: str = None) -> list:
    """Takes an IJVM bytecode, runs it and returns the stack state.

    Args:
        bytecode (str): Inpute compiled IJVM.
        constantPool (str, optional): Constant pool binaries. Defaults to "".
        format (str, optional): Format of the provided binary code, can be <"addressed" | "raw">. Defaults to "addressed".
        outputFile (str, optional): File where the output is writen. Defaults to None.

    Returns:
        list: State of the stack after the execution of the bytecode.
    """

    match format:
        case "addressed":
            raise NotImplementedError("Addressed format is not supported yet.")
        case "raw":
            raise NotImplementedError("Raw format is not supported yet.")


print(extractData(
"""
0x40000 0xb6 0x00 0x01 0x00
0x40004 0x01 0x00 0x00 0x10
0x40008 0x00 0x10 0x06 0xb6
0x4000c 0x00 0x02 0x00 0x02
0x40010 0x00 0x00 0x15 0x01
0x40014 0x10 0x01 0x9f 0x00
0x40018 0x22 0x15 0x01 0x10
0x4001c 0x02 0x9f 0x00 0x1b
0x40020 0x10 0x00 0x15 0x01
0x40024 0x10 0x01 0x64 0xb6
0x40028 0x00 0x02 0x10 0x00
0x4002c 0x15 0x01 0x10 0x02
0x40030 0x64 0xb6 0x00 0x02
0x40034 0x60 0xa7 0x00 0x05
0x40038 0x10 0x01 0xac 0x00
"""
))
