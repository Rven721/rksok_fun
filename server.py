"""some kind of small async server"""
import asyncio
from loguru import logger
from logic.request_checker import  check_request, get_response

logger.remove()
logger.add("log/hystory.log", format="<white>{time:YYYY-MM-DD HH:mm:ss}</white> | <level>{level}</level> | <level>{message}</level>", rotation="10MB", compression="gz")

HOST = "192.168.0.2"
#HOST = "127.0.0.1"
PORT = 9090
PERMIT_HOST = "vragi-vezde.to.digital"
#PERMIT_HOST = "127.0.0.1"
PERMIT_PORT = 51624
PROTOCOL = "РКСОК/1.0"
ENCODING = "UTF-8"
SEPARATOR = "\r\n\r\n"

request_verb = {
    "ОТВАВАЙ": "GET",
    "УДОЛИ": "DELETE",
    "ЗАПИШИ":"WRITE",
}


async def ask_permit(request):
    """Will check if the request is valid and return permition or denay with text of resopse"""
    reader, writer = await asyncio.open_connection(PERMIT_HOST, PERMIT_PORT)
    writer.write(request.encode(ENCODING))
    await writer.drain()
    permit_response = await reader.readuntil(SEPARATOR.encode(ENCODING))
    response =  permit_response.decode(ENCODING)
    return response

@logger.catch
async def request_handler(reader, writer):
    """will receivi a request from the socket, ask for prmit and send the response"""
    logger.info("New connection")
    request = b""
    try:
        while not SEPARATOR.encode() in request:
            request_part = b""
            try:
                request_part = await reader.readuntil(SEPARATOR.encode(ENCODING))
            except asyncio.exceptions.LimitOverrunError as err:
                logger.info("Got a vary long request. Erasing buffer and resturting...")
                request_part = await reader.read(err.consumed)
                logger.info(f"{request_part.decode()}")
            request += request_part
        logger.info(f"Got new request: {request.decode(ENCODING)}")
        correct_request = check_request(request.decode(ENCODING))
        if not correct_request:
            logger.warning("Bad request")
            response = f"НИПОНЯЛ {PROTOCOL}{SEPARATOR}"
        else:
            permit_request = f"АМОЖНА? {PROTOCOL}\r\n{request.strip().decode(ENCODING)}{SEPARATOR}"
            try:
                logger.info(f"Ask for permit:\n{permit_request}")
                permition = await ask_permit(permit_request)
            except ConnectionError:
                logger.error("Approvment server does not responde")
                response = "Товарищ майор отсутствует. Обратитесь позже."
            logger.info(permition)
            if permition.split(' ')[0] == "МОЖНА":
                logger.success(f"Apprevment text: {permition}")
                response = get_response(request.decode(ENCODING))
            else:
                logger.warning(f"Apprevment denied: {permition.strip()}")
                response = permition
    except asyncio.IncompleteReadError:
        logger.warning("Bad request")
        response = f"НИПОНЯЛ {PROTOCOL}{SEPARATOR}"
    logger.info(f"Sanding a response:\n{response}")
    writer.write(response.encode(ENCODING))
    await writer.drain()
    logger.info("Close conneciton\n")
    writer.close()
    await writer.wait_closed()

async def main():
    """Will start the server"""
    server = await asyncio.start_server(request_handler, HOST, PORT)
    async with server:
        await server.serve_forever()

asyncio.run(main())
