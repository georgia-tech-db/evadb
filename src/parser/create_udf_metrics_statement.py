from src.parser.statement import AbstractStatement
from src.parser.types import StatementType


class CreateUDFMetricsStatement(AbstractStatement):
    def __init__(self,
                 udf_name: str,
                 dataset: str,
                 category: str,
                 precision: float,
                 recall: float):
        super().__init__(StatementType.CREATE_UDF_METRICS)
        self._udf_name = udf_name
        self._dataset = dataset
        self._category = category
        self._precision = precision
        self._recall = recall

    def __str__(self) -> str:
        print_str = 'CREATE UDF METRICS {} DATASET {} CATEGORY {} ' \
            'PRECISION {:.4f} RECALL {:.4f}'.format(
                self._udf_name, self._dataset, self._category,
                self._precision, self._recall)
        return print_str

    @property
    def udf_name(self):
        return self._udf_name

    @property
    def dataset(self):
        return self._dataset

    @property
    def category(self):
        return self._category

    @property
    def precision(self):
        return self._precision

    @property
    def recall(self):
        return self._recall

    def __eq__(self, other):
        if not isinstance(other, CreateUDFMetricsStatement):
            return False
        return (self.udf_name == other.udf_name and
                self.dataset == other.dataset and
                self.category == other.category and
                self.precision == other.precision and
                self.recall == other.recall)
