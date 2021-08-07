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
NOW = datetime.now().strftime("%Y%m%d")
DB_LOC = '/var/lib/gce-drive/luigi-task-hist.db'
TMP_PATH = '/var/lib/gce-drive/db-replication-checkpoints'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'analytics-and-insights-luigi-pipelines.json'
logging.basicConfig(
    level='INFO',
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p'
)


class ReplicateLuigiSchedulerDatabase(luigi.ExternalTask):
    """ Connect to the internal scheduler database and replicate all tables over to BigQuery. """
    def output(self):
        return luigi.LocalTarget(f"{TMP_PATH}/{self.get_task_family()}-{NOW}.txt")

    def run(self):
        self.list_tables()
        for table in ['tasks', 'task_parameters', 'task_events']:
            cursor = self.db_cursor()
            results = cursor.execute(f"SELECT * FROM {table}")
            cols = [description[0] for description in results.description]
            rows = [row for row in results]
            df = pd.DataFrame(data=rows, columns=cols)
            pdgbq.to_gbq(dataframe=df, destination_table=f"LuigiSchedulerDatabase.{table}", if_exists='replace')

        with self.output().open('w') as checkpoint:
            checkpoint.write('SUCCESS')

    def list_tables(self):
        cursor = self.db_cursor()
        results = cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table' ;")
        logging.info([row for row in results])

    @staticmethod
    def db_cursor():
        with sqlite3.connect(DB_LOC) as conn:
            return conn.cursor()


if __name__ == '__main__':
    luigi.build([ReplicateLuigiSchedulerDatabase()], local_scheduler=True)
