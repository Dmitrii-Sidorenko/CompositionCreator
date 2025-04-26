import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal

print(f"Пытаемся импортировать Qt: {Qt}")
print(f"Есть ли атрибут AlignCenter в Qt: {'AlignCenter' in dir(Qt)}")

class BasesScreen(QWidget):
    switch_screen_signal = pyqtSignal(str)
    base_selected_signal = pyqtSignal(str)  # Новый сигнал

    def __init__(self, parent=None): # Убираем switch_screen_signal из параметров
        super().__init__(parent)
        self.selected_base = None
        self.initUI()

    def initUI(self):
        bases_layout = QVBoxLayout()
        title_label_bases = QLabel("Выберите основу композиции")
        title_label_bases.setAlignment(Qt.AlignmentFlag.AlignCenter) # <---- ИЗМЕНЕННАЯ СТРОКА
        bases_layout.addWidget(title_label_bases)

        grid_layout = QGridLayout()
        base_names = ["Основа 1", "Основа 2", "Основа 3", "Основа 4", "Основа 5", "Основа 6"]
        self.base_buttons = {}
        row, col = 0, 0
        for base_name in base_names:
            button = QPushButton(base_name)
            button.setObjectName(base_name) # Добавлена установка objectName
            self.base_buttons[base_name] = button
            # Привязываем имя файла (по умолчанию "base_1.obj" и т.д.) к кнопке
            file_name = f"base_{base_names.index(base_name) + 1}.obj"
            button.clicked.connect(lambda checked, name=file_name: self.select_base(name))
            grid_layout.addWidget(button, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1
        bases_layout.addLayout(grid_layout)

        navigation_layout_bases = QHBoxLayout()
        home_button_bases = QPushButton("Главная")
        home_button_bases.setObjectName("Главная") # Добавлена установка objectName
        home_button_bases.clicked.connect(lambda: self.switch_screen_signal.emit("main"))
        decorations_button_bases = QPushButton("Украшения")
        decorations_button_bases.setObjectName("Украшения") # Добавлена установка objectName
        decorations_button_bases.clicked.connect(lambda: self.switch_screen_signal.emit("decorations"))
        help_button_bases = QPushButton("Помощь")
        help_button_bases.setObjectName("Помощь") # Добавлена установка objectName
        help_button_bases.clicked.connect(lambda: self.switch_screen_signal.emit("help"))
        navigation_layout_bases.addWidget(home_button_bases)
        navigation_layout_bases.addWidget(decorations_button_bases)
        navigation_layout_bases.addWidget(help_button_bases)
        bases_layout.addLayout(navigation_layout_bases)

        self.setLayout(bases_layout)

    def select_base(self, base_file):
        self.selected_base = base_file
        print(f"Выбрана основа: {self.selected_base}")
        self.base_selected_signal.emit(base_file)  # Испускаем сигнал с именем файла
        self.switch_screen_signal.emit("main")  # После выбора основы возвращаемся на главный экран

if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    window = BasesScreen()
    window.show()
    sys.exit(app.exec_())