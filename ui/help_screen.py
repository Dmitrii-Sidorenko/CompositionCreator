# ui/help_screen.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal

class HelpScreen(QWidget):
    switch_screen_signal = pyqtSignal(str) # Объявляем сигнал внутри HelpScreen

    def __init__(self, parent=None): # Убираем switch_screen_signal из параметров
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        help_layout = QVBoxLayout()
        title_label_help = QLabel("Помощь")
        title_label_help.setAlignment(Qt.AlignmentFlag.AlignCenter)
        help_layout.addWidget(title_label_help)

        info_label = QLabel()
        info_label.setWordWrap(True)
        help_message = """
        ## Использование программы "Создание композиции"

        Добро пожаловать в программу для создания 3D композиций!

        **Основные разделы:**

        * **Главная:** Основной экран с 3D-визуализацией вашей композиции и элементами управления.
        * **Основы:** Экран для выбора основной 3D-модели, которая станет основой вашей композиции. Нажмите на одну из кнопок ("Основа 1" - "Основа 6") для выбора.
        * **Украшения:** Экран для добавления и выбора дополнительных 3D-моделей (украшений) к вашей композиции. Вы можете перейти на этот экран, нажав кнопку "Украшения" в главном меню или на экране "Основы".
        * **Сохранить композицию:** Позволяет сохранить текущую композицию в файл формата JSON. Этот файл будет содержать информацию об основе и всех добавленных украшениях, включая их положение, поворот и масштаб.
        * **Открыть композицию:** Позволяет загрузить ранее сохраненную композицию из JSON-файла.
        * **Сохранить изображение:** Сохраняет текущий вид 3D-окна как изображение в формате PNG или JPEG.
        * **Открыть модель...:** Позволяет загрузить 3D-модель (OBJ, STL, PLY) и установить ее в качестве основы композиции напрямую.
        * **Добавить украшение:** Позволяет загрузить 3D-модель (OBJ, STL, PLY) и добавить ее как новое украшение в композицию. Вам будет предложено ввести имя для украшения.
        * **Помощь:** Текущий экран с информацией об использовании программы.

        **Управление на главном экране:**

        * **Выбор украшения:** Кликните на украшение в 3D-виде, чтобы выделить его. Выбранное украшение отобразится в списке украшений (если такой список реализован).
        * **Трансформация:** После выбора украшения вы можете использовать слайдеры в правой части окна для изменения его положения (Перемещение), вращения (Вращение) и размера (Масштаб) по осям X, Y и Z.

        **Работа с украшениями:**

        * На экране "Украшения" (если это отдельный экран) вы можете увидеть список добавленных украшений и, возможно, удалять их или изменять их свойства.

        **Сохранение и открытие композиций:**

        * Используйте кнопки "Сохранить композицию" и "Открыть композицию" для сохранения и загрузки ваших работ.

        **Сохранение изображения:**

        * Кнопка "Сохранить изображение" сделает снимок текущего состояния 3D-вида.

        Если у вас возникнут дополнительные вопросы, обратитесь к документации или разработчику.
        """
        print(help_message)
        info_label.setText(help_message)
        help_layout.addWidget(info_label)

        navigation_layout_help = QHBoxLayout()
        home_button_help = QPushButton("Главная")
        home_button_help.clicked.connect(lambda: self.switch_screen_signal.emit("main"))
        decorations_button_help = QPushButton("Украшения")
        decorations_button_help.clicked.connect(lambda: self.switch_screen_signal.emit("decorations"))
        help_button_help = QPushButton("Помощь") # Кнопка "Помощь" на экране "Помощь"
        help_button_help.clicked.connect(lambda: self.switch_screen_signal.emit("help"))
        navigation_layout_help.addWidget(home_button_help)
        navigation_layout_help.addWidget(decorations_button_help)
        navigation_layout_help.addWidget(help_button_help)
        help_layout.addLayout(navigation_layout_help)

        self.setLayout(help_layout)