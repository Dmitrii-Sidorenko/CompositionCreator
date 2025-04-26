import unittest
from core.composition_data import Base, Decoration, Composition
import json

class TestCompositionData(unittest.TestCase):

    def test_base_creation(self):
        base = Base("file", "base.obj")
        self.assertEqual(base.type, "file")
        self.assertEqual(base.data, "base.obj")

    def test_base_to_dict(self):
        base = Base("file", "base.obj")
        expected_dict = {"type": "file", "data": "base.obj"}
        self.assertEqual(base.to_dict(), expected_dict)

    def test_decoration_creation(self):
        decoration = Decoration("sphere", "sphere.obj")
        self.assertEqual(decoration.name, "sphere")
        self.assertEqual(decoration.model_path, "sphere.obj")
        self.assertEqual(decoration.position, [0.0, 0.0, 0.0])
        self.assertEqual(decoration.rotation, [0.0, 0.0, 0.0])
        self.assertEqual(decoration.scale, [1.0, 1.0, 1.0])
        self.assertIsNotNone(decoration.color) # Проверяем, что цвет генерируется

    def test_decoration_to_dict(self):
        decoration = Decoration("sphere", "sphere.obj") # Убрали передачу color
        # Цвет генерируется случайно, поэтому мы не можем точно предсказать его.
        # Проверим только наличие остальных ключей и типов.
        decoration_dict = decoration.to_dict()
        expected_keys = {"name", "model_path", "position", "rotation", "scale", "color"}
        self.assertEqual(set(decoration_dict.keys()), expected_keys)
        self.assertEqual(decoration_dict["name"], "sphere")
        self.assertEqual(decoration_dict["model_path"], "sphere.obj")
        self.assertEqual(decoration_dict["position"], [0.0, 0.0, 0.0])
        self.assertEqual(decoration_dict["rotation"], [0.0, 0.0, 0.0])
        self.assertEqual(decoration_dict["scale"], [1.0, 1.0, 1.0])
        self.assertIsInstance(decoration_dict["color"], tuple)
        self.assertEqual(len(decoration_dict["color"]), 3)
        for c in decoration_dict["color"]:
            self.assertIsInstance(c, float)
            self.assertTrue(0.0 <= c <= 1.0)

    def test_composition_creation(self):
        composition = Composition()
        self.assertIsNone(composition.base)
        self.assertEqual(composition.decorations, [])

    def test_composition_set_base(self):
        composition = Composition()
        base = Base("file", "base.obj")
        composition.set_base(base)
        self.assertEqual(composition.base, base)

    def test_composition_add_decoration(self):
        composition = Composition()
        decoration1 = Decoration("sphere", "sphere.obj")
        decoration2 = Decoration("cube", "cube.obj")
        composition.add_decoration(decoration1)
        composition.add_decoration(decoration2)
        self.assertEqual(len(composition.decorations), 2)
        self.assertEqual(composition.decorations[0], decoration1)
        self.assertEqual(composition.decorations[1], decoration2)

    def test_composition_to_json_empty(self):
        composition = Composition()
        expected_json = "{}"
        self.assertEqual(composition.to_json(), expected_json)

    def test_composition_to_json_with_data(self):
        composition = Composition()
        base = Base("file", "base.obj")
        decoration = Decoration("sphere", "sphere.obj") # Убрали передачу color
        composition.set_base(base)
        composition.add_decoration(decoration)
        expected_dict = {
            "base": {"type": "file", "data": "base.obj"},
            "decorations": [{
                "name": "sphere",
                "model_path": "sphere.obj",
                "position": [0.0, 0.0, 0.0],
                "rotation": [0.0, 0.0, 0.0],
                "scale": [1.0, 1.0, 1.0],
                "color": list(decoration.color) # Получаем текущий цвет объекта
            }]
        }
        self.assertEqual(json.loads(composition.to_json()), expected_dict)

    def test_composition_from_json_empty(self):
        json_str = "{}"
        composition = Composition.from_json(json_str)
        self.assertIsNone(composition.base)
        self.assertEqual(composition.decorations, [])

    def test_composition_from_json_with_data(self):
        json_str = """
        {
            "base": {"type": "file", "data": "base.obj"},
            "decorations": [
                {
                    "name": "sphere",
                    "model_path": "sphere.obj",
                    "position": [1.0, 2.0, 3.0],
                    "rotation": [10.0, 20.0, 30.0],
                    "scale": [0.5, 0.5, 0.5],
                    "color": [0.4, 0.5, 0.6]
                }
            ]
        }
        """
        composition = Composition.from_json(json_str)
        self.assertIsNotNone(composition.base)
        self.assertEqual(composition.base.type, "file")
        self.assertEqual(composition.base.data, "base.obj")
        self.assertEqual(len(composition.decorations), 1)
        decoration = composition.decorations[0]
        self.assertEqual(decoration.name, "sphere")
        self.assertEqual(decoration.model_path, "sphere.obj")
        self.assertEqual(decoration.position, [1.0, 2.0, 3.0])
        self.assertEqual(decoration.rotation, [10.0, 20.0, 30.0])
        self.assertEqual(decoration.scale, [0.5, 0.5, 0.5])
        # Цвет загружается из JSON, поэтому проверяем его
        self.assertEqual(decoration.color, (0.4, 0.5, 0.6))

if __name__ == '__main__':
    unittest.main()