# -*- coding: utf-8 -*-
# core/snippet_factory.py

import os
from lxml import etree as ET

class SnippetFactory:
    """
    Handles generation of default XML snippets for new elements.
    """
    @staticmethod
    def generate_snippet(tag_name):
        ns = 'xmlns:dcc="https://ptb.de/dcc" xmlns:si="https://ptb.de/si"'
        rnd = os.urandom(2).hex()

        if tag_name in ['type']: return f'<dcc:{tag_name} {ns}>application</dcc:{tag_name}>'
        if tag_name in ['status']: return f'<dcc:{tag_name} {ns}>beforeAdjustment</dcc:{tag_name}>'
        if tag_name in ['issuer']: return f'<dcc:{tag_name} {ns}>other</dcc:{tag_name}>'
        if tag_name in ['conformity']: return f'<dcc:{tag_name} {ns}>pass</dcc:{tag_name}>'
        if tag_name in ['performanceLocation']: return f'<dcc:{tag_name} {ns}>laboratory</dcc:{tag_name}>'
        if tag_name in ['countryCode', 'countryCodeISO3166_1']: return f'<dcc:{tag_name} {ns}>BR</dcc:{tag_name}>'
        if tag_name in ['usedLangCodeISO639_1', 'mandatoryLangCodeISO639_1']: return f'<dcc:{tag_name} {ns}>pt</dcc:{tag_name}>'
        if tag_name in ['date', 'receiptDate', 'beginPerformanceDate', 'endPerformanceDate', 'issueDate']: return f'<dcc:{tag_name} {ns}>2026-01-01</dcc:{tag_name}>'
        if tag_name in ['traceable', 'valid', 'cryptElectronicSeal', 'cryptElectronicSignature', 'cryptElectronicTimeStamp', 'mainSigner', 'inValidityRange']: return f'<dcc:{tag_name} {ns}>false</dcc:{tag_name}>'
        if tag_name in ['typeOfChange']: return f'<dcc:{tag_name} {ns}>substituted</dcc:{tag_name}>'

        if tag_name in ['name', 'description', 'declaration', 'further', 'noQuantity']:
            return f'<dcc:{tag_name} {ns}><dcc:content lang="pt">Preencher...</dcc:content></dcc:{tag_name}>'
        if tag_name == 'text':
            return f'<dcc:text {ns}><dcc:content lang="pt">Novo Texto</dcc:content></dcc:text>'

        if tag_name == 'reportAmendedSubstituted':
            return f'<dcc:reportAmendedSubstituted {ns}><dcc:typeOfChange>substituted</dcc:typeOfChange><dcc:replacedUniqueIdentifier>ID-000</dcc:replacedUniqueIdentifier></dcc:reportAmendedSubstituted>'
        if tag_name == 'refTypeDefinitions':
            return f'<dcc:refTypeDefinitions {ns}><dcc:refTypeDefinition><dcc:name><dcc:content lang="pt">Ref</dcc:content></dcc:name><dcc:namespace>ns</dcc:namespace><dcc:link>http://url</dcc:link></dcc:refTypeDefinition></dcc:refTypeDefinitions>'
        if tag_name == 'refTypeDefinition':
            return f'<dcc:refTypeDefinition {ns}><dcc:name><dcc:content lang="pt">Ref</dcc:content></dcc:name><dcc:namespace>ns</dcc:namespace><dcc:link>http://url</dcc:link></dcc:refTypeDefinition>'
        if tag_name in ['certificate', 'previousReport', 'linkedReport']:
            return f'<dcc:{tag_name} {ns}><dcc:referral><dcc:content lang="pt">Ref</dcc:content></dcc:referral><dcc:referralID>ID-00</dcc:referralID><dcc:procedure>Proc</dcc:procedure><dcc:value>Hash</dcc:value></dcc:{tag_name}>'
        if tag_name == 'relativeUncertainty':
            return f'<dcc:relativeUncertainty {ns}><si:relativeUncertaintySingle><si:value>0.01</si:value><si:unit>\\one</si:unit></si:relativeUncertaintySingle></dcc:relativeUncertainty>'
        if tag_name == 'positionCoordinates':
            return f'<dcc:positionCoordinates {ns}><dcc:positionCoordinateSystem>WGS84</dcc:positionCoordinateSystem><dcc:positionCoordinate1><si:value>0.0</si:value><si:unit>\\degree</si:unit></dcc:positionCoordinate1><dcc:positionCoordinate2><si:value>0.0</si:value><si:unit>\\degree</si:unit></dcc:positionCoordinate2></dcc:positionCoordinates>'
        if tag_name == 'software':
            return f'<dcc:software {ns}><dcc:name><dcc:content lang="pt">Software</dcc:content></dcc:name><dcc:release>1.0</dcc:release><dcc:type>application</dcc:type></dcc:software>'
        if tag_name == 'contact':
            return f'<dcc:contact {ns}><dcc:name><dcc:content lang="pt">Nome</dcc:content></dcc:name><dcc:eMail>email@exemplo.com</dcc:eMail><dcc:location><dcc:city>Cidade</dcc:city><dcc:countryCode>BR</dcc:countryCode><dcc:postCode>00000</dcc:postCode></dcc:location></dcc:contact>'
        if tag_name == 'person':
            return f'<dcc:person {ns}><dcc:name><dcc:content lang="pt">Pessoa</dcc:content></dcc:name></dcc:person>'
        if tag_name == 'location':
            return f'<dcc:location {ns}><dcc:city>Cidade</dcc:city><dcc:countryCode>BR</dcc:countryCode><dcc:postCode>00000</dcc:postCode></dcc:location>'
        if tag_name == 'identification':
            return f'<dcc:identification {ns}><dcc:issuer>other</dcc:issuer><dcc:value>ID-000</dcc:value></dcc:identification>'
        if tag_name == 'equipmentClass':
            return f'<dcc:equipmentClass {ns}><dcc:reference>Padrão</dcc:reference><dcc:classID>ID-00</dcc:classID></dcc:equipmentClass>'
        if tag_name == 'item':
            return f'<dcc:item {ns} id="item_{rnd}"><dcc:name><dcc:content lang="pt">Item</dcc:content></dcc:name><dcc:description><dcc:content lang="pt">Desc</dcc:content></dcc:description><dcc:identifications><dcc:identification><dcc:issuer>other</dcc:issuer><dcc:value>SN-000</dcc:value></dcc:identification></dcc:identifications></dcc:item>'
        if tag_name == 'result':
            return f'<dcc:result {ns} id="res_{rnd}"><dcc:name><dcc:content lang="pt">Dado</dcc:content></dcc:name><dcc:data><dcc:quantity id="q_{rnd}"><dcc:noQuantity><dcc:content lang="pt">Vazio</dcc:content></dcc:noQuantity></dcc:quantity></dcc:data></dcc:result>'
        if tag_name in ['quantity', 'itemQuantity', 'measuringEquipmentQuantity', 'usedMethodQuantity']:
            return f'<dcc:{tag_name} {ns} id="q_{rnd}"><dcc:name><dcc:content lang="pt">Grandeza</dcc:content></dcc:name><dcc:noQuantity><dcc:content lang="pt">Vazio</dcc:content></dcc:noQuantity></dcc:{tag_name}>'
        if tag_name == 'measuringEquipment':
            return f'<dcc:measuringEquipment {ns} id="me_{rnd}"><dcc:name><dcc:content lang="pt">Equipamento</dcc:content></dcc:name><dcc:identifications><dcc:identification><dcc:issuer>other</dcc:issuer><dcc:value>ID</dcc:value></dcc:identification></dcc:identifications></dcc:measuringEquipment>'
        if tag_name == 'usedMethod':
            return f'<dcc:usedMethod {ns} id="um_{rnd}"><dcc:name><dcc:content lang="pt">Método</dcc:content></dcc:name></dcc:usedMethod>'
        if tag_name == 'influenceCondition':
            return f'<dcc:influenceCondition {ns} id="ic_{rnd}"><dcc:name><dcc:content lang="pt">Condição</dcc:content></dcc:name><dcc:status>beforeAdjustment</dcc:status><dcc:data><dcc:quantity id="q_ic_{rnd}"><dcc:noQuantity><dcc:content lang="pt">Vazio</dcc:content></dcc:noQuantity></dcc:quantity></dcc:data></dcc:influenceCondition>'
        if tag_name in ['statement', 'metaData']:
            return f'<dcc:{tag_name} {ns} id="st_{rnd}"><dcc:declaration><dcc:content lang="pt">Texto</dcc:content></dcc:declaration></dcc:{tag_name}>'
        if tag_name == 'formula':
            return f'<dcc:formula {ns}><dcc:latex>x=y</dcc:latex></dcc:formula>'
        if tag_name in ['byteData', 'descriptionData', 'document']:
            return f'<dcc:{tag_name} {ns}><dcc:fileName>arq.txt</dcc:fileName><dcc:mimeType>text/plain</dcc:mimeType><dcc:dataBase64>eA==</dcc:dataBase64></dcc:{tag_name}>'
        if tag_name == 'xml':
            return f'<dcc:xml {ns}><dcc:text><dcc:content lang="pt">Custom XML</dcc:content></dcc:text></dcc:xml>'
        
        if tag_name == 'real': return f'<si:real {ns}><si:value>0.0</si:value><si:unit>\\one</si:unit></si:real>'
        if tag_name == 'hybrid': return f'<si:hybrid {ns}><si:real><si:value>0.0</si:value><si:unit>\\one</si:unit></si:real></si:hybrid>'
        if tag_name == 'complex': return f'<si:complex {ns}><si:valueReal>0.0</si:valueReal><si:valueImag>0.0</si:valueImag><si:unit>\\one</si:unit></si:complex>'
        if tag_name == 'constant': return f'<si:constant {ns}><si:value>0.0</si:value><si:unit>\\one</si:unit><si:dateTime>2026-01-01T00:00:00</si:dateTime></si:constant>'
        if tag_name == 'realListXMLList': return f'<si:realListXMLList {ns}><si:valueXMLList>0.0</si:valueXMLList><si:unitXMLList>\\one</si:unitXMLList></si:realListXMLList>'
        if tag_name == 'complexListXMLList': return f'<si:complexListXMLList {ns}><si:valueRealXMLList>0.0</si:valueRealXMLList><si:valueImagXMLList>0.0</si:valueImagXMLList><si:unitXMLList>\\one</si:unitXMLList></si:complexListXMLList>'
        
        # Fallback dynamic creation for unknown tags 
        return f'<dcc:{tag_name} {ns}>Preencher...</dcc:{tag_name}>'
