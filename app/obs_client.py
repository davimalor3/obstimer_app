import asyncio
import logging

import simpleobsws

logger = logging.getLogger(__name__)


class OBSClient:
    def __init__(self, host="localhost", port=4455, password=""):
        self.url = f"ws://{host}:{port}"
        self.password = password
        self.client = None

    async def connect(self):
        identification_parameters = simpleobsws.IdentificationParameters(
            ignoreNonFatalRequestChecks=False
        )

        self.client = simpleobsws.WebSocketClient(
            url=self.url,
            password=self.password,
            identification_parameters=identification_parameters,
        )

        await asyncio.wait_for(self.client.connect(), timeout=10.0)
        logger.info("Conectado ao OBS")
        await asyncio.sleep(1.0)

        response = await self.client.call(simpleobsws.Request("GetVersion"))
        return response.ok()

    async def start_recording(self):
        return await self._call_request("StartRecord")

    async def stop_recording(self):
        return await self._call_request("StopRecord")

    async def is_recording(self):
        response = await self.client.call(simpleobsws.Request("GetRecordStatus"))
        return response.ok() and response.responseData.get("outputActive", False)

    async def disconnect(self):
        if self.client:
            await self.client.disconnect()

    async def _call_request(self, request_type):
        try:
            response = await self.client.call(simpleobsws.Request(request_type))
            return response.ok()

        except Exception as e:
            logger.error(f"Erro ao executar {request_type}: {e}")
            return False
