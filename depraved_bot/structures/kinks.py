from pydantic import BaseModel

class RequiredKink(BaseModel):
    name: str
    id: int

class OptionalKink(BaseModel):
    name: str
    green: int
    yellow: int
    red: int

    def flatten(self):
        return self.green, self.yellow, self.red
