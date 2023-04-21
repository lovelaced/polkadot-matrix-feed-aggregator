# data_checkers/__init__.py

class DataChecker:
    def __init__(self, client, matrix_room_id, checker_config, logger):
        self.client = client
        self.matrix_room_id = matrix_room_id
        self.logger = logger

