"""A prarcer for request"""
import base64
from loguru import logger

logger.remove()
logger.add("log/hystory.log", format="<white>{time:YYYY-MM-DD HH:mm:ss}</white> | <level>{level}</level> | <level>{message}</level>", rotation="10MB", compression="gz")

instructions = {
    "ОТДОВАЙ": "GET",
    "УДОЛИ": "DELETE",
    "ЗОПИШИ": "WRITE",
}


def parse_request(request: str) -> dict:
    """Will return a dict with instructon, adressee and data"""
    parsed_request = {
        "instruction": None,
        "protocol": None,
        "addressee": None,
        "data": None,
    }
    split_request = request.split("\n", maxsplit=1)
    try:
        parsed_request["instruction"] = instructions[split_request[0].split(' ')[0]]
    except KeyError:
        parsed_request["instruction"] = "BAD_REQUEST"
    parsed_request["protocol"] = split_request[0].split(' ')[-1].strip()
    parsed_request["addressee"] = " ".join(split_request[0].split(' ')[1:-1]).strip()
    if parsed_request["instruction"] == "WRITE":
        parsed_request["data"] = split_request[1].strip()
    return parsed_request
