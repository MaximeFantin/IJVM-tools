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
    extractedData: dict = {"address": None, "data": []}
    for line in splitedText:
        splitedLine: list = line.split(" ")
        lineStarted: bool = False
        for byte in splitedLine:
            if not byte:
                continue
            val: int = toHex(byte)
            if not lineStarted:
                lineStarted = True
                if extractedData["address"] == None:
                    extractedData["address"] = val
                continue
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


def inMethodDefSection(pointer: int, bytecode: dict, constantPool: dict) -> bool:
    """Check if the pointer is in a method definition section.

    Args:
        pointer (int): Actual position of the pointer.
        bytecode (dict): Dictionary containing the bytecode.
        constantPool (dict): Dictionary containing the constant pool.

    Returns:
        bool: True if the pointer is in a method definition section, False otherwise.
    """

    defSectionAddrs: list[int] = []
    for addr in constantPool["data"]:
        if (a := addr - bytecode["address"]) > 0:
            if pointer in range(a, a + 4):
                return True

    return False


def executeInstruction(stack: list, pointer: int, bytecode: dict, constantPool: dict) -> int:
    """Take an instruction and executes it.

    Args:
        stack (list): Actual state of the stack.
        pointer (int): Position of the pointer in the stack.
        bytecode (list): IJVM bytecode.
        constantPool (list): Constant pool of the IJVM bytecode.

    Returns:
        int: New position of the pointer.
    """

    match INSTRUCTIONS[bytecode["data"][pointer]]:
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
            TOS: int = stack.pop()
            stack[-1] += TOS
            return pointer + 1

        case "ISUB":
            TOS: int = stack.pop()
            stack[-1] -= TOS
            return pointer + 1

        case "IAND":
            TOS: int = stack.pop()
            stack[-1] &= TOS
            return pointer + 1

        case "IOR":
            TOS: int = stack.pop()
            stack[-1] |= TOS
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
            stack.pop()
            methodAddr: int = (len(stack) - 1) | 0x2_000_000
            returnPointer: int = stack.pop() - bytecode["address"]
            while stack[-1] != methodAddr:
                stack.pop()
            stack[-1] = returnValue
            return returnPointer

        case "INVOKEVIRTUAL":
            methodAddr: int = constantPool["data"][
                (bytecode["data"][pointer + 1] << 8 | bytecode["data"][pointer + 2]) - constantPool["address"]
            ]
            methodPointer = methodAddr - bytecode["address"]
            varAmount: int = bytecode["data"][methodPointer + 2] << 8 | bytecode["data"][methodPointer + 3]
            envDefinition: int = 0x2_000_000 + len(stack) + varAmount
            argsAmount: int = bytecode["data"][methodPointer] << 8 | bytecode["data"][methodPointer + 1]
            stack[-argsAmount] = envDefinition
            for _ in range(varAmount):
                stack.append(0)
            #stack.append(methodAddr)
            stack.append(bytecode["address"] + pointer + 3)
            stack.append(0x2_000_000)
            return methodPointer + 4

        case "WIDE":
            raise NotImplementedError("WIDE instruction is not supported yet.")


def addressedRun(bytecode: str, constantPool: str = "") -> list:
    """Takes an IJVM bytecode in addressed format, runs it and returns the stack state.

    Args:
        bytecode (str): IJVM bytecode.
        constantPool (str, optional): Constant pool of the IJVM bytecode. Defaults to "".

    Returns:
        list: State of the stack after the execution of the bytecode.
    """

    bytecodeData: dict = extractData(bytecode)
    constantPoolData: dict = extractData(constantPool)
    stack: list = [0]
    pointer: int = 0

    while pointer < len(bytecodeData["data"]) and not inMethodDefSection(pointer, bytecodeData, constantPoolData):
        if bytecodeData["data"][pointer] not in INSTRUCTIONS:
            pointer += 1
            continue
        pointer = executeInstruction(stack, pointer, bytecodeData, constantPoolData)
    
    return stack


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
            outputStack: list = addressedRun(bytecode, constantPool)
        case "raw":
            raise NotImplementedError("Raw format is not supported yet.")

    if outputFile:
        with open(outputFile, "w") as file:
            for item in outputStack:
                file.write(f"{item}\n")

    return outputStack


print(run(
"""
0x40000 0xb6 0x00 0x01 0x00
0x40004 0x01 0x00 0x03 0x10
0x40008 0x0a 0x36 0x01 0x10
0x4000c 0x40 0x10 0x05 0x15
0x40010 0x01 0xb6 0x00 0x02
0x40014 0x10 0x40 0x10 0x06
0x40018 0xb6 0x00 0x03 0x60
0x4001c 0x00 0x03 0x00 0x01
0x40020 0x15 0x01 0x59 0x15
0x40024 0x02 0x60 0x60 0xac
0x40028 0x00 0x02 0x00 0x01
0x4002c 0x15 0x01 0x10 0x02
0x40030 0x60 0xac 0x00 0x00
""",
constantPool=
"""
0x0 Ox0
0x1 Ox40003
0x2 Ox4001c
0x3 Ox40028
"""
))
