from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal  # <---- Добавлен импорт pyqtSignal

class DecorationsScreen(QWidget):
    switch_screen_signal = pyqtSignal(str)
    decorations_selected_signal = pyqtSignal(list)  # <---- Определен сигнал decorations_selected_signal

    def __init__(self, parent=None): # Убираем switch_screen_signal из параметров
        super().__init__(parent)
        self.selected_decorations = []
        self.initUI()

    def initUI(self):
        decorations_layout = QVBoxLayout()
        title_label_decorations = QLabel("Выберите украшения")  # Изменим заголовок
        title_label_decorations.setAlignment(Qt.AlignmentFlag.AlignCenter)
        decorations_layout.addWidget(title_label_decorations)

        grid_layout = QGridLayout()
        decoration_names = ["Украшение 1", "Украшение 2", "Украшение 3",
                            "Украшение 4", "Украшение 5", "Украшение 6"]  # Список названий украшений
        self.decoration_buttons = {}
        row, col = 0, 0
        for decoration_name in decoration_names:
            button = QPushButton(decoration_name)
            button.setObjectName(decoration_name)  # <---- Добавьте эту строку
            self.decoration_buttons[decoration_name] = button
            # Привязываем имя файла (по умолчанию "decoration_1.obj" и т.д.) к кнопке
            file_name = f"decoration_{decoration_names.index(decoration_name) + 1}.obj"
            button.clicked.connect(lambda checked, name=file_name: self.select_decoration(name))
            grid_layout.addWidget(button, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1
        decorations_layout.addLayout(grid_layout)

        navigation_layout_decorations = QHBoxLayout()
        home_button_decorations = QPushButton("Главная")
        home_button_decorations.clicked.connect(lambda: self.switch_screen_signal.emit("main"))
        bases_button_decorations = QPushButton("Основы композиций")
        bases_button_decorations.clicked.connect(lambda: self.switch_screen_signal.emit("bases"))
        help_button_decorations = QPushButton("Помощь")
        help_button_decorations.clicked.connect(lambda: self.switch_screen_signal.emit("help"))
        navigation_layout_decorations.addWidget(home_button_decorations)
        navigation_layout_decorations.addWidget(bases_button_decorations)
        navigation_layout_decorations.addWidget(help_button_decorations)
        decorations_layout.addLayout(navigation_layout_decorations)

        self.setLayout(decorations_layout)
    def select_decoration(self, decoration_file):  # Изменим параметр на имя файла
        if decoration_file not in self.selected_decorations:
            self.selected_decorations.append(decoration_file)
            print(f"Добавлено украшение: {decoration_file}")
        else:
            self.selected_decorations.remove(decoration_file)
            print(f"Удалено украшение: {decoration_file}")
        print(f"DecorationsScreen: Готов к излучению сигнала с данными: {self.selected_decorations}") # <---- Добавлено
        self.decorations_selected_signal.emit(self.selected_decorations)  # Испускаем сигнал с выбранными украшениями
        print(
            f"DecorationsScreen: Испущен сигнал decorations_selected_signal с данными: {self.selected_decorations}")
        # Пока не переходим автоматически на другой экран после выбора украшения
        # self.switch_screen_signal.emit("save") # После выбора украшения переходим к сохранению (пока)