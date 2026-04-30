# -*- coding: utf-8 -*-
# core/xml_handler.py

import os
from lxml import etree as ET
from .schema_parser import SchemaParser

class LocalFileResolver(ET.Resolver):
    def __init__(self, local_dir):
        self.local_dir = local_dir

    def resolve(self, url, id, context):
        filename = os.path.basename(url)
        local_path = os.path.join(self.local_dir, filename)
        if os.path.exists(local_path):
            return self.resolve_filename(local_path, context)
        return super().resolve(url, id, context)

class XMLHandler:
    """
    Handles loading, parsing, and validating XML with local Schemas.
    """
    def __init__(self, schemas_base_path):
        self.schemas_base_path = schemas_base_path
        self.xml_tree = None
        self.xml_root = None
        self.dcc_schema = None
        self.schema_parser = None
        self.schema_version = None

    def load_xml(self, file_path):
        parser_preliminar = ET.XMLParser(resolve_entities=False, no_network=True)
        self.xml_tree = ET.parse(file_path, parser_preliminar)
        self.xml_root = self.xml_tree.getroot()
        self.schema_version = self.xml_root.get('schemaVersion')
        
        if self.schema_version:
            version_schema_dir = os.path.join(self.schemas_base_path, self.schema_version)
            if os.path.isdir(version_schema_dir):
                schema_path = os.path.join(version_schema_dir, 'dcc.xsd')
                try:
                    resolver = LocalFileResolver(version_schema_dir)
                    parser_com_resolver = ET.XMLParser(resolve_entities=False, no_network=True)
                    parser_com_resolver.resolvers.add(resolver)
                    schema_doc = ET.parse(schema_path, parser_com_resolver)
                    self.dcc_schema = ET.XMLSchema(schema_doc)
                    self.schema_parser = SchemaParser(schema_doc)
                except Exception as e:
                    raise Exception(f"Erro ao carregar o schema XSD:\n{e}")
            else:
                raise Exception(f"A pasta de schemas para a versão '{self.schema_version}' não foi encontrada.")
        else:
            raise Exception("O atributo 'schemaVersion' não foi encontrado no XML.")
        
        return self.xml_tree, self.xml_root, self.dcc_schema, self.schema_parser

    def load_schema(self, schema_version):
        self.schema_version = schema_version
        version_schema_dir = os.path.join(self.schemas_base_path, schema_version)
        if not os.path.isdir(version_schema_dir):
            raise Exception(f"A pasta de schemas para a versão '{schema_version}' não foi encontrada.")
            
        schema_path = os.path.join(version_schema_dir, 'dcc.xsd')
        if not os.path.exists(schema_path):
            raise Exception(f"O arquivo dcc.xsd não foi encontrado em '{version_schema_dir}'.")
            
        resolver = LocalFileResolver(version_schema_dir)
        parser_com_resolver = ET.XMLParser(resolve_entities=False, no_network=True)
        parser_com_resolver.resolvers.add(resolver)
        schema_doc = ET.parse(schema_path, parser_com_resolver)
        self.dcc_schema = ET.XMLSchema(schema_doc)
        self.schema_parser = SchemaParser(schema_doc)
        return self.dcc_schema, self.schema_parser

    def validate_xml(self, tree_to_save):
        if self.dcc_schema:
            try:
                self.dcc_schema.assertValid(tree_to_save.getroot())
                return True, None
            except ET.DocumentInvalid as e:
                return False, str(e)
        return True, None
