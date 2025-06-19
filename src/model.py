from dataclasses import dataclass, fields
import csv


@dataclass
class Product:
    name: str
    brand: str
    price: int
    rating: float


def check_field(field_name, dataclass_type=Product):
    # Получаем все поля датакласса
    class_fields = {f.name: f for f in fields(dataclass_type)}

    if field_name in class_fields:
        field = class_fields[field_name]
        return {
            "exists": True,
            "type": field.type,
            "default": (
                field.default if field.default != field.default_factory else "factory"
            ),
            "is_required": field.default is field.default_factory is None,
        }
    return {"exists": False}


def from_csv_to_product(path: str):
    try:
        with open(path, mode="r", encoding="utf-8") as file:
            csv_reader = csv.DictReader(file)
            data = list(csv_reader)
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")

    products: list[Product] = []

    try:
        for row in data:
            products.append(
                Product(
                    name=str(row["name"]),
                    brand=str(row["brand"]),
                    price=int(row["price"]),
                    rating=float(row["rating"]),
                )
            )

        return products
    except Exception as e:
        print(f'Ошибка при конвертации данных в "Products: {e}"')
