from typing import List, Mapping, Any
from marshmallow import fields
from marshmallow.exceptions import ValidationError
from marshmallow.validate import URL


class UnionField(fields.Field):
    def __init__(self, val_types: List[fields.Field]):
        self.valid_types = val_types
        super().__init__()

    def _deserialize(self, value: Any, attr: str = None, data: Mapping[str, Any] = None, **kwargs):
        errors = []
        for field in self.valid_types:
            try:
                return field.deserialize(value, attr, data, **kwargs)
            except ValidationError as error:
                errors.append(error.messages)
                raise ValidationError(errors)

class NullableURL(URL):
    def __call__(self, value) -> Any:
        if type(value) is str and len(value) < 1:
            return value
        return super().__call__(value)