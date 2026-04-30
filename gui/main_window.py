# -*- coding: utf-8 -*-
# gui/main_window.py

import os
import sys
from copy import deepcopy

from PySide6 import QtGui, QtCore, QtWidgets
from PySide6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QFileDialog,
    QLineEdit, QLabel, QFormLayout, QMessageBox, QScrollArea, QGroupBox, QTextEdit,
    QStackedWidget, QPushButton, QHBoxLayout, QMenu
)
from PySide6.QtGui import Qt, QFont
from PySide6.QtCore import Slot, QFile, QIODevice
from PySide6.QtUiTools import QUiLoader

from lxml import etree as ET

from gui.widgets import AutoResizingTextEdit
from config.dcc_config import LABEL_MAP, MAIN_SECTION_TAGS, GROUPING_TAGS
from core.xml_handler import XMLHandler
from core.snippet_factory import SnippetFactory

def clean_tag(tag):
    return tag.split('}')[-1] if '}' in tag else tag

# GLOBAL QSS
GLOBAL_STYLESHEET = """
QMainWindow { background: rgb(255, 255, 255); }
QMenuBar { background-color: rgb(35, 131, 158); font-size: 13px; color: white; }
QMenuBar::item { background-color: transparent; padding: 8px 12px; border-radius: 4px; color: white; }
QMenuBar::item:selected { background-color: rgb(33, 123, 148); }
QMenu { background-color: rgb(35, 131, 158); color: white; border: 1px solid rgb(33, 123, 148); }
QMenu::item { padding: 6px 20px 6px 20px; }
QMenu::item:selected { background-color: rgb(50, 150, 180); }
QWidget#pageHome { background: rgb(255, 255, 255); }
QLabel#lblTitleDCC { font-size: 150px; font-weight: 700; color: rgb(0,0,0); background: transparent; }
QLabel#lblTitleEditor { font-size: 36px; font-weight: 700; color: rgb(0,0,0); background: transparent; }
QWidget#formContainer { background: rgb(245, 245, 245); }
#formContainer QGroupBox { border: 2px solid rgb(33, 68, 110); border-radius: 10px; background-color: rgb(53, 139, 242); padding: 12px 0px 0 6px; margin: 6px 10px 6px 0px; font-size: 10pt; font-weight: bold; }
#formContainer QGroupBox::title { font-family: Roboto; font-size: 12pt; subcontrol-origin: margin; border: 2px solid rgb(33, 68, 110); border-radius: 3px; left: 10px; padding: 0px 6px 0px 6px; background-color: rgb(64,108,160); color: white; }
#formContainer QLabel { font-size: 10pt; font-family: Verdana; font-weight: bold; color: black; margin: 0px 0px 3px 3px; padding: 0px; }
#formContainer QLineEdit { font-size: 10pt; font-weight: normal; font-family: Verdana; border-radius: 2px; background-color: rgb(228,228,228); min-height: 1.2em; margin: 0px 0px 3px 3px; color: rgb(20,20,20); padding: 2px; border: 1px solid rgb(150,150,150); }
#formContainer QTextEdit { font-size: 10pt; font-weight: normal; font-family: Verdana; border-radius: 2px; background-color: rgb(228,228,228); margin: 0px 0px 3px 3px; color: rgb(20,20,20); padding: 2px; border: 1px solid rgb(150,150,150); }
QCheckBox::indicator { width: 18px; height: 18px; }
"""

class DCCFormEditor(QMainWindow):
    def __init__(self, base_dir, version_info):
        super().__init__()
        self.base_dir = base_dir
        self.version_info = version_info
        
        self.xml_handler = XMLHandler(os.path.join(self.base_dir, "schemas"))

        loader = QUiLoader()
        ui_file_path = os.path.join(self.base_dir, "gui", "untitled.ui")
        ui_file = QFile(ui_file_path)
        if not ui_file.open(QIODevice.ReadOnly):
            QMessageBox.critical(self, "Erro Fatal", f"Não foi possível encontrar a interface:\n{ui_file_path}")
            sys.exit(-1)
            
        self.ui = loader.load(ui_file) 
        ui_file.close()

        self.setWindowTitle(f"Editor de Formulário DCC (v{self.version_info} Schema-Driven)")
        self.setGeometry(self.ui.geometry())
        self.setMinimumWidth(900)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        home_screen = self.ui.findChild(QWidget, "pageHome")
        self.stacked_widget.addWidget(home_screen)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.form_container = QWidget()
        self.form_container.setObjectName("formContainer") 
        self.main_layout = QVBoxLayout(self.form_container)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.form_container)
        self.stacked_widget.addWidget(self.scroll_area)

        menubar = self.ui.menuBar()
        self.setMenuBar(menubar)

        self.ui.actionAbrir_Arquivo.triggered.connect(self.open_file)
        self.ui.actionNovoDcc.triggered.connect(self.create_new_dcc)
        self.ui.actionSalvar_2.triggered.connect(self.save_file)
        self.ui.actionSalvar_como_2.triggered.connect(self.save_file_as)
        self.ui.actionSair.triggered.connect(self.close)

        self.view_menu = menubar.addMenu("Visualizar")
        self.action_translate = QtGui.QAction("Traduzir Tags para Português", self, checkable=True)
        self.action_translate.setChecked(True)
        self.action_translate.triggered.connect(self.toggle_translation)
        self.view_menu.addAction(self.action_translate)
        
        self.use_translation = True
        self.current_file_path = None
        self.form_fields = []
        self.group_boxes = []
        self.ns = {'dcc': 'https://ptb.de/dcc'}
        self.countnative = 0

        self.statusbar = self.statusBar()
        self.statusbar.setFont(QFont('Arial', 9, QFont.Weight.DemiBold))
        self.statusbar.setSizeGripEnabled(False)
        self.setMouseTracking(True)
        self.atualizaStatusBar("Pronto", 'rgb(228,228,228)', 'bold')

    def setCurrentDCCPath(self, cfp):
        self.current_file_path = cfp

    def getCurrentDCCPath(self):
        return self.current_file_path

    def nativeEvent(self, event, tipo):
        self.countnative += 1
        if self.countnative % 1000 == 0:
            if self.getCurrentDCCPath():
                self.atualizaStatusBar(f"Arquivo DCC: {self.getCurrentDCCPath()}", 'rgb(255,255,255)', 'bold')
            self.countnative = 0

    def sync_form_to_tree(self):
        if not self.xml_handler.xml_tree: return
        for field_info in self.form_fields:
            widget = field_info['widget']
            element = field_info['element']
            field_type = field_info['type']
            new_value = widget.toPlainText() if isinstance(widget, QTextEdit) else widget.text()

            if field_type == 'text':
                element.text = new_value if new_value.strip() else None
            elif field_type == 'attribute':
                attr_name = field_info['name']
                element.set(attr_name, new_value)

    @Slot(bool)
    def toggle_translation(self, checked):
        self.use_translation = checked
        if self.xml_handler.xml_root is not None:
            scroll_pos = self.scroll_area.verticalScrollBar().value()
            self.sync_form_to_tree()
            self._populate_form()
            self.scroll_area.verticalScrollBar().setValue(scroll_pos)

    def _clear_form(self):
        self.form_fields = []
        self.group_boxes = []
        while self.main_layout.count():
            child = self.main_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _populate_form(self):
        if self.xml_handler.xml_root is not None:
            self._clear_form()
            self._recursive_populate(self.xml_handler.xml_root, self.main_layout)

    def _create_form_row(self, layout, element, data_type, attr_name="", parent_element=None):
        tag = clean_tag(element.tag)
        parent_tag = clean_tag(parent_element.tag) if parent_element is not None else ""
        
        if tag == 'content' or parent_tag in ['name', 'description', 'person']:
            base_tag_name = parent_tag if parent_tag else tag
        else:
            base_tag_name = tag

        if self.use_translation:
            base_label = LABEL_MAP.get(base_tag_name, base_tag_name)
        else:
            base_label = base_tag_name

        if data_type == 'attribute':
            if self.use_translation:
                attr_label = LABEL_MAP.get(attr_name, attr_name)
            else:
                attr_label = attr_name
            label_text = f"{base_label} @ {attr_label}"
        else:
            label_text = base_label

        value = element.attrib.get(attr_name) if data_type == 'attribute' else (element.text or "").strip()

        if len(value) > 40:
            field = AutoResizingTextEdit(value)
        else:
            field = QLineEdit(value)

        label_widget = QLabel(label_text + ":")
        label_widget.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        if isinstance(layout, QFormLayout):
            layout.addRow(label_widget, field)
            self.form_fields.append({'widget': field, 'element': element, 'type': data_type, 'name': attr_name})


    def add_xml_node(self, parent_element, tag_to_add):
        scroll_pos = self.scroll_area.verticalScrollBar().value()
        self.sync_form_to_tree()
        
        snippet = SnippetFactory.generate_snippet(tag_to_add)
        new_node = ET.fromstring(snippet)
        parent_element.append(new_node)
        
        self._populate_form()
        self.scroll_area.verticalScrollBar().setValue(scroll_pos)
        self.atualizaStatusBar(f"Adicionado novo(a) '{LABEL_MAP.get(tag_to_add, tag_to_add)}'", "green", "bold")

    def _add_child_buttons(self, element, layout):
        tag = clean_tag(element.tag)
        
        # O programa original bloqueava a edição estrutural dessas tags, mantendo
        # apenas a tag <content> singular fornecida através do SnippetFactory.
        if tag in ['name', 'description', 'person', 'declaration', 'further', 
                   'noQuantity', 'text', 'xml', 'file', 'formula', 'latex', 'mathml']:
            return
            
        parser = self.xml_handler.schema_parser
        if parser:
            rules = parser.get_allowed_children(tag)
            allowed = rules.get('children', [])
            multiple = rules.get('multiple', [])
        else:
            # Fallback when no parser available
            return
            
        present_tags = [clean_tag(child.tag) for child in element]
        addable = []
        for a in allowed:
            if a in multiple or a not in present_tags:
                addable.append(a)
                
        if addable:
            btn_add = QPushButton(f"+ Adicionar em {LABEL_MAP.get(tag, tag) if self.use_translation else tag}")
            btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_add.setStyleSheet("""
                QPushButton { background-color: rgb(35, 131, 158); color: white; border-radius: 4px; padding: 6px; font-weight: bold; font-family: Verdana; }
                QPushButton:hover { background-color: rgb(50, 150, 180); }
            """)
            
            menu = QMenu(btn_add)
            for a in addable:
                label = LABEL_MAP.get(a, a) if self.use_translation else a
                action = menu.addAction(f"Adicionar {label}")
                action.triggered.connect(lambda checked=False, el=element, tag_to_add=a: self.add_xml_node(el, tag_to_add))
            btn_add.setMenu(menu)
            
            h_layout = QHBoxLayout()
            h_layout.addStretch()
            h_layout.addWidget(btn_add)
            layout.addRow(h_layout)

    def _recursive_populate(self, element, parent_layout, parent_element=None):
        tag = clean_tag(element.tag)
        parser = self.xml_handler.schema_parser
        
        if tag in ['name', 'description', 'person']:
            if isinstance(parent_layout, QFormLayout):
                for attr_name, _ in element.attrib.items():
                    self._create_form_row(parent_layout, element, 'attribute', attr_name, parent_element=parent_element)
            
            for child in element:
                self._recursive_populate(child, parent_layout, parent_element=element)
                
            if isinstance(parent_layout, QFormLayout):
                self._add_child_buttons(element, parent_layout)
            return
            
        is_main_sec = parser.is_main_section(tag) if parser else tag in MAIN_SECTION_TAGS
        if is_main_sec:
            title = LABEL_MAP.get(tag, tag) if self.use_translation else tag
            if element.get('refId'):
                title += f" (refId: {element.get('refId')})"
            section_box = QGroupBox(title)
            section_box.setCheckable(True)
            section_box.setChecked(True)
            self.group_boxes.append({'widget': section_box, 'element': element})
            if isinstance(parent_layout, QFormLayout):
                parent_layout.addRow(section_box)
            else:
                parent_layout.addWidget(section_box)
            content_layout = QFormLayout()
            section_box.setLayout(content_layout)
            for child in element:
                self._recursive_populate(child, content_layout, parent_element=element)
            
            self._add_child_buttons(element, content_layout)
            return
            
        is_group_tag = parser.is_grouping_tag(tag) if parser else tag in GROUPING_TAGS
        if is_group_tag:
            title = LABEL_MAP.get(tag, tag) if self.use_translation else tag
            if element.get('value'):
                title += f" ({element.get('value')})"
            group_box = QGroupBox(title)
            group_box.setCheckable(True)
            group_box.setChecked(True)
            self.group_boxes.append({'widget': group_box, 'element': element})
            if isinstance(parent_layout, QFormLayout):
                parent_layout.addRow(group_box)
            else:
                parent_layout.addWidget(group_box)
            form_layout = QFormLayout()
            group_box.setLayout(form_layout)
            for child in element:
                self._recursive_populate(child, form_layout, parent_element=element)
                
            self._add_child_buttons(element, form_layout)
            return
            
        if isinstance(parent_layout, QFormLayout):
            for attr_name, _ in element.attrib.items():
                self._create_form_row(parent_layout, element, 'attribute', attr_name, parent_element=parent_element)
            
            has_text = element.text and element.text.strip()
            is_leaf = len(element) == 0
            if has_text or tag == 'content' or is_leaf:
                self._create_form_row(parent_layout, element, 'text', parent_element=parent_element)
                
            for child in element:
                self._recursive_populate(child, parent_layout, parent_element=element)
                
            self._add_child_buttons(element, parent_layout)
                
        elif isinstance(parent_layout, QVBoxLayout):
            for child in element:
                self._recursive_populate(child, parent_layout, parent_element=element)

    @Slot()
    def create_new_dcc(self):
        schemas_base_path = os.path.join(self.base_dir, "schemas")
        versions = []
        if os.path.exists(schemas_base_path):
            for d in os.listdir(schemas_base_path):
                if os.path.isdir(os.path.join(schemas_base_path, d)):
                    if os.path.exists(os.path.join(schemas_base_path, d, "dcc.xsd")):
                        versions.append(d)
        
        if not versions:
            QMessageBox.critical(self, "Esquemas Não Encontrados", "Nenhuma pasta de esquema dcc.xsd encontrada.")
            return

        version, ok = QtWidgets.QInputDialog.getItem(self, "Selecionar Versão do Schema", "Escolha qual a versão do esquema para gerar o Novo DCC:", sorted(versions, reverse=True), 0, False)
        if not ok or not version: return

        new_file_path, _ = QFileDialog.getSaveFileName(self, "Onde deseja salvar o Novo DCC?", "", "Arquivos XML (*.xml)")
        if not new_file_path: return 

        self._clear_form()
        try:
            # 1. Load schema directly to create the parser
            self.xml_handler.load_schema(version)
            
            # 2. Auto Generate minimum required XML Tree
            generated_tree = self.xml_handler.schema_parser.generate_minimal_xml(version)
            self.xml_handler.xml_tree = generated_tree
            self.xml_handler.xml_root = generated_tree.getroot()

            self.setCurrentDCCPath(new_file_path)
            self.setWindowTitle(f"Editor DCC v{self.version_info} (Schema: {self.xml_handler.schema_version})")
            self.atualizaStatusBar(f"Novo Arquivo DCC (Auto-gerado): {new_file_path}", 'rgb(228,228,228)', 'normal')
            
            self.xml_handler.xml_tree.write(self.current_file_path, encoding="utf-8", xml_declaration=True, pretty_print=True)
            self._populate_form()
            self.stacked_widget.setCurrentIndex(1)
        except Exception as e:
            self.atualizaStatusBar(f"Erro: {e}", 'rgb(255,0,0)', 'bold')

    @Slot()
    def open_file(self):
        self._clear_form()
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecione um Arquivo XML", "", "Arquivos XML (*.xml)")
        if file_path:
            try:
                self.xml_handler.load_xml(file_path)
                self.setCurrentDCCPath(file_path)
                self.setWindowTitle(f"Editor DCC v{self.version_info} (Schema: {self.xml_handler.schema_version})")
                self.atualizaStatusBar(f"Arquivo DCC: {file_path}", 'rgb(228,228,228)', 'normal')
                self._populate_form()
                self.stacked_widget.setCurrentIndex(1)
            except Exception as e:
                self.atualizaStatusBar(f"Erro: {e}", 'rgb(255,0,0)', 'bold')

    @Slot()
    def save_file(self):
        if not self.xml_handler.xml_tree: return

        self.sync_form_to_tree()

        try:
            tree_to_save = deepcopy(self.xml_handler.xml_tree)
            root_to_save = tree_to_save.getroot()
        except Exception as e:
            return
            
        ns_map = self.xml_handler.xml_root.nsmap
        if None in ns_map: ns_map['default'] = ns_map.pop(None)

        elements_to_remove = []
        for group_info in self.group_boxes:
            widget = group_info['widget']
            if not widget.isChecked():
                original_element = group_info['element']
                try:
                    path = self.xml_handler.xml_tree.getpath(original_element)
                    found_elements = root_to_save.xpath(path, namespaces=ns_map)
                    if found_elements: elements_to_remove.append(found_elements[0])
                except Exception:
                    pass

        for el_to_remove in elements_to_remove:
            parent = el_to_remove.getparent()
            if parent is not None: parent.remove(el_to_remove)

        is_valid, err = self.xml_handler.validate_xml(tree_to_save)
        if not is_valid:
            QMessageBox.critical(self, "Erro de Schema", f"O XML é inválido:\n{err}")
            return 

        try:
            tree_to_save.write(self.getCurrentDCCPath(), encoding="utf-8", xml_declaration=True, pretty_print=True)
            self.atualizaStatusBar(f"Salvo: {self.getCurrentDCCPath()}", 'green', 'normal')
        except Exception as e:
             QMessageBox.critical(self, "Erro ao Salvar", str(e))

    @Slot()
    def save_file_as(self):
        if not self.xml_handler.xml_tree: return
        file_path, _ = QFileDialog.getSaveFileName(self, "Salvar como...", "", "Arquivos XML (*.xml)")
        if file_path:
            self.setCurrentDCCPath(file_path)
            self.save_file()

    def atualizaStatusBar(self, basemessage, bkcor, fweight):
        try:
            self.statusbar.showMessage(f" Status | {basemessage}")
            self.statusbar.setStyleSheet(f"background-color: {bkcor}; color: black; border: 1px solid rgb(100,156,156); font-weight:{fweight}")
            QtCore.QCoreApplication.processEvents()
        except ValueError as ve:
            print(ve)
