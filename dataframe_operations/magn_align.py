import pandas as pd


class magnAlign:

    def set_manual_align(self,
                         column_name,
                         pd_dataframe,
                         offset):

        pd_dataframe[column_name] = pd_dataframe[column_name] + offset

        return pd_dataframe[column_name]
