import json
import os


class Settings:
    def __init__(self, setting_file='setting_file.json'):
        self.collection = dict()

        self.filename = setting_file
        self.default_settings = {
            "THRSH_MIN": 30,
            "MIN_OBJ": 215,
            "MAX_OBJ": 250,
            "DWN_LINE": 290,
            "TOP_LINE": 195
        }

        self.load_from_file()

    def __getitem__(self, field):
        return self.collection.get(field)

    def load_from_file(self):
        try:
            if os.path.exists(self.filename):
                with open(self.filename, "r") as file:
                    file_settings = json.load(file)

                if self.check_new_settings(file_settings):
                    self.collection = file_settings
                    return True
            raise ValueError
        except Exception:
            self.set_default_settings_active()
            return False

    def check_new_settings(self, new_values):
        if isinstance(new_values, dict):
            fields_error = len(set(self.default_settings.keys()) - set(new_values.keys())) != 0
            values_error = min(new_values.values()) <= 0
            if not (values_error or fields_error):
                return True
        return False

    def write_file(self):
        try:
            with open(self.filename, "w") as file:
                json.dump(self.collection, file)
            return True
        except Exception:
            return False

    def set_default_settings_active(self):
        self.collection = self.default_settings.copy()
