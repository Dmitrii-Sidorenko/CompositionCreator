import unittest
from unittest.mock import MagicMock
from PyQt6.QtWidgets import QApplication, QPushButton, QLabel
from PyQt6.QtCore import Qt
from ui.bases_screen import BasesScreen

if not QApplication.instance():
    app = QApplication([])

class TestBasesScreen(unittest.TestCase):

    def setUp(self):
        self.bases_screen = BasesScreen()
        self.app = QApplication.instance()

    def test_initUI(self):
        self.assertIsNotNone(self.bases_screen.layout())
        self.assertEqual(len(self.bases_screen.base_buttons), 6)
        for button in self.bases_screen.base_buttons.values():
            self.assertIsInstance(button, QPushButton)
        # Проверяем наличие навигационных кнопок
        navigation_texts = ["Главная", "Украшения", "Помощь"]
        found_navigation_buttons = [button.text() for button in self.bases_screen.findChildren(QPushButton) if button.text() in navigation_texts]
        self.assertEqual(sorted(found_navigation_buttons), sorted(navigation_texts))
        # Проверяем заголовок окна
        title_label = next(label for label in self.bases_screen.findChildren(QLabel) if label.text() == "Выберите основу композиции")
        self.assertEqual(title_label.alignment(), Qt.AlignmentFlag.AlignCenter)

    def test_button_connections(self):
        switch_mock = MagicMock()
        base_selected_mock = MagicMock()
        self.bases_screen.switch_screen_signal.connect(switch_mock)
        self.bases_screen.base_selected_signal.connect(base_selected_mock)

        base_names = ["Основа 1", "Основа 2", "Основа 3", "Основа 4", "Основа 5", "Основа 6"]
        base_buttons = {name: self.bases_screen.findChildren(QPushButton, name)[0] for name in base_names}

        for base_name in base_names:
            button = base_buttons[base_name]
            button.click()
            file_name = f"base_{base_names.index(base_name) + 1}.obj"
            self.assertEqual(self.bases_screen.selected_base, file_name)
            base_selected_mock.assert_called_once_with(file_name)
            switch_mock.assert_called_once_with("main")
            switch_mock.reset_mock()
            base_selected_mock.reset_mock()

        # Проверяем нажатие навигационных кнопок
        home_button = next(button for button in self.bases_screen.findChildren(QPushButton) if button.text() == "Главная")
        decorations_button = next(button for button in self.bases_screen.findChildren(QPushButton) if button.text() == "Украшения")
        help_button = next(button for button in self.bases_screen.findChildren(QPushButton) if button.text() == "Помощь")

        home_button.click()
        switch_mock.assert_called_with("main")
        switch_mock.reset_mock()

        decorations_button.click()
        switch_mock.assert_called_with("decorations")
        switch_mock.reset_mock()

        help_button.click()
        switch_mock.assert_called_with("help")
        switch_mock.reset_mock()

    def test_select_base_method(self):
        switch_mock = MagicMock()
        base_selected_mock = MagicMock()
        self.bases_screen.switch_screen_signal.connect(switch_mock)
        self.bases_screen.base_selected_signal.connect(base_selected_mock)

        test_file_name = "custom_base.obj"
        self.bases_screen.select_base(test_file_name)
        self.assertEqual(self.bases_screen.selected_base, test_file_name)
        base_selected_mock.assert_called_once_with(test_file_name)
        switch_mock.assert_called_once_with("main")

if __name__ == '__main__':
    unittest.main()