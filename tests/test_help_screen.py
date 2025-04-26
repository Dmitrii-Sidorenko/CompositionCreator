import unittest
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QApplication, QPushButton, QLabel
from PyQt6.QtCore import Qt
from ui.help_screen import HelpScreen

if not QApplication.instance():
    app = QApplication([])
class TestHelpScreen(unittest.TestCase):

    def setUp(self):
        self.help_screen = HelpScreen()

    def test_initialization(self):
        self.assertIsInstance(self.help_screen, HelpScreen)

    def test_title_label(self):
        title_label = self.help_screen.findChildren(QLabel)
        self.assertTrue(any(label.text() == "Помощь" for label in title_label))
        title_label = next(label for label in title_label if label.text() == "Помощь")
        self.assertEqual(title_label.alignment(), Qt.AlignmentFlag.AlignCenter)

    def test_info_label_content(self):
        info_labels = self.help_screen.findChildren(QLabel)
        for label in info_labels:
            print(f"Найденная метка: '{label.text()}'")  # Добавим отладочный вывод
        info_label = next(label for label in info_labels if "## Использование" in label.text())
        self.assertIn("Добро пожаловать в программу для создания 3D композиций!", info_label.text())
        self.assertTrue(info_label.wordWrap())

    def test_navigation_buttons(self):
        buttons = self.help_screen.findChildren(QPushButton)
        navigation_button_texts = ["Главная", "Украшения", "Помощь"]
        found_navigation_buttons = [button.text() for button in buttons if button.text() in navigation_button_texts]
        self.assertEqual(sorted(found_navigation_buttons), sorted(navigation_button_texts))

    @patch('ui.help_screen.HelpScreen.switch_screen_signal')
    def test_navigation_button_clicks(self, mock_switch_screen_signal):
        buttons = self.help_screen.findChildren(QPushButton)
        navigation_buttons = {button.text(): button for button in buttons if button.text() in ["Главная", "Украшения", "Помощь"]}

        navigation_buttons["Главная"].click()
        mock_switch_screen_signal.emit.assert_called_with("main")
        mock_switch_screen_signal.reset_mock()

        navigation_buttons["Украшения"].click()
        mock_switch_screen_signal.emit.assert_called_with("decorations")
        mock_switch_screen_signal.reset_mock()

        navigation_buttons["Помощь"].click()
        mock_switch_screen_signal.emit.assert_called_with("help")
        mock_switch_screen_signal.reset_mock()

if __name__ == '__main__':
    unittest.main()