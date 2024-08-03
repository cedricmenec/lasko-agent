import win32print
from typing import List
from app.models.printer import PrinterListModel, PrinterModel

class PrinterService:
        
    @staticmethod
    async def get_printer_list() -> PrinterListModel:
        """
        Retrieves a list of all available printers on the system.

        Returns:
            List[PrinterModel]: A list of PrinterModel objects representing the available printers.
        """
        printers = []
        try:
            for printer_info in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL, None, 1):
                printer_name = printer_info[2]
                printer_handle = win32print.OpenPrinter(printer_name)
                try:
                    printer_info = win32print.GetPrinter(printer_handle, 2)
                    status = printer_info['Status']
                    status_str = "Ready" if status == 0 else "Error"

                    printer = PrinterModel(
                        id=printer_name,
                        name=printer_name,
                        status=status_str,
                        capabilities={}
                        #capabilities={
                        #    "color": printer_info['Attributes'] & win32print.PRINTER_ATTRIBUTE_COLOR > 0,
                        #    "duplex": printer_info['Attributes'] & win32print.PRINTER_ATTRIBUTE_DUPLEX > 0,
                        #}
                    )
                    printers.append(printer)
                finally:
                    win32print.ClosePrinter(printer_handle)
        except Exception as e:
            # Log the error
            print(f"Error retrieving printer list: {str(e)}")
            # In a production environment, you might want to use a proper logging system
            # and possibly raise a custom exception to be handled by the API layer

        return PrinterListModel(printers=printers)


    async def get_printer_status(self, printer_id: str) -> dict:
        # Implement logic to get printer status
        return {"status": "online"}

    async def submit_print_job(self, job_data: dict) -> dict:
        # Implement logic to submit print job
        return {"job_id": "job1", "status": "submitted"}

    async def get_print_job_status(self, job_id: str) -> dict:
        # Implement logic to get print job status
        return {"job_id": job_id, "status": "printing"}

    async def cancel_print_job(self, job_id: str) -> dict:
        # Implement logic to cancel print job
        return {"job_id": job_id, "status": "cancelled"}