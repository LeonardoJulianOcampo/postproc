import pandas as pd


class tempAlign:

    def set_manual_align(self, imu_name, pd_dataframe, offset):
        pd_dataframe['time_' + imu_name] = pd_dataframe['time_' + imu_name] + offset
        return pd_dataframe['time_' + imu_name]
