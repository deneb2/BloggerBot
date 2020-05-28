class MetadataException(Exception):
    """ exception raised if any error during metadata extraction"""
    def __init__(self, message):
        super().__init__(message)

