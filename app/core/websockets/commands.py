from enum import Enum

class CommandType(Enum):
    GET_PRINTER_LIST = "get_printer_list"
    GET_PRINTER_STATUS = "get_printer_status"
    SUBMIT_PRINT_JOB = "submit_print_job"
    GET_PRINT_JOB_STATUS = "get_print_job_status"
    CANCEL_PRINT_JOB = "cancel_print_job"

class Command:
    def __init__(self, type: CommandType, payload: dict = None):
        self.type = type
        self.payload = payload or {}

    def to_dict(self):
        return {
            "type": self.type.value,
            "payload": self.payload
        }