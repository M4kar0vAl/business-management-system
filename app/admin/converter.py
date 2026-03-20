from typing import Any

from sqladmin.fields import DateTimeField
from sqladmin.forms import ModelConverter as ModelConverterBase
from sqladmin.forms import converts
from sqlalchemy.orm import ColumnProperty
from wtforms.fields.core import UnboundField


class ModelConverter(ModelConverterBase):
    @converts("TIMESTAMPAware")
    def conv_timestamp_aware(
        self,
        model: type,  # noqa: ARG002
        prop: ColumnProperty,  # noqa: ARG002
        kwargs: dict[str, Any],
    ) -> UnboundField:
        return DateTimeField(**kwargs)
