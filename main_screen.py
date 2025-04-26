from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QMenu, QInputDialog
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, pyqtSignal
import pyvista as pv
from pyvistaqt import QtInteractor
from core.composition_data import Composition, Base, Decoration
import os
import traceback
import json  # Import json module

class PyVistaView(QWidget):  # Класс PyVistaView должен быть определен здесь
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.qvtk_widget = QtInteractor(self)
        self.layout.addWidget(self.qvtk_widget)
        self.plotter = pv.Plotter(off_screen=False)
        rw = self.qvtk_widget.GetRenderWindow()
        if rw:
            rw.AddRenderer(self.plotter.renderer)
        self.decoration_actors = []  # Список для хранения акторов украшений

    def clear_plotter(self):
        self.plotter.clear()
        self.decoration_actors = []

    def render_scene(self, base=None, decorations=None):
        self.plotter.clear()
        self.decoration_actors = []  # Очищаем список акторов при перерисовке

        current_dir = os.getcwd()
        print(f"PyVistaView: Текущая рабочая директория: {current_dir}")

        # Загрузка основы
        if base and base.data:
            base_name, base_ext = os.path.splitext(base.data)
            json_path = os.path.join(current_dir, "data", "bases", base_name + ".json")
            obj_path = os.path.join(current_dir, "data", "bases", base.data)

            base_mesh = None

            if os.path.exists(json_path):
                print(f"PyVistaView: Найден JSON-файл основы: {json_path}")
                try:
                    with open(json_path, 'r') as f:
                        base_config = json.load(f)
                    if base_config.get('type') == 'obj' and base_config.get('data'):
                        obj_file_path_from_json = os.path.join(current_dir, "data", "bases", base_config['data'])
                        print(f"PyVistaView: Попытка загрузить основу из JSON: {obj_file_path_from_json}")
                        if os.path.exists(obj_file_path_from_json):
                            base_mesh = pv.read(obj_file_path_from_json)
                            print("PyVistaView: Основа из JSON прочитана успешно.")
                        else:
                            print(f"PyVistaView: OBJ-файл, указанный в JSON, не найден: {obj_file_path_from_json}")
                except json.JSONDecodeError as e:
                    print(f"PyVistaView: Ошибка при чтении JSON-файла основы ({json_path}): {e}")
                    traceback.print_exc()
                except Exception as e:
                    print(f"PyVistaView: Общая ошибка при загрузке основы из JSON ({json_path}): {e}")
                    traceback.print_exc()

            # Если JSON не найден или произошла ошибка, пробуем загрузить OBJ напрямую (как раньше)
            if base_mesh is None and os.path.exists(obj_path):
                print(f"PyVistaView: JSON-файл не найден или ошибка. Попытка загрузить OBJ напрямую: {obj_path}")
                try:
                    base_mesh = pv.read(obj_path)
                    print("PyVistaView: OBJ-файл основы прочитан успешно.")
                except Exception as e:
                    print(f"PyVistaView: Ошибка загрузки OBJ-модели основы ({obj_path}): {e}")
                    traceback.print_exc()
            elif base_mesh is None:
                print(f"PyVistaView: Файл модели основы не найден (ни JSON, ни OBJ): {obj_path}")
                sphere = pv.Sphere(radius=0.7)
                base_mesh = sphere
                print("PyVistaView: Загружена стандартная сфера вместо отсутствующей основы.")

            if base_mesh:
                print(f"PyVistaView: Количество точек в основе: {base_mesh.n_points}")
                print(f"PyVistaView: Количество ячеек в основе: {base_mesh.n_cells}")
                try:
                    self.plotter.add_mesh(base_mesh, color="lightblue", metallic=0.5, roughness=0.5, name="base")
                    print("PyVistaView: Основа успешно добавлена.")
                except ValueError as ve:
                    print(f"PyVistaView: Ошибка при добавлении меша основы: {ve}")
                    traceback.print_exc()

        # Загрузка украшений
        if decorations:
            for i, decoration in enumerate(decorations):
                if decoration.model_path:
                    decoration_path = os.path.join(current_dir, "data", "decorations", decoration.model_path)
                    print(f"PyVistaView: Попытка загрузить украшение: {decoration_path}")
                    if os.path.exists(decoration_path):
                        try:
                            decoration_mesh = pv.read(decoration_path)
                            actor = self.plotter.add_mesh(decoration_mesh, color=decoration.color, metallic=0.8, roughness=0.2,
                                                         name=f"decoration_{i}")
                            self.decoration_actors.append(actor)
                            print(f"PyVistaView: Актор '{actor.name}' добавлен. Количество акторов: {len(self.decoration_actors)}, Цвет: {decoration.color}")
                        except Exception as e:
                            print(f"PyVistaView: Ошибка загрузки модели украшения ({decoration_path}): {e}")
                            traceback.print_exc()
                    else:
                        print(f"PyVistaView: Файл модели украшения не найден: {decoration_path}")
                        cylinder = pv.Cylinder(radius=0.2, height=1.0)
                        actor = self.plotter.add_mesh(cylinder, color=decoration.color, metallic=0.8, roughness=0.2,
                                                     name=f"decoration_{i}")
                        self.decoration_actors.append(actor)
                        print(f"PyVistaView: Актор '{actor.name}' добавлен. Количество акторов: {len(self.decoration_actors)}, Цвет: {decoration.color}")

        self.plotter.camera_position = [(2.0, 2.0, 2.0), (0.0, 0.0, 0.0), (0.0, 0.0, 1.0)]
        self.plotter.enable_shadows()
        self.plotter.add_light(pv.Light(position=(2, 2, 2), color='white'))
        self.plotter.reset_camera()
        self.qvtk_widget.update()

    def transform_decoration(self, index, translate=[0, 0, 0], rotate=[0, 0, 0], scale=[1, 1, 1]):
        if index is not None and 0 <= index < len(self.decoration_actors):
            actor = self.decoration_actors[index]
            actor.SetPosition(translate)
            actor.SetOrientation(rotate)
            actor.SetScale(scale)
            self.qvtk_widget.update()

class MainScreen(QWidget):
    decoration_selected = pyqtSignal(int)  # Новый сигнал для выбора украшения

    def __init__(self, parent=None):
        super().__init__(parent)
        self.composition = Composition()
        self.selected_decoration_index = None  # Добавляем отслеживание выбранного индекса
        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout()  # Используем горизонтальный макет

        # Виджет PyVista
        self.pyvista_view = PyVistaView(parent=self)
        main_layout.addWidget(self.pyvista_view, 1)  # Занимает большую часть пространства

        # Панель управления сбоку
        controls_layout = QVBoxLayout()
        label = QLabel("Список украшений")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        controls_layout.addWidget(label)

        self.decoration_list_widget = QListWidget()
        self.decoration_list_widget.itemClicked.connect(self.on_decoration_selected)
        # Включаем контекстное меню
        self.decoration_list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        # Подключаем сигнал для отображения контекстного меню
        self.decoration_list_widget.customContextMenuRequested.connect(self.show_decoration_context_menu)
        controls_layout.addWidget(self.decoration_list_widget)

        main_layout.addLayout(controls_layout)
        self.setLayout(main_layout)
        self.update_3d_view()

    def on_decoration_selected(self, item):
        index = self.decoration_list_widget.row(item)
        print(f"MainScreen: Выбрано украшение в списке под индексом: {index}")
        self.decoration_selected.emit(index)
        self.selected_decoration_index = index # Обновляем выбранный индекс

    def update_3d_view(self):
        if self.pyvista_view:
            print("MainScreen: Вызов PyVistaView.render_scene")  # Добавлено для отладки
            self.pyvista_view.render_scene(self.composition.base, self.composition.decorations)
            print("MainScreen: Завершение PyVistaView.render_scene")  # Добавлено для отладки
        else:
            print("MainScreen: PyVistaView не инициализирован, невозможно обновить 3D вид.")

    def load_composition(self, composition_data):
        try:
            if 'base' in composition_data and composition_data['base']:
                base_data = composition_data['base']
                print(f"MainScreen: Загрузка основы - {base_data}")  # Debug print
                self.composition.set_base(Base(base_data['type'], base_data['data']))
            else:
                self.composition.set_base(None)
                print("MainScreen: Основа не найдена в данных.")  # Debug print

            self.composition.decorations = []
            self.decoration_list_widget.clear()  # Очищаем список перед загрузкой

            if 'decorations' in composition_data and composition_data['decorations']:
                print(f"MainScreen: Загрузка украшений - {composition_data['decorations']}")  # Debug print
                for dec_data in composition_data['decorations']:
                    decoration = Decoration(dec_data['name'], dec_data.get('model_path'))
                    decoration.position = dec_data.get('position', [0.0, 0.0, 0.0])
                    decoration.rotation = dec_data.get('rotation', [0.0, 0.0, 0.0])
                    decoration.scale = dec_data.get('scale', [1.0, 1.0, 1.0])
                    decoration.color = tuple(dec_data.get('color', decoration.color)) # Сохраняем цвет, если есть
                    self.composition.add_decoration(decoration)
                    self.decoration_list_widget.addItem(decoration.name)  # Добавляем название в список
            else:
                print("MainScreen: Украшения не найдены в данных.")  # Debug print

            self.update_3d_view()  # Перерисовываем сцену после загрузки данных

            # Применяем сохраненные трансформации к акторам после отрисовки
            if self.pyvista_view and self.pyvista_view.decoration_actors and self.composition.decorations:
                print("MainScreen: Применение трансформаций к украшениям.")  # Debug print
                for i, decoration in enumerate(self.composition.decorations):
                    if i < len(self.pyvista_view.decoration_actors):
                        self.pyvista_view.transform_decoration(i, decoration.position, decoration.rotation,
                                                             decoration.scale)
            else:
                print("MainScreen: Нет украшений для трансформации или акторы отсутствуют, или PyVistaView не инициализирован.")  # Debug print

            print("MainScreen: Композиция загружена.")

        except Exception as e:
            print(f"MainScreen: Ошибка при загрузке композиции: {e}")
            traceback.print_exc()  # Print the full traceback

    def update_decoration_list(self):
        print("MainScreen: Вызов update_decoration_list")  # Добавлено для отладки
        self.decoration_list_widget.clear()
        for decoration in self.composition.decorations:
            self.decoration_list_widget.addItem(decoration.name)
        print("MainScreen: Завершение update_decoration_list")  # Добавлено для отладки

    def update_3d_view_single_model(self, model_path):
        if self.pyvista_view:
            self.pyvista_view.clear_plotter() # Очищаем плоттер перед загрузкой новой модели
            current_dir = os.getcwd()
            full_model_path = model_path
            if not os.path.isabs(model_path):
                full_model_path = os.path.join(current_dir, "data", "bases", model_path) # Или decorations, в зависимости от вашей структуры

            if os.path.exists(full_model_path):
                try:
                    mesh = pv.read(full_model_path)
                    self.pyvista_view.plotter.add_mesh(mesh, name="opened_model") # Используем параметры по умолчанию
                    self.pyvista_view.plotter.reset_camera() # Вызываем reset_camera у self.plotter
                    self.pyvista_view.qvtk_widget.update()
                except Exception as e:
                    print(f"MainScreen: Ошибка при загрузке модели: {e}")
                    traceback.print_exc()
            else:
                print(f"MainScreen: Файл модели не найден: {full_model_path}")
        else:
            print("MainScreen: PyVistaView не инициализирован, невозможно загрузить отдельную модель.")

    def load_external_base(self, file_path, base_name):
        if self.pyvista_view:
            self.pyvista_view.clear_plotter()
            try:
                mesh = pv.read(file_path)
                self.composition.set_base(Base("file", os.path.basename(file_path)))
                self.pyvista_view.render_scene(self.composition.base, self.composition.decorations)
                print(f"MainScreen: Основа '{base_name}' успешно загружена из '{file_path}'.")
            except Exception as e:
                print(f"MainScreen: Ошибка при загрузке основы '{file_path}': {e}")
                traceback.print_exc()
        else:
            print("MainScreen: PyVistaView не инициализирован, невозможно загрузить основу.")

    def show_decoration_context_menu(self, position):
        selected_item = self.decoration_list_widget.itemAt(position)
        print(f"MainScreen: Вызов show_decoration_context_menu на элементе: {selected_item}")  # Добавлено для отладки
        if selected_item:
            menu = QMenu(self)
            remove_action = QAction("Удалить", self)
            remove_action.triggered.connect(lambda: self.remove_selected_decoration(selected_item))
            menu.addAction(remove_action)
            menu.exec(self.decoration_list_widget.mapToGlobal(position))
        else:
            print("MainScreen: show_decoration_context_menu - нет выбранного элемента.") # Добавлено для отладки

    def remove_selected_decoration(self, item):
        print(f"MainScreen: Вызов remove_selected_decoration на элементе: {item}")
        index_to_remove = self.decoration_list_widget.row(item)
        print(f"MainScreen: Индекс для удаления: {index_to_remove}")
        if 0 <= index_to_remove < len(self.composition.decorations):
            print(f"MainScreen: Попытка удалить украшение с индексом: {index_to_remove}")

            # Удаляем актора из плоттера и списка акторов
            if self.pyvista_view and index_to_remove < len(self.pyvista_view.decoration_actors):
                actor_to_remove = self.pyvista_view.decoration_actors.pop(index_to_remove)
                self.pyvista_view.plotter.remove_actor(actor_to_remove)
                print(f"MainScreen: Актор украшения с индексом {index_to_remove} удален из PyVistaView.")
                print(f"MainScreen: Количество акторов после удаления: {len(self.pyvista_view.decoration_actors)}")
            else:
                print(f"MainScreen: Не удалось удалить актор: pyvista_view не инициализирован или индекс вне границ.")

            # Удаляем данные об украшении из композиции
            try:
                del self.composition.decorations[index_to_remove]
                print(f"MainScreen: Украшение с индексом {index_to_remove} удалено из композиции.")
            except IndexError:
                print(f"MainScreen: Ошибка: Индекс {index_to_remove} вне границ списка украшений композиции.")
                return

            self.update_decoration_list()
            self.update_3d_view()  # Перерисовываем сцену

            # Обновляем выбранный индекс
            if self.selected_decoration_index == index_to_remove:
                self.selected_decoration_index = None
                if self.parent():
                    self.parent().update_transform_sliders(None)
            elif self.selected_decoration_index is not None and self.selected_decoration_index > index_to_remove:
                self.selected_decoration_index -= 1