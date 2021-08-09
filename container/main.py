"""
Title: db_replication.py

Created on: 2021-07-28

Author: FriscianViales

Encoding: UTF-8

Description: Luigi replication job.
"""

# Import libraries:
import logging
import luigi
import sqlite3
import os
import pandas as pd
import pandas_gbq as pdgbq
from datetime import datetime

# File configurations:
NOW = datetime.now().strftime('%Y%m%d-%H00')
DB_LOC = '/var/lib/gce-drive/luigi-task-hist.db'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'analytics-and-insights-luigi-pipelines.json'
logging.basicConfig(
    level='INFO',
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p'
)


class LuigiSchedulerReplicateDatabaseToBigQuery(luigi.ExternalTask):
    """ Connect to the internal scheduler database and replicate all tables over to BigQuery. """
    def output(self):
        return luigi.LocalTarget(f"Checkpoints/{self.get_task_family()}-{NOW}.txt")

    def run(self):
        logging.info(f"Replicating Luigi Scheduler Databse...")
        for table in ['tasks', 'task_parameters', 'task_events']:
            cursor = self.db_cursor()
            results = cursor.execute(f"SELECT * FROM {table}")
            cols = [description[0] for description in results.description]
            rows = [row for row in results]
            df = pd.DataFrame(data=rows, columns=cols)
            pdgbq.to_gbq(dataframe=df, destination_table=f"LuigiSchedulerDatabase.{table}", if_exists='replace')

        with self.output().open('w') as checkpoint:
            checkpoint.write('SUCCESS')

    @staticmethod
    def db_cursor():
        with sqlite3.connect(DB_LOC) as conn:
            return conn.cursor()


if __name__ == '__main__':
    luigi.build([LuigiSchedulerReplicateDatabaseToBigQuery()], local_scheduler=True)
