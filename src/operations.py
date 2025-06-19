from abc import ABC, abstractmethod
from typing import List
from src.model import Product, check_field
from tabulate import tabulate


class Operation(ABC):
    @abstractmethod
    def execute(self, data: List[Product], arg: str) -> List[Product]:
        pass


class WhereOperation(Operation):
    def execute(self, data: List[Product], arg: str) -> List[Product]:
        ops = ["<", ">", "="]
        op = None

        # Ищем оператор в строке условия
        for op_symbol in ops:
            if op_symbol in arg:
                key, value = arg.split(op_symbol, 1)
                key, value = key.strip(), value.strip()
                op = op_symbol
                break

        if not op:
            raise ValueError(f"Неизвестный оператор в условии: {arg}")

        # Проверяем существование поля
        check = check_field(field_name=key, dataclass_type=Product)
        if not check.get("exists"):
            raise ValueError(f"Поле {key} не существует")

        field_type = check.get("type")
        is_numeric = field_type in (int, float)

        if not is_numeric and op != "=":
            raise ValueError(f"Оператор {op} применим только к числовым полям")

        try:
            if is_numeric:
                value = float(value) if "." in value else int(value)
            elif field_type is bool:
                value = value.lower() in ("true", "1", "yes")
            else:
                value = str(value)
        except ValueError:
            raise ValueError(f"Невозможно преобразовать '{value}' в {field_type}")

        match op:
            case "<" if is_numeric:
                op_func = lambda p: getattr(p, key) < value
            case ">" if is_numeric:
                op_func = lambda p: getattr(p, key) > value
            case "=":
                op_func = lambda p: str(getattr(p, key)) == str(value)
            case _:
                raise ValueError(f"Недопустимый оператор {op} для типа {field_type}")

        return [p for p in data if op_func(p)]


class AggregateOperation(Operation):
    def execute(self, data: List[Product], arg: str) -> List[Product]:
        key, func_name = arg.split("=", maxsplit=1)

        # Проверяем поле
        check = check_field(field_name=key, dataclass_type=Product)
        if not (check.get("exists") and check.get("type") in (int, float)):
            raise ValueError(f"Поле {key} не существует или имеет нечисловой тип")

        match func_name:
            case "min":
                return [min(data, key=lambda p: getattr(p, key))]
            case "max":
                return [max(data, key=lambda p: getattr(p, key))]
            case "avg":
                # Выводит среднее значение и продукт, который ближе всего к среднему значению.
                avg_value = sum(getattr(p, key) for p in data) / len(data)
                print(tabulate([{"avg": avg_value}], headers="keys", tablefmt="grid"))
                closest = min(data, key=lambda p: abs(getattr(p, key) - avg_value))
                return [closest]
            case _:
                raise ValueError(f"Неизвестная агрегатная функция: {func_name}")
