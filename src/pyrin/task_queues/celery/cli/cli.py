# -*- coding: utf-8 -*-
"""
celery cli module.
"""

import pyrin.task_queues.celery.cli.services as celery_cli_services

from pyrin.cli.decorators import cli
from pyrin.core.structs import CLI


class CeleryCLI(CLI):
    """
    celery cli class.

    this class exposes all celery cli commands.
    """

    _execute_service = celery_cli_services.execute

    @cli
    def worker(self, concurrency=None, hostname=None, beat=False, queues=None,
               purge=False, autoscale=None, logfile=None, loglevel=None,
               pidfile=None, optimization=None, help=False):
        """
        create a worker node.

        :keyword int concurrency: number of child processes processing the queue.
                                  the default is the number of cpus available on
                                  your system.

        :keyword str hostname: set custom hostname for worker node.

        :keyword bool beat: also run the `celery beat` periodic task scheduler.
                            please note that there must only be one instance of
                            this service.

        :keyword str queues: list of queues to enable for this worker, separated by comma.
        :keyword bool purge: purges all waiting tasks before the daemon is started.

        :keyword str autoscale: enable autoscaling by providing
                                max_concurrency, min_concurrency.

        :keyword str logfile: path to log file. if no logfile is specified, `stderr` is used.

        :keyword str loglevel: logging level, choose between `DEBUG`, `INFO`, `WARNING`,
                               `ERROR`, `CRITICAL` or `FATAL`.

        :keyword str pidfile: optional file used to store the process pid.
                              the program won't start if this file already exists
                              and the pid is still alive.

        :keyword str optimization: optimization profile to be applied.
                                   it could be from: `default` and `fair`.

        :keyword bool help: show help for this command.
        """
        pass

    @cli
    def beat(self, logfile=None, loglevel=None, pidfile=None, help=False):
        """
        start the beat periodic task scheduler.

        :keyword str logfile: path to log file. if no logfile is specified, `stderr` is used.

        :keyword str loglevel: logging level, choose between `DEBUG`, `INFO`, `WARNING`,
                               `ERROR`, `CRITICAL` or `FATAL`.

        :keyword str pidfile: optional file used to store the process pid.
                              the program won't start if this file already exists
                              and the pid is still alive.

        :keyword bool help: show help for this command.
        """
        pass

    @cli
    def result(self, task_id, task=None, traceback=False, help=False):
        """
        gives the return value for a given task id.

        :param str task_id: id of the task.

        :keyword str task: name of the task (if custom backend).
        :keyword bool traceback: show traceback if any.
        :keyword bool help: show help for this command.
        """
        pass

    @cli
    def inspect(self, method, include_defaults=None, samples_count=None,
                object_type=None, count=None, max_depth=None, task_ids=None,
                attributes=None, destination=None, timeout=None, json=None,
                help=False):
        """
        inspect the worker at runtime.

        :param str method: inspect method. it could be from these methods:
                           `active`, `active_queues`, `clock`, `conf`, `memdump`,
                           `memsample`, `objgraph`, `ping`, `query_task`, `registered`,
                           `report`, `reserved`, `revoked`, `scheduled` and `stats`.

        :keyword bool include_defaults: this is only for `conf` method.
        :keyword int samples_count: this is only for `memdump` method.
        :keyword str object_type: this is only for `objgraph` method.
        :keyword int count: this is only for `objgraph` method.
        :keyword int max_depth: this is only for `objgraph` method.
        :keyword str | list[str] task_ids: list of task ids.
                                           this is only for `query_task` method.

        :keyword str | list[str] attributes: this is only for `registered` method.
        :keyword str | list[str] destination: comma separated destination node names.
        :keyword float timeout: timeout in seconds waiting for reply.
        :keyword bool json: use json as output format.
        :keyword bool help: show help for this command.
        """
        pass

    @cli
    def status(self, help=False):
        """
        show list of worker nodes that are online.

        :keyword bool help: show help for this command.
        """
        pass