# core/composition_data.py
import json
import random

class Base:
    def __init__(self, type, data):
        self.type = type
        self.data = data

    def to_dict(self):
        return {'type': self.type, 'data': self.data}

class Decoration:
    def __init__(self, name, model_path=None):
        self.name = name
        self.model_path = model_path
        self.position = [0.0, 0.0, 0.0]
        self.rotation = [0.0, 0.0, 0.0]
        self.scale = [1.0, 1.0, 1.0]
        self.color = self._generate_random_color()

    def _generate_random_color(self):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        return (r / 255.0, g / 255.0, b / 255.0)

    def to_dict(self):
        return {
            'name': self.name,
            'model_path': self.model_path,
            'position': self.position,
            'rotation': self.rotation,
            'scale': self.scale,
            'color': self.color
        }

class Composition:
    def __init__(self):
        self.base = None
        self.decorations = []

    def set_base(self, base):
        self.base = base

    def add_decoration(self, decoration):
        self.decorations.append(decoration)

    def to_json(self):
        data = {}
        if self.base:
            data['base'] = self.base.to_dict()
        if self.decorations:
            data['decorations'] = [dec.to_dict() for dec in self.decorations]
        return json.dumps(data, indent=4)

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        composition = cls()
        if 'base' in data:
            composition.set_base(Base(data['base']['type'], data['base']['data']))
        if 'decorations' in data:
            for dec_data in data['decorations']:
                decoration = Decoration(
                    dec_data['name'],
                    dec_data.get('model_path')
                )
                decoration.position = dec_data.get('position', [0.0, 0.0, 0.0])
                decoration.rotation = dec_data.get('rotation', [0.0, 0.0, 0.0])
                decoration.scale = dec_data.get('scale', [1.0, 1.0, 1.0])
                decoration.color = tuple(dec_data.get('color', decoration.color)) # Сохраняем цвет, если есть
                composition.add_decoration(decoration)
        return composition