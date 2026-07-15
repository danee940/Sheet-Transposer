"""Gunicorn configuration exposing server lifecycle events in the logs."""
# pylint: disable=invalid-name,missing-function-docstring

import os

bind = f"0.0.0.0:{os.environ.get('PORT', '8080')}"
workers = int(os.environ.get("GUNICORN_WORKERS", "2"))
threads = int(os.environ.get("GUNICORN_THREADS", "4"))
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "150"))
worker_class = "gthread"

accesslog = "-"
errorlog = "-"
loglevel = os.environ.get("GUNICORN_LOG_LEVEL", "info")


def on_starting(server):
    server.log.info(
        "gunicorn master starting: bind=%s workers=%s timeout=%ss", bind, workers, timeout
    )


def when_ready(server):
    server.log.info("gunicorn ready and accepting connections on %s", bind)


def worker_int(worker):
    worker.log.warning("worker %s received SIGINT/SIGQUIT, shutting down", worker.pid)


def worker_abort(worker):
    worker.log.error("worker %s aborted (likely request timeout after %ss)", worker.pid, timeout)


def worker_exit(server, worker):
    server.log.info("worker %s exited", worker.pid)


def on_exit(server):
    server.log.warning("gunicorn master shutting down; container is stopping")
