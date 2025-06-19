import argparse
from tabulate import tabulate
from dataclasses import asdict
from src.operations import WhereOperation, AggregateOperation
from src.model import from_csv_to_product


OPERATIONS = {"filter": WhereOperation, "aggregate": AggregateOperation}


def main():
    try:
        # Парсинг аргументов
        arg_parser = argparse.ArgumentParser(description="Фильтрация CSV-файла")
        arg_parser.add_argument("--file", required=True, help="Путь к CSV-файлу")

        for op_name in OPERATIONS:
            arg_parser.add_argument(f"--{op_name}", help=f"Условие для {op_name}")

        args = arg_parser.parse_args()

        # Загрузка данных
        result = from_csv_to_product(args.file)

        # Применение операций
        for op_name, op_class in OPERATIONS.items():
            if arg_value := getattr(args, op_name, None):
                operation = op_class()
                result = operation.execute(result, arg_value)

        # Вывод результатов
        if not result:
            print("Нет данных, соответствующих условию")
            return

        print(tabulate([asdict(p) for p in result], headers="keys", tablefmt="grid"))

    except FileNotFoundError:
        print(f"Ошибка: файл {args.file} не найден")
    except Exception as e:
        print(f"Ошибка: {str(e)}")


if __name__ == "__main__":
    main()
