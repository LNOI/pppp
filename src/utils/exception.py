class ApiInputValidationError(Exception):
    pass

class WrapperInterfaceError(Exception):
    pass

class FaissIndexError(WrapperInterfaceError):
    pass

class DBError(WrapperInterfaceError):
    pass

class SQLalchemyError(DBError):
    pass

class RawQueryError(DBError):
    pass

class RedisError(WrapperInterfaceError):
    pass

class RedisKeyNotExistError(RedisError):
    pass

class RedisIncorrectTypeError(RedisError):
    pass

class S3Error(WrapperInterfaceError):
    pass

class S3UploadError(S3Error):
    pass

class S3DownloadError(S3Error):
    pass

class S3NotExistError(S3DownloadError):
    pass

class S3OtherDownloadError(S3DownloadError):
    pass

class InputError(Exception):
    pass

class NoneInputError(InputError):
    pass

class PostEncodeError(Exception):
    pass

class NotificationError(Exception):
    pass