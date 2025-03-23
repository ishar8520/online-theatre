class AdminNotificationNotFoundError(Exception):
    pass


class DeliveryNotFoundError(Exception):
    pass


class DatabaseError(Exception):
    pass


class TemplateNotFoundError(Exception):
    pass


class TemplateTypeNotFoundError(Exception):
    pass


class TemplateAlreadyExistsError(Exception):
    pass


class SystemTemplateOperationNotAllowedError(Exception):
    pass

