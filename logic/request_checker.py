"""A module for checking requests"""

import os
from loguru import logger
from logic.parser import parse_request

logger.remove()
logger.add("log/hystory.log", format="<white>{time:YYYY-MM-DD HH:mm:ss}</white> | <level>{level}</level> | <level>{message}</level>", rotation="10MB", compression="gz")

SEPARATOR = "\r\n\r\n"
PROTOCOL = "РКСОК/1.0"
DATABASE_PATH = os.getcwd()

response_status = {
    "OK": "НОРМАЛДЫКС",
    "NOT_FOUND": "НИНАШОЛ",
    "NOT_APPROOVED": "НИЛЬЗЯ",
    "INCORRECT_REQUEST": "НИПОНЯЛ"
}

protocol_instructions = ("GET", "WRITE", "DELETE",)


def check_request(request: str) -> bool:
    """Will check protocol, lenght of name and instruciton"""
    parsed_request = parse_request(request)
    if parsed_request['instruction'] not in protocol_instructions:
        return False
    if parsed_request["protocol"] != PROTOCOL:
        return False
    if len(parsed_request["addressee"]) > 30:
        return False
    return True

def get_response(request: str) -> str:
    """will return a response for request from the client"""
    addressee_list = [file_name.split(".")[0] for file_name in os.listdir(DATABASE_PATH)]
    logger.info(f"Data form request_hendler: {request}")
    parsed_request = parse_request(request)
    instruction = parsed_request["instruction"]
    addressee = parsed_request["addressee"]
    addressee_data = parsed_request["data"]
    if instruction in ("GET", "DELETE") and addressee not in addressee_list:
        response = f"{response_status['NOT_FOUND']} {PROTOCOL}{SEPARATOR}"
    elif instruction == "GET":
        with open(f"{DATABASE_PATH}/{addressee}.txt", mode='r', encoding="UTF-8") as data_file:
            addressee_data = data_file.read()
        logger.info(f"Data from the database: {addressee_data}")
        response = f"{response_status['OK']} {PROTOCOL}\r\n{addressee_data}{SEPARATOR}"
    elif instruction == "WRITE":
        logger.info(f"Will save: {addressee_data}")
        with open(f"{DATABASE_PATH}/{addressee}.txt", mode="w", encoding="UTF-8") as data_file:
            data_file.write(addressee_data)
        response = f"{response_status['OK']} {PROTOCOL}{SEPARATOR}"
    elif instruction == "DELETE":
        os.remove(f"{DATABASE_PATH}/{addressee}.txt")
        response = f"{response_status['OK']} {PROTOCOL}{SEPARATOR}"
    return response
