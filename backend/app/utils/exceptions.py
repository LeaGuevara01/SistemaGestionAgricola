class ImportError(Exception):
    """Excepción base para errores de importación"""
    pass

class CSVParseError(ImportError):
    """Error al parsear archivo CSV"""
    pass

class ValidationError(ImportError):
    """Error de validación de datos"""
    pass

class BulkImportError(ImportError):
    """Error durante importación masiva"""
    pass