import yaml

with open("config.yaml", "r") as stream:
    config = yaml.safe_load(stream)

class RequiredKink:
    def __init__(self, kink_config: dict):
        self.name = kink_config["name"]
        self.id = kink_config["id"]

    def __repr__(self):
        return f'<RequiredKink {self.name}, id={self.id}>'

class OptionalKink:
    def __init__(self, kink_config: dict):
        self.name = kink_config["name"]
        self.green = kink_config["green"]
        self.yellow = kink_config["yellow"]
        self.red = kink_config["red"]
    
    def __repr__(self):
        return f'<OptionalKink {self.name}, green={self.green} yellow={self.yellow} red={self.red}>'

    def flatten(self):
        return self.green, self.yellow, self.red
    
required_kinks = [RequiredKink(kink) for kink in config["kinks"]["required_kinks"]]
optional_kinks = [OptionalKink(kink) for kink in config["kinks"]["optional_kinks"]]
