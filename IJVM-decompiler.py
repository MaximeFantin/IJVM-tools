SPACE_CHAR: set = {" ", "\t"}
INSTRUCTIONS: dict = {0x00: "NOP", 0x10: "BIPUSH", 0x13: "LDCW", 0x15: "ILOAD", 0x36: "ISTORE", 0x57: "POP", 0x59: "DUP", 0x5f: "SWAP",
                      0x60: "IADD", 0x64: "ISUB", 0x7e: "IAND", 0x80: "IOR", 0x84: "IINC", 0x99: "IFEQ", 0x9b: "IFLT", 0x9f: "IFICMPEQ",
                      0xa7: "GOTO", 0xac: "IRETURN", 0xb6: "INVOKEVIRTUAL", 0xc4: "WIDE"}
SINGLE_INSTRUCTIONS: set = {0x00, 0x57, 0x59, 0x5f, 0x60, 0x64, 0x80, 0x84, 0xac}


def extractAddress(bytecode: str) -> dict:
    """Separate addresses from the bytecode.

    Args:
        bytecode (str): Input bytecode.

    Returns:
        dict: Dictionary containing both the starting address and the code.
    """

    extract: dict = {"address": None, "data": []}
    splitData: list = bytecode.split(" ")
    for elem in splitData:
        if elem:
            extract["address"] = elem
            break

    for ind in range(len(splitData)):
        if "Ox" in splitData[ind]:
            splitData[ind] = splitData[ind].replace("Ox", "0x")

        if splitData[ind] and splitData[ind] != extract["address"]:
            if '\n' in splitData[ind]:
                splitData[ind] = splitData[ind][:splitData[ind].index('\n')]
            extract["data"].append(eval(splitData[ind]))
    extract["address"] = eval(extract["address"])
    return extract


def toAddress(extractedCode: dict, addresse: int) -> int:
    """Search for a value from a specific address in an extracted code.

    Args:
        extractedCode (dict): Input extracted code.
        addresse (int): Address of the desired value.

    Returns:
        int: Value at the input address.
    """

    return extractedCode["data"][addresse - extractedCode["address"]]


def addressedDecompile(bytecode: str, constantPool: str) -> str:
    """Decompile IJVM code for addressed format.

    Args:
        bytecode (str): IJVM code.
        constantPool (str): Constant pool of the code.
    
    Returns:
        str: Decompiled IJVM code.
    """

    values: dict = extractAddress(bytecode)
    pool: dict = extractAddress(constantPool)
    dataList: list = values["data"]
    methodsAddresses: dict = {}
    instructionsString: str = ""

    mainEnded: bool = False
    curentAddress: int = values["address"]
    i: int = 0
    while i < len(dataList):
        curentAddress = values["address"] + i
        if not i and dataList[0] == 0xb6:
            instructionsString += ".main\n"
            instructionsString += ".var\n"
            for j in range(dataList[6]):
                instructionsString += f"{chr(97 + j)}\n"
            instructionsString += ".end-var\n"
            i = 7
            continue

        if curentAddress in methodsAddresses:
            if not mainEnded:
                instructionsString += ".end-main\n"
                mainEnded = True
            else:
                instructionsString += ".end-method\n"
            instructionsString += f".method {methodsAddresses[curentAddress]}("
            for j in range(dataList[i + 1] - 1):
                if not j:
                    instructionsString += "a"
                else:
                    instructionsString += f",{chr(97 + j)}"
            instructionsString += ")\n"
            instructionsString += ".var\n"
            for j in range(dataList[i + 3]):
                instructionsString += f"{chr(97 + dataList[i + 1] - 1 + j)}\n"
            instructionsString += ".end-var\n"
            i += 4
            continue


        if dataList[i] in SINGLE_INSTRUCTIONS:
            instructionsString += f"{INSTRUCTIONS[dataList[i]]}\n"
        else:
            match ins := INSTRUCTIONS[dataList[i]]:
                case "BIPUSH":
                    instructionsString += f"{ins} {dataList[i + 1]}\n"
                    i += 1
                case "ILOAD":
                    instructionsString += f"{ins} {chr(96 + dataList[i + 1])}\n"
                    i += 1
                case "ISTORE":
                    instructionsString += f"{ins} {chr(96 + dataList[i + 1])}\n"
                    i += 1
                case "IINC":
                    instructionsString += f"{ins} {chr(96 + dataList[i + 1])} {dataList[i + 2]}\n"
                    i += 2
                case "INVOKEVIRTUAL":
                    instructionsString += f"{ins} m{dataList[i + 2]}\n"
                    methodsAddresses[toAddress(pool, dataList[i + 2])] = f"m{dataList[i + 2]}"
                    i += 2

        i += 1

    if mainEnded:
        instructionsString += ".end-method"
    else:
        instructionsString += ".end-main"
    
    return instructionsString


def decompile(bytecode: str, constantPool: str = "", format: str = "addressed") -> str:
    """Generate an IJVM code based on IJVM compiled binary.

    Args:
        bytecode (str): Inpute compiled IJVM.
        constantPool (str, optional): Constant pool binaries. Defaults to "".
        format (str, optional): Format of the provided binary code, can be <"addressed" | "raw">. Defaults to "addressed".

    Returns:
        str: IJVM code corresponding to the provided input.
    """

    match format:
        case "addressed":
            return addressedDecompile(bytecode, constantPool)



print(decompile(
"""0x40000 0xb6 0x00 0x01 0x00
0x40004 0x01 0x00 0x03 0x10
0x40008 0x0a 0x36 0x01 0x10
0x4000c 0x40 0x10 0x05 0x15
0x40010 0x01 0xb6 0x00 0x02
0x40014 0x10 0x40 0x10 0x05
0x40018 0x15 0x01 0xb6 0x00
0x4001c 0x02 0x60 0x00 0x03
0x40020 0x00 0x01 0x15 0x01
0x40024 0x59 0x15 0x02 0x59
0x40028 0x60 0x60 0x60 0xac""",
constantPool=
"""
0x0 Ox0
0x1 Ox40003
0x2 Ox4001e"""
))
