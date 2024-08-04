from datetime import datetime
from app.core.websockets.commands import CommandType
from app.models.printer import PrinterListModel
from app.services.printer_service import PrinterService

class RequestHandler:
    def __init__(self):
        self.printer_service = PrinterService()

    async def handle_request(self, command: str, payload: dict) -> dict:
        start_time = datetime.utcnow()

        if command == "health-check":
            response_payload = await self.handle_health_check()
        elif command == CommandType.GET_PRINTER_LIST.value:
            response_payload = await self.handle_get_printer_list()
        elif command == CommandType.GET_PRINTER_STATUS.value:
            response_payload = await self.handle_get_printer_status(payload)
        else:
            response_payload = {"error": f"Unknown command ({command})"}

        end_time = datetime.now(datetime.UTC)
        processing_time = (end_time - start_time).total_seconds()

        return {
            "payload": response_payload,
            "processing_time": processing_time,
            "status": "success" if "error" not in response_payload else "error"
        }

    async def handle_health_check(self) -> dict:
        return {"status": "healthy"}

    async def handle_get_printer_list(self) -> dict:
        printer_list: PrinterListModel = await self.printer_service.get_printer_list()
        return {"printers": printer_list.model_dump()["printers"]}

    async def handle_get_printer_status(self, payload: dict) -> dict:
        printer_id = payload.get("printer_id")
        printer_status = await self.printer_service.get_printer_status(printer_id)
        return printer_status