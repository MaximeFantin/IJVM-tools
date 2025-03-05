
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
        for byte in splitedLine:
            if not byte:
                continue
            if not extractedData["address"]:
                extractedData["address"] = toHex(byte)
                continue
            if not (byte & 0x40000):
                extractedData["data"].append(toHex(byte))
    
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
