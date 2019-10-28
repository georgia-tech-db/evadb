from abc import ABCMeta


class CustomUDF(ABCMeta):

    def process(self, data):
        new_df = None
        # custom filter code for this UDF
        return new_df
