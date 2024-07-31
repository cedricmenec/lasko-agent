from typing import List
from pydantic import BaseModel

class PrinterModel(BaseModel):
    """
    Represents a printer model with the following attributes:
    
    - `id`: A unique identifier for the printer.
    - `name`: The name of the printer.
    - `status`: The current status of the printer (e.g. "online", "offline", "error").
    - `capabilities`: A dictionary of the printer's capabilities, such as supported media types, print resolutions, etc.
    """
    id: str
    name: str
    status: str
    capabilities: dict


class PrinterListModel(BaseModel):
    """
    Represents a list of `PrinterModel` objects.
    
    - `printers`: A list of `PrinterModel` objects representing the printers.
    """
    printers: List[PrinterModel]
