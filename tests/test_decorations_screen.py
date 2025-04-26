import unittest
from unittest.mock import MagicMock
from PyQt6.QtWidgets import QApplication, QPushButton, QLabel
from PyQt6.QtCore import Qt
from ui.decorations_screen import DecorationsScreen

if not QApplication.instance():
    app = QApplication([])

class TestDecorationsScreen(unittest.TestCase):

    def setUp(self):
        self.decorations_screen = DecorationsScreen()
        self.app = QApplication.instance()

    def test_initUI(self):
        self.assertIsNotNone(self.decorations_screen.layout())
        self.assertEqual(len(self.decorations_screen.decoration_buttons), 6)
        for button in self.decorations_screen.decoration_buttons.values():
            self.assertIsInstance(button, QPushButton)
        # Проверяем наличие навигационных кнопок
        navigation_texts = ["Главная", "Основы композиций", "Помощь"]
        found_navigation_buttons = [button.text() for button in self.decorations_screen.findChildren(QPushButton) if button.text() in navigation_texts]
        self.assertEqual(sorted(found_navigation_buttons), sorted(navigation_texts))
        # Проверяем заголовок окна
        title_label = next(label for label in self.decorations_screen.findChildren(QLabel) if label.text() == "Выберите украшения")
        self.assertEqual(title_label.alignment(), Qt.AlignmentFlag.AlignCenter)

    def test_button_connections(self):
        switch_mock = MagicMock()
        decorations_selected_mock = MagicMock()
        self.decorations_screen.switch_screen_signal.connect(switch_mock)
        self.decorations_screen.decorations_selected_signal.connect(decorations_selected_mock)

        decoration_names = ["Украшение 1", "Украшение 2", "Украшение 3",
                            "Украшение 4", "Украшение 5", "Украшение 6"]
        decoration_buttons = {name: self.decorations_screen.findChildren(QPushButton, name)[0] for name in decoration_names}

        for decoration_name in decoration_names:
            button = decoration_buttons[decoration_name]
            button.click()
            file_name = f"decoration_{decoration_names.index(decoration_name) + 1}.obj"
            self.assertIn(file_name, self.decorations_screen.selected_decorations)
            decorations_selected_mock.assert_called_with(self.decorations_screen.selected_decorations)
            decorations_selected_mock.reset_mock()
            button.click() # Отменяем выбор
            self.assertNotIn(file_name, self.decorations_screen.selected_decorations)
            decorations_selected_mock.assert_called_with(self.decorations_screen.selected_decorations)
            decorations_selected_mock.reset_mock()

        # Проверяем нажатие навигационных кнопок
        home_button = next(button for button in self.decorations_screen.findChildren(QPushButton) if button.text() == "Главная")
        bases_button = next(button for button in self.decorations_screen.findChildren(QPushButton) if button.text() == "Основы композиций")
        help_button = next(button for button in self.decorations_screen.findChildren(QPushButton) if button.text() == "Помощь")

        home_button.click()
        switch_mock.assert_called_with("main")
        switch_mock.reset_mock()

        bases_button.click()
        switch_mock.assert_called_with("bases")
        switch_mock.reset_mock()

        help_button.click()
        switch_mock.assert_called_with("help")
        switch_mock.reset_mock()

    def test_select_decoration_method(self):
        decorations_selected_mock = MagicMock()
        self.decorations_screen.decorations_selected_signal.connect(decorations_selected_mock)

        test_file_name = "custom_decoration.obj"
        self.decorations_screen.select_decoration(test_file_name)
        self.assertIn(test_file_name, self.decorations_screen.selected_decorations)
        decorations_selected_mock.assert_called_once_with(self.decorations_screen.selected_decorations)

        self.decorations_screen.select_decoration(test_file_name) # Отменяем выбор
        self.assertNotIn(test_file_name, self.decorations_screen.selected_decorations)
        self.assertEqual(decorations_selected_mock.call_count, 2)
        self.assertEqual(decorations_selected_mock.call_args_list[-1][0][0], []) # Проверяем, что сигнал был эмитирован с пустым списком

if __name__ == '__main__':
    unittest.main()