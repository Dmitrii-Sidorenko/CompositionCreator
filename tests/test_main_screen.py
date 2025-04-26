import unittest
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QApplication, QListWidgetItem, QListWidget
from PyQt6.QtCore import Qt, QPoint
from ui.main_screen import MainScreen
from core.composition_data import Composition, Base, Decoration
from ui.main_screen import PyVistaView  # Импортируем PyVistaView

if not QApplication.instance():
    app = QApplication([])

class TestMainScreen(unittest.TestCase):

    def setUp(self):
        self.main_screen = MainScreen()
        self.app = QApplication.instance()

    def test_initUI(self):
        self.assertIsNotNone(self.main_screen.layout())
        self.assertIsInstance(self.main_screen.pyvista_view, PyVistaView)
        self.assertIsInstance(self.main_screen.decoration_list_widget, QListWidget)
        self.assertEqual(self.main_screen.decoration_list_widget.contextMenuPolicy(), Qt.ContextMenuPolicy.CustomContextMenu)
        self.assertIsInstance(self.main_screen.composition, Composition)
        self.assertIsNone(self.main_screen.selected_decoration_index)

    def test_on_decoration_selected(self):
        # Добавляем элементы в список
        self.main_screen.composition.decorations = [
            Decoration("Декорация A", "model_a.obj"),
            Decoration("Декорация B", "model_b.obj")
        ]
        self.main_screen.update_decoration_list()

        # Эмулируем выбор первого элемента
        item1 = self.main_screen.decoration_list_widget.item(0)
        self.main_screen.on_decoration_selected(item1)
        self.assertEqual(self.main_screen.selected_decoration_index, 0)

        # Эмулируем выбор второго элемента
        item2 = self.main_screen.decoration_list_widget.item(1)
        self.main_screen.on_decoration_selected(item2)
        self.assertEqual(self.main_screen.selected_decoration_index, 1)

        # Эмулируем снятие выбора (через клик на уже выбранном элементе)
        self.main_screen.on_decoration_selected(item2)
        self.assertEqual(self.main_screen.selected_decoration_index, 1) # Индекс не должен меняться при повторном клике (логика текущей реализации)

    def test_update_3d_view(self):
        mock_pyvista_view = MagicMock()
        self.main_screen.pyvista_view = mock_pyvista_view
        base = Base("obj", "base.obj")
        decoration = Decoration("Декорация 1", "model1.obj")
        decoration.color = (1, 0, 0)
        decorations = [decoration]
        self.main_screen.composition.base = base
        self.main_screen.composition.decorations = decorations
        self.main_screen.update_3d_view()
        mock_pyvista_view.render_scene.assert_called_once_with(base, decorations)

        # Проверяем вызов с пустой композицией
        self.main_screen.composition.base = None
        self.main_screen.composition.decorations = []
        self.main_screen.update_3d_view()
        mock_pyvista_view.render_scene.assert_called_with(None, [])

    def test_load_composition(self):
        mock_pyvista_view = MagicMock()
        self.main_screen.pyvista_view = mock_pyvista_view
        composition_data = {
            'base': {'type': 'obj', 'data': 'test_base.obj'},
            'decorations': [
                {'name': 'Декорация A', 'model_path': 'dec_a.obj', 'position': [1.0, 2.0, 3.0], 'rotation': [4.0, 5.0, 6.0], 'scale': [0.5, 0.5, 0.5], 'color': [0.1, 0.2, 0.3]},
                {'name': 'Декорация B', 'model_path': 'dec_b.obj'}
            ]
        }
        self.main_screen.load_composition(composition_data)
        self.assertEqual(self.main_screen.composition.base.data, 'test_base.obj')
        self.assertEqual(len(self.main_screen.composition.decorations), 2)
        self.assertEqual(self.main_screen.decoration_list_widget.count(), 2)
        self.assertEqual(self.main_screen.decoration_list_widget.item(0).text(), 'Декорация A')
        self.assertEqual(self.main_screen.decoration_list_widget.item(1).text(), 'Декорация B')
        self.assertEqual(self.main_screen.composition.decorations[0].position, [1.0, 2.0, 3.0])
        self.assertEqual(self.main_screen.composition.decorations[0].rotation, [4.0, 5.0, 6.0])
        self.assertEqual(self.main_screen.composition.decorations[0].scale, [0.5, 0.5, 0.5])
        self.assertEqual(self.main_screen.composition.decorations[0].color, (0.1, 0.2, 0.3))
        self.assertEqual(self.main_screen.composition.decorations[1].name, 'Декорация B')
        mock_pyvista_view.render_scene.assert_called_once()

        # Проверяем загрузку без основы и украшений
        composition_data_empty = {'base': None, 'decorations': None}
        self.main_screen.load_composition(composition_data_empty)
        self.assertIsNone(self.main_screen.composition.base)
        self.assertEqual(len(self.main_screen.composition.decorations), 0)
        self.assertEqual(self.main_screen.decoration_list_widget.count(), 0)
        self.assertEqual(mock_pyvista_view.render_scene.call_count, 2) # Вызывался еще раз с None, []

    def test_update_decoration_list(self):
        self.main_screen.composition.decorations = [
            Decoration("Первое", "model1.obj"),
            Decoration("Второе", "model2.obj"),
            Decoration("Третье", "model3.obj")
        ]
        self.main_screen.update_decoration_list()
        self.assertEqual(self.main_screen.decoration_list_widget.count(), 3)
        self.assertEqual(self.main_screen.decoration_list_widget.item(0).text(), "Первое")
        self.assertEqual(self.main_screen.decoration_list_widget.item(1).text(), "Второе")
        self.assertEqual(self.main_screen.decoration_list_widget.item(2).text(), "Третье")

        # Проверяем с пустым списком украшений
        self.main_screen.composition.decorations = []
        self.main_screen.update_decoration_list()
        self.assertEqual(self.main_screen.decoration_list_widget.count(), 0)

    def test_load_external_base(self):
        mock_pyvista_view = MagicMock()
        self.main_screen.pyvista_view = mock_pyvista_view
        file_path = "path/to/external_base.obj"
        base_name = "Новая основа"
        with patch('ui.main_screen.pv.read') as mock_read:
            mock_read.return_value = MagicMock()
            self.main_screen.load_external_base(file_path, base_name)
            self.assertEqual(self.main_screen.composition.base.data, "external_base.obj")
            self.assertEqual(self.main_screen.composition.base.type, "file")
            mock_pyvista_view.render_scene.assert_called_once()

        # Проверяем обработку ошибки загрузки
        with patch('ui.main_screen.pv.read', side_effect=FileNotFoundError("File not found")):
            self.main_screen.composition.base = None # Сбрасываем базу перед тестом
            self.main_screen.load_external_base(file_path, base_name)
            self.assertIsNone(self.main_screen.composition.base)
            self.assertEqual(mock_pyvista_view.render_scene.call_count, 1) # render_scene вызывается даже при ошибке

    def test_remove_selected_decoration(self):
        # Добавляем несколько украшений
        self.main_screen.composition.decorations = [
            Decoration("Декорация 1", "model1.obj"),
            Decoration("Декорация 2", "model2.obj"),
            Decoration("Декорация 3", "model3.obj")
        ]
        self.main_screen.update_decoration_list()
        mock_pyvista_view = MagicMock()
        mock_pyvista_view.plotter = MagicMock()
        mock_pyvista_view.decoration_actors = [MagicMock()] * 3 # Инициализируем список акторов
        self.main_screen.pyvista_view = mock_pyvista_view

        # Выбираем второй элемент и удаляем его
        item_to_remove = self.main_screen.decoration_list_widget.item(1)
        self.main_screen.decoration_list_widget.setCurrentItem(item_to_remove)
        self.main_screen.remove_selected_decoration(item_to_remove)

        self.assertEqual(len(self.main_screen.composition.decorations), 2)
        self.assertEqual(self.main_screen.decoration_list_widget.count(), 2)
        self.assertEqual(self.main_screen.composition.decorations[0].name, "Декорация 1")
        self.assertEqual(self.main_screen.composition.decorations[1].name, "Декорация 3")
        mock_pyvista_view.render_scene.assert_called()
        mock_pyvista_view.plotter.remove_actor.assert_called_once()

        # Проверяем удаление первого элемента
        self.main_screen.composition.decorations = [Decoration("A", "a.obj"), Decoration("B", "b.obj")]
        self.main_screen.update_decoration_list()
        mock_pyvista_view.decoration_actors = [MagicMock()] * 2
        item_to_remove = self.main_screen.decoration_list_widget.item(0)
        self.main_screen.decoration_list_widget.setCurrentItem(item_to_remove)
        self.main_screen.remove_selected_decoration(item_to_remove)
        self.assertEqual(len(self.main_screen.composition.decorations), 1)
        self.assertEqual(self.main_screen.composition.decorations[0].name, "B")
        self.assertEqual(self.main_screen.decoration_list_widget.count(), 1)
        self.assertEqual(mock_pyvista_view.plotter.remove_actor.call_count, 2)

        # Проверяем удаление последнего элемента
        self.main_screen.composition.decorations = [Decoration("X", "x.obj"), Decoration("Y", "y.obj")]
        self.main_screen.update_decoration_list()
        mock_pyvista_view.decoration_actors = [MagicMock()] * 2
        item_to_remove = self.main_screen.decoration_list_widget.item(1)
        self.main_screen.decoration_list_widget.setCurrentItem(item_to_remove)
        self.main_screen.remove_selected_decoration(item_to_remove)
        self.assertEqual(len(self.main_screen.composition.decorations), 1)
        self.assertEqual(self.main_screen.composition.decorations[0].name, "X")
        self.assertEqual(self.main_screen.decoration_list_widget.count(), 1)
        self.assertEqual(mock_pyvista_view.plotter.remove_actor.call_count, 3)

        # Проверяем попытку удаления при пустом списке
        self.main_screen.composition.decorations = []
        self.main_screen.update_decoration_list()
        item_to_remove = QListWidgetItem("Нереальный элемент")
        self.main_screen.remove_selected_decoration(item_to_remove) # Не должно быть ошибки

if __name__ == '__main__':
    unittest.main()