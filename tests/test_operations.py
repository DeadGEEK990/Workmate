import pytest
from src.model import Product
from src.operations import WhereOperation, AggregateOperation


@pytest.fixture
def sample_products():
    return [
        Product(name="iphone 15 pro", brand="apple", price=999, rating=4.9),
        Product(name="galaxy s23 ultra", brand="samsung", price=1199, rating=4.8),
        Product(name="redmi note 12", brand="xiaomi", price=199, rating=4.6),
        Product(name="iphone 14", brand="apple", price=799, rating=4.7),
    ]


class TestWhereOperation:
    def test_numeric_greater_than_price(self, sample_products):
        op = WhereOperation()
        result = op.execute(sample_products, "price>1000")
        assert len(result) == 1
        assert result[0].name == "galaxy s23 ultra"
        assert result[0].price == 1199

    def test_numeric_equals_rating(self, sample_products):
        op = WhereOperation()
        result = op.execute(sample_products, "rating=4.6")
        assert len(result) == 1
        assert result[0].name == "redmi note 12"

    def test_string_condition_brand(self, sample_products):
        op = WhereOperation()
        result = op.execute(sample_products, "brand=apple")
        assert len(result) == 2
        assert all(p.brand == "apple" for p in result)
        assert "iphone 15 pro" in [p.name for p in result]
        assert "iphone 14" in [p.name for p in result]

    def test_invalid_operator_for_string(self, sample_products):
        op = WhereOperation()
        with pytest.raises(ValueError, match="применим только к числовым полям"):
            op.execute(sample_products, "brand>amazon")

    def test_nonexistent_field(self, sample_products):
        op = WhereOperation()
        with pytest.raises(ValueError, match="не существует"):
            op.execute(sample_products, "weight=100")


class TestAggregateOperation:
    def test_min_price(self, sample_products):
        op = AggregateOperation()
        result = op.execute(sample_products, "price=min")
        assert len(result) == 1
        assert result[0].name == "redmi note 12"
        assert result[0].price == 199

    def test_max_rating(self, sample_products):
        op = AggregateOperation()
        result = op.execute(sample_products, "rating=max")
        assert len(result) == 1
        assert result[0].name == "iphone 15 pro"
        assert result[0].rating == 4.9

    def test_avg_price(self, sample_products, capsys):
        op = AggregateOperation()
        result = op.execute(sample_products, "price=avg")

        captured = capsys.readouterr()
        assert "avg" in captured.out
        assert "799" in captured.out  # (999 + 1199 + 199 + 799) / 4 = 799.0

        assert len(result) == 1
        assert result[0].name == "iphone 14"

    def test_avg_rating(self, sample_products, capsys):
        op = AggregateOperation()
        result = op.execute(sample_products, "rating=avg")

        captured = capsys.readouterr()
        assert "avg" in captured.out
        assert "4.75" in captured.out  # (4.9 + 4.8 + 4.6 + 4.7) / 4

        assert len(result) == 1
        assert result[0].name in ["galaxy s23 ultra", "iphone 14"]

    def test_invalid_aggregation_field(self, sample_products):
        op = AggregateOperation()
        with pytest.raises(ValueError, match="нечисловой тип"):
            op.execute(sample_products, "name=min")
