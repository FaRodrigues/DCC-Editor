# -*- coding: utf-8 -*-
# DCC Editor version 5.4 (2025)
# Autor: Gustavo Chieza | Fernando Alves Rodrigues
# Empresa: Inmetro

import sys
import os

from PySide6 import QtGui, QtCore, QtWidgets
from lxml import etree as ET
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QFileDialog, QMenuBar,
    QLineEdit, QLabel, QFormLayout, QMessageBox, QScrollArea, QGroupBox, QTextEdit
)

from PySide6.QtGui import QAction, Qt, QFont, QTextOption, QFontMetrics
from PySide6.QtCore import Slot


# Define a versão do script
version = "5.4"
# Define os rótulos do Menu
menuLabels = ["Abrir DCC", "Salvar Alterações", "Salvar Como"]

MAIN_SECTION_TAGS = ['coreData', 'items', 'calibrationLaboratory', 'respPersons', 'customer', 'statements',
                     'dccSoftware', 'usedMethods', 'usedSoftware', 'measuringEquipments', 'influenceConditions',
                     'measurementMetaData', 'measurementResult']
GROUPING_TAGS = ['item', 'contact', 'address', 'accreditation', 'identification', 'respPerson', 'software',
                 'usedMethod', 'measuringEquipment', 'influenceCondition', 'result', 'list', 'quantity',
                 'relativeUncertainty', 'metaData', 'statement', 'reportAmendedSubstituted', 'manufacturer']
MULTILINE_TEXT_TAGS = ['description', 'declaration', 'further', 'valueXMLList', 'unitXMLList', 'labelXMLList',
                       'uncertaintyXMLList', 'coverageFactorXMLList']
LABEL_MAP = {'coreData': 'Dados Principais', 'items': 'Itens Calibrados', 'item': 'Item', 'list': 'Lista',
             'calibrationLaboratory': 'Laboratório', 'respPersons': 'Responsáveis', 'person': 'Pessoa',
             'customer': 'Cliente', 'statements': 'Declarações Gerais', 'dccSoftware': 'Software do DCC',
             'software': 'Software', 'usedMethods': 'Métodos Utilizados', 'usedMethod': 'Método Utilizado',
             'usedSoftware': 'Software Utilizado na Medição', 'measuringEquipments': 'Equipamentos de Medição',
             'measuringEquipment': 'Equipamento', 'influenceConditions': 'Condições de Influência',
             'influenceCondition': 'Condição', 'respPerson': 'Pessoa Responsável', 'mainSigner': 'Responsável Técnico',
             'uniqueIdentifier': 'ID Único',
             'countryCodeISO3166_1': 'Cód. País', 'countryCode': 'Cód. País', "further": "Complemento",
             "reference": "Referência", "declaration": "Texto Declaração", 'givenName': 'Nome Próprio',
             'familyName': 'Sobrenome', 'role': 'Cargo', 'eMail': 'E-mail', 'phone': 'Telefone', 'state': 'Estado',
             'city': 'Cidade', 'street': 'Rua', 'streetNo': 'Número', 'postCode': 'CEP', 'country': 'País',
             'accrBodyName': 'Órgão Acreditador', 'accrNumber': 'Nº Acreditação', 'accrScope': 'Escopo',
             'specification': 'Especificação', 'value': 'Valor', 'content': 'Conteúdo', 'real': 'Valor Real',
             'uncertainty': 'Incerteza', 'release': 'Versão/Release', 'model': 'Modelo', 'issuer': 'Emissor',
             'name': 'Nome', 'contact': 'Contato', 'address': 'Endereço', 'accreditation': 'Acreditação',
             'identification': 'Identificação', 'result': 'Resultado', 'quantity': 'Grandeza',
             'statementOfConformity': 'Conformidade', 'manufacturer': 'Fabricante', 'unit': 'Unidade',
             'procedure': 'Procedimento', 'norm': 'Norma', 'statement': 'Declaração', 'description': 'Descrição',
             "usedLangCodeISO639_1": "Código ISO 639", "mandatoryLangCodeISO639_1": "Código Obrigatório ISO 639",
             "date": "Data", "receiptDate": "Data de Recebimento", "beginPerformanceDate": "Data de Início",
             "endPerformanceDate": "Data de Conclusão", "performanceLocation": "Local",
             "measurementResult": "Resultado da Medição", "measurementMetaData": "Metadados da Medição",
             "valueXMLList": "Lista de Valores", "unitXMLList": "Lista de Unidades",
             "uncertaintyXMLList": "Lista de Incertezas", "coverageFactorXMLList": "Lista de Fatores de Abrangência",
             "coverageFactorXMLList": "Lista de Fatores de Abrangência",
             "coverageProbabilityXMLList": "Lista de Intervalos de Confiança",
             "distributionXMLList": "Lista de Distribuição Estatística",
             "conformityXMLList": "Conformidade"}


def clean_tag(tag):
    return tag.split('}')[-1] if '}' in tag else tag


class LocalFileResolver(ET.Resolver):
    def __init__(self, local_dir):
        self.local_dir = local_dir

    def resolve(self, url, id, context):
        filename = os.path.basename(url)
        local_path = os.path.join(self.local_dir, filename)
        if os.path.exists(local_path):
            return self.resolve_filename(local_path, context)
        return super().resolve(url, id, context)


class DCCFormEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        # self.setWindowTitle("Editor de Formulário DCC (v5.2 Multi-Schema)")
        self.setGeometry(100, 100, 900, 800)
        self.setMinimumWidth(900)
        self.xml_tree = None
        self.xml_root = None
        self.current_file_path = None
        self.form_fields = []
        self.dcc_schema = None
        self.ns = {'dcc': 'https://ptb.de/dcc'}
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&Arquivo")
        open_action = QAction(f"&{menuLabels[0]}", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        save_action = QAction(f"&{menuLabels[1]}", self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        save_as_action = QAction(f"&{menuLabels[2]}", self)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        file_menu.addSeparator()
        exit_action = QAction("&Sair", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.setCentralWidget(scroll_area)
        self.form_container = QWidget()
        self.main_layout = QVBoxLayout(self.form_container)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll_area.setWidget(self.form_container)
        self.statusbar = self.statusBar()
        self.statusbar.setFont(QFont('Arial', 9, QFont.Weight.DemiBold))
        self.statusbar.setSizeGripEnabled(False)
        self.setMouseTracking(True)
        self.countnative = 0
        self.atualizaStatusBar("Pronto", 'rgb(228,228,228)', 'bold')

    def setCurrentDCCPath(self, cfp):
        self.current_file_path = cfp

    def getCurrentDCCPath(self):
        return self.current_file_path

    def nativeEvent(self, event, tipo):
        self.countnative += 1
        if self.countnative % 1000 == 0:
            # print("alo" + event)
            self.atualizaStatusBar(f"Local do Arquivo DCC: {self.getCurrentDCCPath()}", 'rgb(255,255,255)', 'bold')
            self.countnative = 0

    def _clear_form(self):
        self.form_fields = []
        while self.main_layout.count():
            child = self.main_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _populate_form(self):
        if self.xml_root is not None:
            self._clear_form()
            self._recursive_populate(self.xml_root, self.main_layout)
        else:
            return

    def _create_form_row(self, layout, element, data_type, attr_name="", parent_element=None):
        tag = clean_tag(element.tag)
        parent_tag = clean_tag(parent_element.tag) if parent_element is not None else ""
        if tag == 'content':
            base_label = LABEL_MAP.get(parent_tag, parent_tag)
            lang = element.get('lang', '')
            label_text = f"{base_label} ({lang})" if lang else base_label
        else:
            label_text = LABEL_MAP.get(tag, tag)
            if data_type == 'attribute':
                label_text = f"{label_text} @ {clean_tag(attr_name)}"

        value = element.attrib.get(attr_name) if data_type == 'attribute' else (element.text or "").strip()

        # if tag in MULTILINE_TEXT_TAGS:
        if len(value) > 40:
            field = QTextEdit(value)
            field.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        else:
            # QLineEdit é para linhas simples
            field = QLineEdit(value)

        label_widget = QLabel(label_text + ":")
        # Configura o alinhamento de objetos QLabel em QFormLayout
        label_widget.setAlignment(Qt.AlignmentFlag.AlignRight)
        # label_widget.setWordWrap(True)
        if isinstance(layout, QFormLayout):
            layout.addRow(label_widget, field)
            self.form_fields.append({'widget': field, 'element': element, 'type': data_type, 'name': attr_name})

    def _recursive_populate(self, element, parent_layout, parent_element=None):
        tag = clean_tag(element.tag)
        if tag in ['name', 'description', 'person']:
            for child in element:
                self._recursive_populate(child, parent_layout, parent_element=element)
            return
        if tag in MAIN_SECTION_TAGS:
            title = LABEL_MAP.get(tag, tag)
            if element.get('refId'):
                title += f" (refId: {element.get('refId')})"
            section_box = QGroupBox(title)
            section_box.setCheckable(True)
            section_box.setChecked(True)
            if isinstance(parent_layout, QFormLayout):
                parent_layout.addRow(section_box)
            else:
                parent_layout.addWidget(section_box)
            content_layout = QFormLayout()
            section_box.setLayout(content_layout)
            for child in element:
                self._recursive_populate(child, content_layout, parent_element=element)
            return
        if tag in GROUPING_TAGS:
            title = LABEL_MAP.get(tag, tag)
            if element.get('value'):
                title += f" ({element.get('value')})"
            group_box = QGroupBox(title)
            if isinstance(parent_layout, QFormLayout):
                parent_layout.addRow(group_box)
            else:
                parent_layout.addWidget(group_box)
            form_layout = QFormLayout()
            group_box.setLayout(form_layout)
            for child in element:
                self._recursive_populate(child, form_layout, parent_element=element)
            return
        if isinstance(parent_layout, QFormLayout):
            if tag == 'content':
                self._create_form_row(parent_layout, element, 'text', parent_element=parent_element)
            else:
                for attr_name, _ in element.attrib.items():
                    self._create_form_row(parent_layout, element, 'attribute', attr_name, parent_element=parent_element)
                if element.text and element.text.strip():
                    self._create_form_row(parent_layout, element, 'text', parent_element=parent_element)
            for child in element:
                self._recursive_populate(child, parent_layout, parent_element=element)
        elif isinstance(parent_layout, QVBoxLayout):
            for child in element:
                self._recursive_populate(child, parent_layout, parent_element=element)

    @Slot()
    def open_file(self):
        self._clear_form()
        file_path, _ = QFileDialog.getOpenFileName(self, f"Selecione um arquivo XML para '{menuLabels[0]}'", "", "Arquivos XML (*.xml)")
        if file_path:
            self.dcc_schema = None  # Reseta o schema a cada abertura
            try:
                parser_preliminar = ET.XMLParser(resolve_entities=False, no_network=True)
                self.xml_tree = ET.parse(file_path, parser_preliminar)
                self.xml_root = self.xml_tree.getroot()
                schema_version = self.xml_root.get('schemaVersion')
                if schema_version:
                    print(f"Versão do schema detectada no DCC: {schema_version}")
                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    version_schema_dir = os.path.join(script_dir, "schemas", schema_version)

                    if os.path.isdir(version_schema_dir):
                        schema_path = os.path.join(version_schema_dir, 'dcc.xsd')
                        try:
                            resolver = LocalFileResolver(version_schema_dir)
                            parser_com_resolver = ET.XMLParser(resolve_entities=False, no_network=True)
                            parser_com_resolver.resolvers.add(resolver)

                            schema_doc = ET.parse(schema_path, parser_com_resolver)
                            self.dcc_schema = ET.XMLSchema(schema_doc)
                            print(f"Schema para a versão {schema_version} carregado com sucesso.")

                        except Exception as e:
                            QMessageBox.warning(self, "Erro no Schema",
                                                f"Erro ao carregar o schema para a versão {schema_version}:\n{e}\n"
                                                "A validação estará desativada.")
                    else:
                        QMessageBox.warning(self, "Schema Não Suportado",
                                            f"A pasta de schemas para a versão '{schema_version}' não foi encontrada.\n"
                                            f"Local esperado: {version_schema_dir}\n"
                                            "A validação de schema estará desativada.")
                else:
                    QMessageBox.warning(self, "Versão do Schema Ausente",
                                        "O atributo 'schemaVersion' não foi encontrado no arquivo DCC.\n"
                                        "A validação de schema estará desativada.")

                # self.current_file_path = file_path
                self.setCurrentDCCPath(file_path)
                self.setWindowTitle(f"Editor DCC v{version} (Schema: {schema_version or 'N/A'})")
                self.atualizaStatusBar(f"Local do Arquivo DCC: {file_path}", 'rgb(228,228,228)', 'normal')
                self._populate_form()

            except Exception as e:
                message = f"Erro ao '{menuLabels[0]}' do arquivo '{os.path.basename(file_path)}' \n | {e.args} |"
                # QMessageBox.critical(self, {menuLabels[0]}, message)
                self.atualizaStatusBar(message, 'rgb(255,0,0)', 'bold')
                # self.current_file_path = None
                self.setCurrentDCCPath(None)
                self.xml_tree = None
                self.xml_root = None

    @Slot()
    def save_file(self):
        if not self.xml_tree:
            message = f"Não foi possível '{menuLabels[1]}' | Nenhum arquivo carregado"
            self.atualizaStatusBar(message, 'orange', 'bold')
            return
        for field_info in self.form_fields:
            widget = field_info['widget']
            element = field_info['element']
            field_type = field_info['type']

            if isinstance(widget, QTextEdit):
                new_value = widget.toPlainText()
            else:  # QLineEdit
                new_value = widget.text()
            if field_type == 'text':
                element.text = new_value if new_value.strip() else None
            elif field_type == 'attribute':
                attr_name = field_info['name']
                element.set(attr_name, new_value)

        if self.dcc_schema:
            try:
                print("Validando o DCC contra o schema...")
                self.dcc_schema.assertValid(self.xml_root)
                print("Validação bem-sucedida.")
            except ET.DocumentInvalid as e:
                QMessageBox.critical(self, "Erro de Validação de Schema",
                                     "O DCC modificado não é válido de acordo com as regras do schema oficial.\n\n"
                                     f"Erro: {e}")
                return
        try:
            curr_dcc_path = self.getCurrentDCCPath()
            if curr_dcc_path is not None:
                self.xml_tree.write(curr_dcc_path,
                                    encoding="utf-8",
                                    xml_declaration=True,
                                    pretty_print=True)
                message = f"Alterações salvas com sucesso em:\n{curr_dcc_path}"
                self.atualizaStatusBar(message, 'green', 'normal')
        except Exception as e:
            QMessageBox.critical(self, "Erro ao Salvar", f"Não foi possível salvar:\n{e}")

    @Slot()
    def save_file_as(self):
        if not self.xml_tree:
            message = f"Não foi possível '{menuLabels[2]}' | Nenhum arquivo carregado."
            self.atualizaStatusBar(message, 'orange', 'bold')
            return
        file_path, _ = QFileDialog.getSaveFileName(self, f"{menuLabels[2]}", "", "Arquivos XML (*.xml)")
        if file_path:
            self.setCurrentDCCPath(file_path)
            self.save_file()

    def atualizaStatusBar(self, basemessage, bkcor, fweight):
        try:
            message = f" Status | {basemessage}"
            self.statusbar.showMessage(message)
            stylelocal = "background-color: {cor}; color: black; border: 1px solid rgb(100,156,156); font-weight:{fontweight}"
            style = stylelocal.format(cor=bkcor, fontweight=fweight)
            self.statusbar.setStyleSheet(style)
            QtCore.QCoreApplication.processEvents()
        except ValueError as ve:
            print(f"Não foi possível atualizar a barra de status: {ve}")


styleSheet = '''
QMainWindow {
    background-color: rgb(228,228,228);
}
QMenuBar {
    background-color: #F0F0F0;
    color: #000000;
    border: 1px solid #000;
    font-weight:bold
}
QMenuBar::item {
    background-color: rgb(228,228,228);
    color: black
}
QMenuBar::item::selected {
    background-color: rgb(255,255,255)
}
QCheckBox::indicator {
    width: 18px;
    height: 18px
}
QGroupBox {
    border: 2px solid white;
    border-radius: 3px;
    background-color: rgb(64,108,160);
    padding: 12px 0px 0 6px;
    margin: 6px 10px 6px 0px;
    font-size: 10pt;
    font-weight: bold
}
QGroupBox::title {
    subcontrol-origin: margin;
    border: 2px solid white;
    border-radius: 3px;
    left: 10px;
    padding: 0px 4px 0px 4px;
    background-color: rgb(192,192,192);
}
QLabel {
    font-size: 9pt;
    font-weight: bold;
    text-align: right;
    min-height: 1em;
    min-width: 16em;
    margin: 0px 0px 3px 3px;
}
QLineEdit {
    font-size: 10pt;
    font-weight: normal;
    font-family: Verdana;
    border-radius: 0px;
    background-color: rgb(228,228,228);
    min-height: 1em;
    margin: 0px 0px 3px 3px;
}
QTextEdit {
    font-size: 10pt;
    font-weight: normal;
    font-family: Verdana;
    border-radius: 1px;
    background-color: rgb(228,228,228);
    margin: 0px 0px 0 0px;
}
QTimeEdit {
    font-size: 11pt;
    background-color: rgb(192,192,192);
    min-height: 1em
}
QToolButton {
    font-size: 11pt;
    font-weight: normal;
    background-color: rgb(192,192,192);
    border-radius: 0px;
    min-height: 1em
}
QLCDNumber {
    background-color: rgb(0,0,0);
    color: rgb(255,255,255)
}
QTabBar {
    border: 0px solid #31363B;
    color: #152464
}
QTabBar::tab:top:selected {
    background-color: #0066cc;
    color: white
}
QComboBox {
    border: 0px solid black;
    background-color: #d0d0d0;
    color: black;
    selection-color: black;
    font-size: 11pt;
    font-weight: bold;
    min-height: 1em
}
'''

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = DCCFormEditor()
    editor.setWindowTitle(f"Editor de Formulário DCC (v{version} Multi-Schema)")
    app.setStyleSheet(styleSheet)
    editor.show()
    app_icon = QtGui.QIcon()
    app_icon.addFile(os.path.join("gui", "icons", "inmetro.ico"), QtCore.QSize(256, 256))
    app.setWindowIcon(app_icon)
    styles = QtWidgets.QStyleFactory.keys()
    app.setStyle(QtWidgets.QStyleFactory.create(styles[-1]))
    sys.exit(app.exec())
