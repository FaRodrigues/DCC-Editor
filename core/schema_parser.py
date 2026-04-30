# -*- coding: utf-8 -*-
# core/schema_parser.py

from lxml import etree as ET
import urllib.parse
from config.dcc_config import MAIN_SECTION_TAGS, GROUPING_TAGS

class SchemaParser:
    """
    Reads an XSD schema to dynamically identify parent-child relationships,
    allowed tags and structural properties to be used in UI generation.
    """
    def __init__(self, schema_doc):
        self.schema_doc = schema_doc
        self.ns = {'xs': 'http://www.w3.org/2001/XMLSchema'}
        self.tree = self.schema_doc
        self.root = self.tree.getroot()
        self.type_definitions = {}
        self.element_cache = {}
        
        self.dcc_ns = self.root.attrib.get('targetNamespace', 'https://ptb.de/dcc')
        
        # Precompute types
        self._analyze_types()

    def _clean_ref(self, ref_str):
        if not ref_str:
            return None
        return ref_str.split(':')[-1] if ':' in ref_str else ref_str

    def _analyze_types(self):
        """Build a dictionary of complexTypes for fast resolution."""
        for ctype in self.root.findall('.//xs:complexType', self.ns):
            name = ctype.get('name')
            if name:
                self.type_definitions[name] = ctype

    def get_allowed_children(self, element_tag_name):
        """
        Dynamically traverse XSD to find allowed children for a given tag.
        Returns a dictionary containing 'children' (list) and 'multiple' (list of tags allowed to repeat).
        """
        if element_tag_name in self.element_cache:
            return self.element_cache[element_tag_name]

        children = []
        multiple = []
        
        # 1. Find the element definition
        elem_node = self.root.find(f".//xs:element[@name='{element_tag_name}']", self.ns)
        if elem_node is None:
            # Maybe it's defined inside another element without a global name but we can search for it broadly
            # Though in DCC schema mostly everything inherits from globally defined complexTypes
            pass
        
        type_name = None
        complex_node = None
        
        if elem_node is not None:
            type_name = self._clean_ref(elem_node.get('type'))
            complex_node = elem_node.find('./xs:complexType', self.ns)
        
        # 2. Resolve complex type
        if type_name and type_name in self.type_definitions:
            complex_node = self.type_definitions[type_name]

        if complex_node is not None:
            # 3. Handle structure (sequence, choice, all, complexContent->extension)
            self._extract_elements_from_node(complex_node, children, multiple)

        # Remove duplicates while preserving order
        unique_children = []
        seen = set()
        for c in children:
            if c not in seen:
                seen.add(c)
                unique_children.append(c)

        result = {'children': unique_children, 'multiple': list(set(multiple))}
        self.element_cache[element_tag_name] = result
        return result

    def _extract_elements_from_node(self, container_node, children_list, multiple_list):
        # Examine direct elements
        for el in container_node.findall('.//xs:element', self.ns):
            # Ensure it's not nested inside another element definition
            parent_el = el.getparent()
            parent_is_element = False
            while parent_el is not None and parent_el != container_node:
                if parent_el.tag == f"{{{self.ns['xs']}}}element":
                    parent_is_element = True
                    break
                parent_el = parent_el.getparent()
            
            if parent_is_element:
                continue

            name = el.get('name')
            ref = el.get('ref')
            
            tag = name if name else self._clean_ref(ref)
            if not tag:
                continue
                
            children_list.append(tag)
            max_occurs = el.get('maxOccurs', '1')
            if max_occurs == 'unbounded' or (max_occurs.isdigit() and int(max_occurs) > 1):
                multiple_list.append(tag)

        # Handle extensions (complexContent -> extension)
        for ext in container_node.findall('.//xs:extension', self.ns):
            base_type = self._clean_ref(ext.get('base'))
            if base_type and base_type in self.type_definitions:
                self._extract_elements_from_node(self.type_definitions[base_type], children_list, multiple_list)
            
            # Extract elements inside the extension itself
            for el in ext.findall('.//xs:element', self.ns):
                name = el.get('name')
                ref = el.get('ref')
                tag = name if name else self._clean_ref(ref)
                if tag:
                    children_list.append(tag)
                    max_occurs = el.get('maxOccurs', '1')
                    if max_occurs == 'unbounded' or (max_occurs.isdigit() and int(max_occurs) > 1):
                        multiple_list.append(tag)

    def is_grouping_tag(self, tag):
        # We can dynamically decide if it's grouping by checking if it allows children.
        # But we also have fallbacks for visual purposes
        res = self.get_allowed_children(tag)
        if res['children']:
            return True
        return tag in GROUPING_TAGS

    def is_main_section(self, tag):
        return tag in MAIN_SECTION_TAGS

    def generate_minimal_xml(self, schema_version):
        out_root = ET.Element(f"{{{self.dcc_ns}}}digitalCalibrationCertificate", nsmap={
            None: self.dcc_ns,
            'si': 'https://ptb.de/si',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
        })
        out_root.set('schemaVersion', schema_version)
        self._build_tree(out_root, 'digitalCalibrationCertificate', depth=0)
        return ET.ElementTree(out_root)
        
    def _get_mandatory_elements(self, node):
        mandatory = []
        try:
            children = node if isinstance(node, list) else list(node)
        except:
            children = []
            
        for child in children:
            tag = child.tag.split('}')[-1]
            
            if tag in ['sequence', 'all']:
                if child.get('minOccurs') == '0':
                    continue
                mandatory.extend(self._get_mandatory_elements(child))
                
            elif tag == 'choice':
                if child.get('minOccurs') == '0':
                    continue
                if len(child) > 0:
                    # Satisfy choice by strictly picking formatting of first option
                    mandatory.extend(self._get_mandatory_elements([child[0]]))
                    
            elif tag == 'element':
                if child.get('minOccurs', '1') != '0':
                    name = child.get('name')
                    ref = child.get('ref')
                    val = name if name else self._clean_ref(ref)
                    if val: mandatory.append(val)
                    
            elif tag == 'complexContent':
                mandatory.extend(self._get_mandatory_elements(child))
                
            elif tag == 'extension':
                base_type = self._clean_ref(child.get('base'))
                if base_type and base_type in self.type_definitions:
                    mandatory.extend(self._get_mandatory_elements(self.type_definitions[base_type]))
                mandatory.extend(self._get_mandatory_elements(child))
                
        result = []
        for m in mandatory:
            if m not in result: result.append(m)
        return result

    def _build_tree(self, current_el, tag_name, depth=0):
        if depth > 10: return
        
        import os
        from core.snippet_factory import SnippetFactory
        elem_node = self.root.xpath(f".//xs:element[@name='{tag_name}']", namespaces=self.ns)
        if not elem_node: 
            current_el.text = "Preencher..."
            return
            
        elem_node = elem_node[0]
        type_name = self._clean_ref(elem_node.get('type'))
        complex_node = elem_node.find('./xs:complexType', self.ns)
        
        if type_name and type_name in self.type_definitions:
            complex_node = self.type_definitions[type_name]
            
        if complex_node is not None:
            mandatory = self._get_mandatory_elements(complex_node)
            for child_tag in mandatory:
                snippet_str = SnippetFactory.generate_snippet(child_tag)
                fallback = f'<dcc:{child_tag} xmlns:dcc="https://ptb.de/dcc" xmlns:si="https://ptb.de/si">Preencher...</dcc:{child_tag}>'
                
                if snippet_str != fallback:
                    try:
                        parsed = ET.fromstring(snippet_str)
                        current_el.append(parsed)
                        continue
                    except: pass
                
                child_el = ET.Element(f"{{{self.dcc_ns}}}{child_tag}")
                
                if child_tag in ['item', 'measuringEquipment', 'usedMethod', 'influenceCondition', 'result', 'quantity', 'list']:
                    child_el.set('id', f"{child_tag}_{os.urandom(2).hex()}")
                if child_tag in ['content', 'text']:
                    child_el.set('lang', 'pt')
                
                current_el.append(child_el)
                self._build_tree(child_el, child_tag, depth+1)
        else:
            if tag_name in ['status']: current_el.text = 'beforeAdjustment'
            elif tag_name in ['type']: current_el.text = 'application'
            elif tag_name in ['conformity']: current_el.text = 'pass'
            elif tag_name in ['issuer']: current_el.text = 'other'
            elif 'Date' in tag_name or tag_name == 'date': current_el.text = '2026-01-01'
            elif tag_name in ['countryCode', 'countryCodeISO3166_1']: current_el.text = 'BR'
            elif tag_name in ['usedLangCodeISO639_1', 'mandatoryLangCodeISO639_1']: current_el.text = 'pt'
            else: current_el.text = "Preencher..."
