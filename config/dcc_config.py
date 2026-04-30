# -*- coding: utf-8 -*-
# config/dcc_config.py

# ==============================================================================
# FALLBACK TAGS CONFIGURATION
# Used if Schema parser cannot find dynamic relationships
# ==============================================================================

MAIN_SECTION_TAGS = [
    'administrativeData', 'measurementResults', 'refTypeDefinitions', 'comment',
    'coreData', 'items', 'calibrationLaboratory', 'respPersons', 'customer', 'statements',
    'dccSoftware', 'usedMethods', 'usedSoftware', 'measuringEquipments', 'influenceConditions',
    'measurementMetaData', 'measurementResult', 'Signature'
]

GROUPING_TAGS = [
    'identifications', 'identification', 'item', 'contact', 'address', 'accreditation', 'respPerson', 
    'software', 'installedSoftwares', 'installedSoftware', 'itemQuantities', 'itemQuantity', 
    'measuringEquipmentQuantities', 'measuringEquipmentQuantity', 'usedMethodQuantities', 'usedMethodQuantity',
    'usedMethod', 'measuringEquipment', 'influenceCondition', 'results', 'result', 'list', 'quantity',
    'relativeUncertainty', 'metaData', 'statement', 'reportAmendedSubstituted', 'manufacturer',
    'refTypeDefinition', 'document', 'equipmentClass', 'owner', 'subItems', 'location', 'positionCoordinates', 
    'respAuthority', 'certificate', 'previousReport', 'linkedReport', 'data', 'formula', 'byteData', 'xml',
    'hybrid', 'complex', 'constant', 'realList', 'complexList', 'realListXMLList', 
    'complexListXMLList', 'measurementUncertaintyUnivariate', 'standardMU', 'expandedMU', 
    'coverageIntervalMU', 'ellipsoidalRegion', 'rectangularRegion', 'covarianceMatrix', 
    'column', 'covariance', 'listMeasurementUncertaintyUnivariate', 'listBivariateUnc',
    'measurementUncertaintyMultivariateXMLList', 'listUnivariateUnc', 'ellipsoidalRegionMUXMLList',
    'rectangularRegionMUXMLList', 'covarianceMatrixXMLList', 'columnXMLList', 'covarianceXMLList',
    'measurementUncertaintyUnivariateXMLList', 'standardMUXMLList', 'expandedMUXMLList', 
    'coverageIntervalMUXMLList',
    'SignedInfo', 'KeyInfo', 'X509Data', 'Reference', 'Transforms', 'Object', 'Manifest', 
    'SignatureProperties', 'PGPData', 'SPKIData', 'KeyValue', 'RSAKeyValue', 'DSAKeyValue'
]

MULTILINE_TEXT_TAGS = [
    'description', 'declaration', 'further', 'noQuantity', 'charsXMLList', 'content', 'file',
    'dataBase64', 'latex', 'mathml', 'SignatureValue', 'DigestValue', 'X509Certificate', 'X509CRL', 
    'PGPKeyPacket', 'SPKISexp', 'Modulus', 'Exponent', 'P', 'Q', 'G', 'Y', 'J', 'Seed', 'PgenCounter',
    'valueXMLList', 'unitXMLList', 'labelXMLList', 'uncertaintyXMLList', 'coverageFactorXMLList',
    'valueRealXMLList', 'valueImagXMLList', 'valueMagnitudeXMLList', 'valuePhaseXMLList', 
    'unitPhaseXMLList', 'intervalMinXMLList', 'intervalMaxXMLList', 'distributionXMLList', 
    'valueStandardMUXMLList', 'valueExpandedMUXMLList', 'dateTimeXMLList', 'coverageProbabilityXMLList',
    'validXMLList', 'conformityXMLList', 'significantDigitXMLList'
]

# ==============================================================================
# LABEL MAP (Translation keys)
# ==============================================================================
LABEL_MAP = {
    'coreData': 'Dados Principais', 'items': 'Itens Calibrados', 'item': 'Item', 'list': 'Lista',
    'calibrationLaboratory': 'Laboratório', 'respPersons': 'Responsáveis', 'person': 'Pessoa',
    'customer': 'Cliente', 'statements': 'Declarações Gerais', 'dccSoftware': 'Software do DCC',
    'software': 'Software', 'usedMethods': 'Métodos Utilizados', 'usedMethod': 'Método Utilizado',
    'usedSoftware': 'Software Utilizado', 'installedSoftwares': 'Softwares Instalados', 'installedSoftware': 'Software Instalado',
    'measuringEquipments': 'Equipamentos de Medição', 'measuringEquipment': 'Equipamento', 'influenceConditions': 'Condições de Influência',
    'influenceCondition': 'Condição', 'respPerson': 'Pessoa Responsável', 'mainSigner': 'Resp. Técnico (Signatário)',
    'uniqueIdentifier': 'ID Único', 'countryCodeISO3166_1': 'Cód. País (ISO 3166)', 'countryCode': 'Cód. País', 
    'further': 'Complemento', 'reference': 'Referência', 'declaration': 'Texto da Declaração', 
    'givenName': 'Nome Próprio', 'familyName': 'Sobrenome', 'role': 'Cargo/Função', 'eMail': 'E-mail', 
    'phone': 'Telefone', 'fax': 'Fax', 'state': 'Estado/Província', 'city': 'Cidade', 'street': 'Rua', 'streetNo': 'Número', 
    'postCode': 'CEP', 'postOfficeBox': 'Caixa Postal', 'country': 'País', 'accrBodyName': 'Órgão Acreditador', 
    'accrNumber': 'Nº Acreditação', 'accrScope': 'Escopo de Acreditação', 'specification': 'Especificação', 
    'value': 'Valor', 'content': 'Conteúdo', 'real': 'Valor Real (Decimal)', 'uncertainty': 'Incerteza', 
    'release': 'Versão/Release', 'model': 'Modelo', 'issuer': 'Emissor', 'name': 'Nome', 'contact': 'Contato', 
    'address': 'Endereço', 'accreditation': 'Acreditação', 'identifications': 'Identificações', 'identification': 'Identificação',
    'results': 'Lista de Resultados', 'result': 'Resultado', 'quantity': 'Grandeza', 'statementOfConformity': 'Declaração de Conformidade', 
    'manufacturer': 'Fabricante', 'unit': 'Unidade', 'procedure': 'Procedimento', 'norm': 'Norma', 
    'statement': 'Declaração', 'description': 'Descrição', 'relativeUncertainty': 'Incerteza Relativa',
    'metaData': 'Metadados', 'reportAmendedSubstituted': 'Relatório Alterado/Substituído', 'typeOfChange': 'Tipo de Alteração',
    'replacedUniqueIdentifier': 'ID Único Substituído',
    "usedLangCodeISO639_1": "Idioma Utilizado (ISO 639)", "mandatoryLangCodeISO639_1": "Idioma Obrigatório (ISO 639)",
    "date": "Data", "receiptDate": "Data de Recebimento", "beginPerformanceDate": "Data de Início da Calibração",
    "endPerformanceDate": "Data de Conclusão", "performanceLocation": "Local da Calibração",
    "measurementResult": "Resultado da Medição", "measurementMetaData": "Metadados da Medição",
    'administrativeData': 'Dados Administrativos', 'measurementResults': 'Resultados das Medições',
    'refTypeDefinitions': 'Definições de Tipos de Referência', 'refTypeDefinition': 'Definição de Tipo de Referência',
    'document': 'Documento Anexo', 'comment': 'Comentário Geral', 'byteData': 'Dados Binários (ByteData)', 
    'dataBase64': 'Conteúdo Base64', 'fileName': 'Nome do Arquivo', 'mimeType': 'Tipo MIME', 
    'formula': 'Fórmula Matemática', 'latex': 'Código LaTeX', 'mathml': 'Código MathML', 
    'xml': 'XML Customizado', 'data': 'Dados Associados', 'descriptionData': 'Dados de Descrição (Anexo)',
    'equipmentClass': 'Classe do Equipamento', 'classID': 'ID da Classe', 'owner': 'Proprietário',
    'itemQuantities': 'Grandezas do Item', 'itemQuantity': 'Grandeza do Item',
    'measuringEquipmentQuantities': 'Grandezas do Equip.', 'measuringEquipmentQuantity': 'Grandeza do Equip.',
    'subItems': 'Sub-itens', 'location': 'Localização', 'positionCoordinates': 'Coordenadas de Posição',
    'positionCoordinateSystem': 'Sistema de Coordenadas', 'positionCoordinate1': 'Coordenada de Posição 1',
    'positionCoordinate2': 'Coordenada de Posição 2', 'positionCoordinate3': 'Coordenada de Posição 3',
    'respAuthority': 'Autoridade Responsável', 'certificate': 'Certificado Vinculado',
    'previousReport': 'Relatório Anterior', 'linkedReport': 'Relatório Vinculado',
    'usedMethodQuantities': 'Grandezas do Método', 'usedMethodQuantity': 'Grandeza do Método',
    'calibrationLaboratoryCode': 'Código do Laboratório', 'cryptElectronicSeal': 'Selo Eletrônico (Criptografia)',
    'cryptElectronicSignature': 'Assinatura Eletrônica (Criptografia)', 'cryptElectronicTimeStamp': 'Carimbo de Tempo',
    'issueDate': 'Data de Emissão', 'valid': 'Status de Validade', 'period': 'Período de Validade',
    'traceable': 'Rastreável', 'convention': 'Convenção Adotada', 'nonSIDefinition': 'Definição Não-SI',
    'nonSIUnit': 'Unidade Não-SI', 'status': 'Status da Condição', 'type': 'Tipo de Registo',
    'referral': 'Referência (Referral)', 'referralID': 'ID da Referência', 'inValidityRange': 'Dentro da Faixa de Validade',
    'lang': 'Idioma', 'id': 'ID do Elemento', 'refId': 'ID de Referência', 'refType': 'Tipo de Referência',
    'schemaVersion': 'Versão do Schema', 'Id': 'ID da Assinatura (XMLDSig)',
    'digitalCalibrationCertificate': 'Certificado Digital de Calibração', 'noQuantity': 'Sem Grandeza', 'text': 'Texto Genérico'
}
