# ui/main_window.py
import os
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QStackedWidget, QFileDialog, QMessageBox, QSlider, QLabel,
    QInputDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
import json
from core.composition_data import Composition, Base, Decoration
from PyQt6.QtGui import QPixmap, QImage
import mss
import mss.tools
from .decorations_screen import DecorationsScreen
from .help_screen import HelpScreen
from .main_screen import MainScreen
from .bases_screen import BasesScreen  # Импорт BasesScreen
from io import BytesIO
import traceback

class MainWindow(QWidget):
    switch_screen_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Создание композиции")
        self.setGeometry(100, 100, 800, 600)
        self.selected_base = None
        self.selected_decorations = []
        self.selected_export_format = None
        self.selected_decoration_index = None

        self.central_widget = QStackedWidget()
        self.main_screen_widget = MainScreen()
        self.bases_screen_widget = BasesScreen()
        self.bases_screen_widget.switch_screen_signal.connect(self.switch_screen)
        self.decorations_screen_widget = DecorationsScreen()  # Изменено: не передаем switch_screen
        self.decorations_screen_widget.switch_screen_signal.connect(self.switch_screen)  # Добавлено подключение сигнала
        # <---- Вот строка, которой не хватало!
        self.decorations_screen_widget.decorations_selected_signal.connect(self.handle_decorations_selection)
        self.help_screen_widget = HelpScreen()
        self.help_screen_widget.switch_screen_signal.connect(self.switch_screen)

        self.switch_screen_signal.connect(self.switch_screen)
        self.bases_screen_widget.base_selected_signal.connect(self.handle_base_selection)
        print(f"MainWindow: Экземпляр DecorationsScreen: {self.decorations_screen_widget}")  # <---- Добавлено
        print(f"MainWindow: Подключен сигнал decorations_selected_signal к: {self.handle_decorations_selection}")  # <---- Добавлено
        self.main_screen_widget.decoration_selected.connect(self.update_transform_sliders)

        self.translateXSlider = None
        self.translateYSlider = None
        self.translateZSlider = None
        self.rotateXSlider = None
        self.rotateYSlider = None
        self.rotateZSlider = None
        self.scaleXSlider = None
        self.scaleYSlider = None
        self.scaleZSlider = None

        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout(self)
        main_layout.addWidget(self.central_widget, 1)

        controls_layout_main = QVBoxLayout()

        button_layout = QVBoxLayout()
        open_bases_screen_button = QPushButton("Основы")  # Кнопка для перехода на экран основ
        open_bases_screen_button.clicked.connect(lambda: self.switch_screen("bases"))
        open_decorations_button = QPushButton("Украшения")
        open_decorations_button.clicked.connect(lambda: self.switch_screen("decorations"))
        save_composition_button = QPushButton("Сохранить композицию")
        save_composition_button.clicked.connect(self.save_composition)
        open_composition_button = QPushButton("Открыть композицию")
        open_composition_button.clicked.connect(self.open_composition)
        save_image_button = QPushButton("Сохранить изображение")
        save_image_button.clicked.connect(self.save_rendered_image)
        help_button_main = QPushButton("Помощь")
        help_button_main.clicked.connect(lambda: self.switch_screen("help"))
        open_model_button = QPushButton("Открыть модель...")
        open_model_button.clicked.connect(self.open_model)
        add_decoration_button = QPushButton("Добавить украшение")
        add_decoration_button.clicked.connect(self.open_decoration)

        button_layout.addWidget(open_model_button)
        button_layout.addWidget(open_bases_screen_button)  # Добавляем кнопку основ
        button_layout.addWidget(open_decorations_button)
        button_layout.addWidget(add_decoration_button)  # Добавляем кнопку "Добавить украшение"
        button_layout.addWidget(save_composition_button)
        button_layout.addWidget(open_composition_button)
        button_layout.addWidget(save_image_button)
        button_layout.addWidget(help_button_main)
        controls_layout_main.addLayout(button_layout)

        transform_layout = QVBoxLayout()
        transform_layout.addWidget(QLabel("<b>Трансформация</b>"))
        translate_label = QLabel("Перемещение:")
        transform_layout.addWidget(translate_label)

        self.translateXSlider = QSlider(Qt.Horizontal)
        self.translateYSlider = QSlider(Qt.Horizontal)
        self.translateZSlider = QSlider(Qt.Horizontal)
        self.translateXSlider.setObjectName("translateXSlider")
        self.translateYSlider.setObjectName("translateYSlider")
        self.translateZSlider.setObjectName("translateZSlider")
        self.translateXSlider.setRange(-100, 100)
        self.translateYSlider.setRange(-100, 100)
        self.translateZSlider.setRange(-100, 100)
        self.translateXSlider.setValue(0)
        self.translateYSlider.setValue(0)
        self.translateZSlider.setValue(0)
        self.translateXSlider.valueChanged.connect(self.update_decoration_transform)
        self.translateYSlider.valueChanged.connect(self.update_decoration_transform)
        self.translateZSlider.valueChanged.connect(self.update_decoration_transform)
        transform_layout.addWidget(QLabel("X:"))
        transform_layout.addWidget(self.translateXSlider)
        transform_layout.addWidget(QLabel("Y:"))
        transform_layout.addWidget(self.translateYSlider)
        transform_layout.addWidget(QLabel("Z:"))
        transform_layout.addWidget(self.translateZSlider)

        rotate_label = QLabel("Вращение:")
        transform_layout.addWidget(rotate_label)
        self.rotateXSlider = QSlider(Qt.Horizontal)
        self.rotateYSlider = QSlider(Qt.Horizontal)
        self.rotateZSlider = QSlider(Qt.Horizontal)
        self.rotateXSlider.setObjectName("rotateXSlider")
        self.rotateYSlider = QSlider(Qt.Horizontal)
        self.rotateZSlider = QSlider(Qt.Horizontal)
        self.rotateXSlider.setRange(-360, 360)
        self.rotateYSlider.setRange(-360, 360)
        self.rotateZSlider.setRange(-360, 360)
        self.rotateXSlider.setValue(0)
        self.rotateYSlider.setValue(0)
        self.rotateZSlider.setValue(0)
        self.rotateXSlider.valueChanged.connect(self.update_decoration_transform)
        self.rotateYSlider.valueChanged.connect(self.update_decoration_transform)
        self.rotateZSlider.valueChanged.connect(self.update_decoration_transform)
        transform_layout.addWidget(QLabel("X:"))
        transform_layout.addWidget(self.rotateXSlider)
        transform_layout.addWidget(QLabel("Y:"))
        transform_layout.addWidget(self.rotateYSlider)
        transform_layout.addWidget(QLabel("Z:"))
        transform_layout.addWidget(self.rotateZSlider)

        scale_label = QLabel("Масштаб:")
        transform_layout.addWidget(scale_label)
        self.scaleXSlider = QSlider(Qt.Horizontal)
        self.scaleYSlider = QSlider(Qt.Horizontal)
        self.scaleZSlider = QSlider(Qt.Horizontal)
        self.scaleXSlider.setObjectName("scaleXSlider")
        self.scaleYSlider = QSlider(Qt.Horizontal)
        self.scaleZSlider = QSlider(Qt.Horizontal)
        self.scaleXSlider.setRange(10, 5000)
        self.scaleYSlider.setRange(10, 5000)
        self.scaleZSlider.setRange(10, 5000)
        self.scaleXSlider.setSingleStep(1)
        self.scaleYSlider.setSingleStep(1)
        self.scaleZSlider.setSingleStep(1)
        self.scaleXSlider.setValue(1000)
        self.scaleYSlider.setValue(1000)
        self.scaleZSlider.setValue(1000)
        self.scaleXSlider.valueChanged.connect(self.update_decoration_transform)
        self.scaleYSlider.valueChanged.connect(self.update_decoration_transform)
        self.scaleZSlider.valueChanged.connect(self.update_decoration_transform)
        transform_layout.addWidget(QLabel("X:"))
        transform_layout.addWidget(self.scaleXSlider)
        transform_layout.addWidget(QLabel("Y:"))
        transform_layout.addWidget(self.scaleYSlider)
        transform_layout.addWidget(QLabel("Z:"))
        transform_layout.addWidget(self.scaleZSlider)

        controls_layout_main.addLayout(transform_layout)
        main_layout.addLayout(controls_layout_main)

        self.central_widget.addWidget(self.main_screen_widget)
        self.central_widget.addWidget(self.decorations_screen_widget)
        self.central_widget.addWidget(self.help_screen_widget)
        self.central_widget.addWidget(self.bases_screen_widget)  # Добавляем обработку для экрана основ

        self.switch_screen("main")

    def switch_screen(self, screen_name):
        self.central_widget.setCurrentIndex({
            "main": 0,
            "decorations": 1,
            "save": 2,
            "help": 3,
            "bases": 4 # Добавляем обработку для экрана основ
        }[screen_name])

    def handle_base_selection(self, base_file):
        print(f"MainWindow: Получен сигнал о выборе основы: {base_file}")
        print(f"MainWindow: self.main_screen_widget = {self.main_screen_widget}")
        if self.main_screen_widget:
            print(f"MainWindow: self.main_screen_widget.pyvista_view = {self.main_screen_widget.pyvista_view}")
            base_path = os.path.join(os.getcwd(), "data", "bases", base_file)
            self.main_screen_widget.load_external_base(base_path, os.path.splitext(base_file)[0])
            self.switch_screen("main")  # Возвращаемся на главный экран после выбора
        else:
            print("MainWindow: self.main_screen_widget is None!")

    def handle_decorations_selection(self, selected_decorations):
        print("MainWindow: Вызвана функция handle_decorations_selection")
        print(f"MainWindow: Выбраны украшения: {selected_decorations}")
        print(f"MainWindow: self.main_screen_widget = {self.main_screen_widget}")
        if self.main_screen_widget:
            print(f"MainWindow: self.main_screen_widget.pyvista_view = {self.main_screen_widget.pyvista_view}")
            if self.main_screen_widget.pyvista_view:
                self.main_screen_widget.pyvista_view.clear_plotter()
                self.main_screen_widget.composition.decorations = []
                for decoration_file in selected_decorations:
                    decoration_path = os.path.join(os.getcwd(), "data", "decorations", decoration_file)
                    try:
                        decoration = Decoration("decoration", decoration_file)
                        self.main_screen_widget.composition.add_decoration(decoration)
                        print(f"MainWindow: Добавлено в композицию: {decoration.name}, {decoration.model_path}")
                    except Exception as e:
                        QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при обработке украшения: {e}")
                        traceback.print_exc()
                self.main_screen_widget.update_decoration_list()
                self.main_screen_widget.update_3d_view()
                self.switch_screen("main")
            else:
                print("MainWindow: self.main_screen_widget.pyvista_view is None!")
        else:
            print("MainWindow: self.main_screen_widget is None!")

    def update_transform_sliders(self, index):
        self.selected_decoration_index = index
        print(f"MainWindow: Выбранный индекс украшения: {index}")
        print(
            f"MainWindow: Количество акторов украшений: {len(self.main_screen_widget.pyvista_view.decoration_actors) if self.main_screen_widget.pyvista_view else None}")
        print(f"MainWindow: pyvista_view: {self.main_screen_widget.pyvista_view}")
        if self.main_screen_widget.pyvista_view and index is not None and 0 <= index < len(
                self.main_screen_widget.pyvista_view.decoration_actors):
            print(f"MainWindow: Попытка получить актор по индексу: {index}")  # <---- Добавлено
            try:
                actor = self.main_screen_widget.pyvista_view.decoration_actors[index]
                print(f"MainWindow: Тип полученного актора: {type(actor)}")  # <---- Добавлено
                pos = actor.GetPosition()
                print(f"MainWindow: Получена позиция актора: {pos}")  # <---- Добавлено
                ori = actor.GetOrientation()
                print(f"MainWindow: Получена ориентация актора: {ori}")  # <---- Добавлено
                scl = actor.GetScale()
                print(f"MainWindow: Получен масштаб актора: {scl}")  # <---- Добавлено

                if self.translateXSlider:
                    print(f"MainWindow: Установка translateXSlider на: {int(pos[0] * 100)}")
                    self.translateXSlider.setValue(int(pos[0] * 100))
                else:
                    print("MainWindow: translateXSlider is None!")

                if self.translateYSlider:
                    print(f"MainWindow: Установка translateYSlider на: {int(pos[1] * 100)}")
                    self.translateYSlider.setValue(int(pos[1] * 100))
                else:
                    print("MainWindow: translateYSlider is None!")

                if self.translateZSlider:
                    print(f"MainWindow: Установка translateZSlider на: {int(pos[2] * 100)}")
                    self.translateZSlider.setValue(int(pos[2] * 100))
                else:
                    print("MainWindow: translateZSlider is None!")

                if self.rotateXSlider:
                    print(f"MainWindow: Установка rotateXSlider на: {int(ori[0])}")
                    self.rotateXSlider.setValue(int(ori[0]))
                else:
                    print("MainWindow: rotateXSlider is None!")

                if self.rotateYSlider:
                    print(f"MainWindow: Установка rotateYSlider на: {int(ori[1])}")
                    self.rotateYSlider.setValue(int(ori[1]))
                else:
                    print("MainWindow: rotateYSlider is None!")

                if self.rotateZSlider:
                    print(f"MainWindow: Установка rotateZSlider на: {int(ori[2])}")
                    self.rotateZSlider.setValue(int(ori[2]))
                else:
                    print("MainWindow: rotateZSlider is None!")

                if self.scaleXSlider:
                    print(f"MainWindow: Установка scaleXSlider на: {int(scl[0] * 1000)}")
                    self.scaleXSlider.setValue(int(scl[0] * 1000))
                else:
                    print("MainWindow: scaleXSlider is None!")

                if self.scaleYSlider:
                    print(f"MainWindow: Установка scaleYSlider на: {int(scl[1] * 1000)}")
                    self.scaleYSlider.setValue(int(scl[1] * 1000))
                else:
                    print("MainWindow: scaleYSlider is None!")

                if self.scaleZSlider:
                    print(f"MainWindow: Установка scaleZSlider на: {int(scl[2] * 1000)}")
                    self.scaleZSlider.setValue(int(scl[2] * 1000))
                else:
                    print("MainWindow: scaleZSlider is None!")

            except IndexError as e:
                print(f"MainWindow: Ошибка IndexError при доступе к актору: {e}")  # <---- Добавлено
            except Exception as e:
                print(f"MainWindow: Другая ошибка при обработке актора: {e}")  # <---- Добавлено
        else:
            if self.translateXSlider:
                self.translateXSlider.setValue(0)
            if self.translateYSlider:
                self.translateYSlider.setValue(0)
            if self.translateZSlider:
                self.translateZSlider.setValue(0)
            if self.rotateXSlider:
                self.rotateXSlider.setValue(0)
            if self.rotateYSlider:
                self.rotateYSlider.setValue(0)
            if self.rotateZSlider:
                self.rotateZSlider.setValue(0)
            if self.scaleXSlider:
                self.scaleXSlider.setValue(1000)
            if self.scaleYSlider:
                self.scaleYSlider.setValue(1000)
            if self.scaleZSlider:
                self.scaleZSlider.setValue(1000)

    def update_decoration_transform(self):
        if self.selected_decoration_index is not None and 0 <= self.selected_decoration_index < len(
                self.main_screen_widget.pyvista_view.decoration_actors):
            translateX = self.translateXSlider.value() / 100.0
            translateY = self.translateYSlider.value() / 100.0
            translateZ = self.translateZSlider.value() / 100.0
            rotateX = self.rotateXSlider.value()
            rotateY = self.rotateYSlider.value()
            rotateZ = self.rotateZSlider.value()
            scaleX = self.scaleXSlider.value() / 1000.0
            scaleY = self.scaleYSlider.value() / 1000.0
            scaleZ = self.scaleZSlider.value() / 1000.0

            self.main_screen_widget.pyvista_view.transform_decoration(
                self.selected_decoration_index,
                translate=[translateX, translateY, translateZ],
                rotate=[rotateX, rotateY, rotateZ],
                scale=[scaleX, scaleY, scaleZ]
            )

    def save_composition(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(self, "Сохранить композицию", "", "JSON Files (*.json)")

        if file_path:
            current_composition = Composition()
            if self.main_screen_widget.composition.base:
                current_composition.set_base(self.main_screen_widget.composition.base)

            for i, decoration in enumerate(self.main_screen_widget.composition.decorations):
                decoration_data = Decoration(decoration.name, decoration.model_path)
                if i < len(self.main_screen_widget.pyvista_view.decoration_actors):
                    actor = self.main_screen_widget.pyvista_view.decoration_actors[i]
                    pos = actor.GetPosition()
                    ori = actor.GetOrientation()
                    scl = actor.GetScale()
                    decoration_data.position = list(pos)
                    decoration_data.rotation = list(ori)
                    decoration_data.scale = list(scl)
                else:
                    decoration_data.position = decoration.position
                    decoration_data.rotation = decoration.rotation
                    decoration_data.scale = decoration.scale
                current_composition.add_decoration(decoration_data)

            try:
                json_data = current_composition.to_json()
                with open(file_path, 'w') as f:
                    f.write(json_data)
                QMessageBox.information(self, "Сохранено", f"Композиция успешно сохранена в {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка сохранения", f"Произошла ошибка при сохранении: {e}")

    def save_rendered_image(self):
        try:
            qvtk_widget = self.main_screen_widget.pyvista_view.qvtk_widget
            rect = qvtk_widget.geometry()
            left, top = rect.x(), rect.y()
            width, height = rect.width(), rect.height()
            bbox = {"left": left, "top": top, "width": width, "height": height}

            with mss.mss() as sct:
                sct_img_mss = sct.grab(bbox)
                image_bytes = BytesIO(mss.tools.to_png(sct_img_mss.rgb, sct_img_mss.size))
                q_image = QImage.fromData(image_bytes.getvalue())
                screenshot = QPixmap.fromImage(q_image)

            file_dialog = QFileDialog()
            file_path, selected_filter = file_dialog.getSaveFileName(
                self,
                "Сохранить изображение",
                "",
                "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg)"
            )

            if file_path:
                screenshot.save(file_path)
                QMessageBox.information(self, "Сохранено", f"Скриншот успешно сохранен в {file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка сохранения", f"Произошла ошибка при сохранении скриншота: {e}")


    def open_composition(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Открыть композицию", "", "JSON Files (*.json)")

        if file_path:
            try:
                with open(file_path, 'r') as f:
                    json_data = f.read()
                composition_data = json.loads(json_data)
                self.main_screen_widget.load_composition(composition_data)
                QMessageBox.information(self, "Открыто", f"Композиция успешно открыта из {file_path}")

            except FileNotFoundError:
                QMessageBox.critical(self, "Ошибка открытия", "Файл не найден.")
            except json.JSONDecodeError:
                QMessageBox.critical(self, "Ошибка открытия", "Ошибка чтения JSON файла.")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка открытия", f"Произошла ошибка при открытии композиции: {e}")

    def open_model(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Открыть модель основы",
            "",
            "OBJ Files (*.obj);;STL Files (*.stl);;PLY Files (*.ply);;All 3D Models (*.obj *.stl *.ply)"
        )

        if file_path:
            try:
                base = Base("file", os.path.basename(file_path))
                self.main_screen_widget.composition.set_base(base)
                self.main_screen_widget.update_3d_view()
                QMessageBox.information(self, "Основа открыта",
                                        f"Основа успешно открыта из {os.path.basename(file_path)}.")
            except FileNotFoundError:
                QMessageBox.critical(self, "Ошибка открытия", "Файл модели основы не найден.")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка открытия", f"Произошла ошибка при открытии модели основы: {e}")
                traceback.print_exc()
    def open_decoration(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Открыть модель украшения",
            "",
            "OBJ Files (*.obj);;STL Files (*.stl);;PLY Files (*.ply);;All 3D Models (*.obj *.stl *.ply)"
        )

        if file_path:
            try:
                decoration_name, ok = QInputDialog.getText(self, "Имя украшения", "Введите имя для украшения:")
                if ok and decoration_name:
                    decoration = Decoration(decoration_name, os.path.basename(file_path))
                    self.main_screen_widget.composition.add_decoration(decoration)
                    self.main_screen_widget.update_decoration_list()  # Обновляем список украшений в UI
                    self.main_screen_widget.update_3d_view()  # Перерисовываем 3D вид
                    QMessageBox.information(self, "Украшение добавлено",
                                            f"Украшение '{decoration_name}' успешно добавлено из {os.path.basename(file_path)}.")
                elif ok:
                    QMessageBox.warning(self, "Имя не введено", "Имя украшения не было введено.")

            except FileNotFoundError:
                QMessageBox.critical(self, "Ошибка открытия", "Файл модели украшения не найден.")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка открытия", f"Произошла ошибка при открытии модели украшения: {e}")
                traceback.print_exc()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())