from utils.helpers import get_logger

log = get_logger(__name__, level=10)

class BaseSheet():
    def __init__(self, sheet_model):
        self.sheet_model = sheet_model
        self.output = 0
