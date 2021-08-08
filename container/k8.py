"""
Title: k8.py

Created on: 8/7/2021

Author: FriscianViales

Encoding: utf-8

Description: Trigger a python script remotely.
"""

import luigi
from kubernetes import config
from kubernetes.client.api import core_v1_api
from kubernetes.stream import stream


# File configs:
config.load_kube_config()


class TriggerScriptRemotelyOnGKE(luigi.ExternalTask):
    """ Do something. """
    def output(self):
        return luigi.LocalTarget(f"{self.get_task_family()}.txt")

    def run(self):
        response = self.exec_cmd()
        print(response)

    def list_pods(self):
        return [x.metadata.name for x in self.client().list_namespaced_pod(namespace='default').items]

    def get_pod(self, pod_name: str):
        return self.client().read_namespaced_pod(
            name=pod_name,
            namespace='default'
        )

    def get_scheduler_pod_name(self):
        pod_name = [
            x for x in self.list_pods()
            if x.split('-')[0] == 'luigi' and x.split('-')[1] == 'scheduler'
        ]
        return pod_name[0]

    def exec_cmd(self):
        cmd = [
            '/bin/sh',
            '-c',
            'python3 main.py'
        ]

        return stream(
            self.client().connect_get_namespaced_pod_exec,
            self.get_scheduler_pod_name(),
            'default',
            command=cmd,
            stderr=True,
            stdin=False,
            stdout=True,
            tty=False
        )

    @staticmethod
    def client() -> core_v1_api.CoreV1Api:
        return core_v1_api.CoreV1Api()


if __name__ == '__main__':
    luigi.build(tasks=[TriggerScriptRemotelyOnGKE()], local_scheduler=True)
