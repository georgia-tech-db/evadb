from sqlalchemy import Column, String, Integer, Float, UniqueConstraint, \
    ForeignKey
from sqlalchemy.orm import relationship

from src.catalog.models.base_model import BaseModel


class UdfMetrics(BaseModel):
    __tablename__ = 'udf_metrics'

    _name = Column('name', String(100))
    _dataset = Column('dataset', String(100))
    _category = Column('category', String(100))
    _precision = Column('precision', Float)
    _recall = Column('recall', Float)
    _udf_id = Column('udf_id', Integer,
                     ForeignKey('udf.id'))
    _udf = relationship('UdfMetadata', back_populates='_metrics')

    __table_args__ = (
        UniqueConstraint('name', 'dataset', 'category'), {}
    )

    def __init__(self,
                 name, str,
                 dataset: str,
                 category: str,
                 precision: float,
                 recall: float,
                 udf_id: int = None):
        self._name = name
        self._dataset = dataset
        self._category = category
        self._precision = precision
        self._recall = recall
        self._udf_io = udf_id

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

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

    @property
    def udf_id(self):
        return self._udf_id

    @udf_id.setter
    def udf_id(self, value):
        return self._udf_id

    def __str__(self):
        udf_metrics_str = 'UDF metrics: ({}, {}, {}, {}, {})\n'.format(
            self.name, self.dataset, self.category, self.precision,
            self.recall)
        return udf_metrics_str

    def __eq__(self, other):
        return self.id == other.id and \
            self.name == other.name and \
            self.dataset == other.dataset and \
            self.category == other.category and \
            self.precision == other.precision and \
            self.recall == other.recall
