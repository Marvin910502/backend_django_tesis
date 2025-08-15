# utils/filters.py
from typing import Iterable, Sequence, Tuple, Any, List, Optional, Set
from django.db.models import Q
from django.core.exceptions import ValidationError

FrontFilter = Tuple[str, str, Any]

def convert_filter(
    filters: Sequence[FrontFilter],
    allowed_fields: Optional[Set[str]] = None,   # lista blanca opcional
) -> Q:
    """
    Convierte FrontFilter[] -> Q combinando todo con AND.
    Operadores soportados: =, !=, <, <=, >, >=, in, not in, ilike, not like, isnull, isnotnull
    """
    q_total = Q()

    for raw_field, op, value in filters:
        # Validación (opcional pero recomendable)
        base_field = raw_field.split("__", 1)[0]
        if allowed_fields is not None and base_field not in allowed_fields:
            raise ValidationError(f"Campo no permitido: {base_field}")

        negate = False

        if op == "=":
            lookup = raw_field
        elif op == "!=":
            lookup = raw_field
            negate = True
        elif op == "<":
            lookup = f"{raw_field}__lt"
        elif op == "<=":
            lookup = f"{raw_field}__lte"
        elif op == ">":
            lookup = f"{raw_field}__gt"
        elif op == ">=":
            lookup = f"{raw_field}__gte"
        elif op == "in":
            lookup = f"{raw_field}__in"
            if not isinstance(value, (list, tuple, set)):
                raise ValidationError(f"El operador 'in' requiere lista/tupla/set; recibido: {type(value).__name__}")
        elif op == "not in":
            lookup = f"{raw_field}__in"
            negate = True
            if not isinstance(value, (list, tuple, set)):
                raise ValidationError(f"El operador 'not in' requiere lista/tupla/set; recibido: {type(value).__name__}")
        elif op == "ilike":
            # Búsqueda case-insensitive tipo ILIKE %valor%
            lookup = f"{raw_field}__icontains"
            if value is None:
                value = ""  # evita error si llega null
        elif op == "not like":
            lookup = f"{raw_field}__icontains"
            negate = True
            if value is None:
                value = ""
        elif op == "isnull":
            lookup = f"{raw_field}__isnull"
            value = True
        elif op == "isnotnull":
            lookup = f"{raw_field}__isnull"
            value = False
        else:
            raise ValidationError(f"Operador no soportado: {op}")

        condition = Q(**{lookup: value})
        q_total &= ~condition if negate else condition

    return q_total
