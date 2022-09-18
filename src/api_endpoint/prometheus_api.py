import logging
import mimetypes
import os
from marshmallow import fields, Schema
from marshmallow.validate import Range

# from prometheus_flask_exporter import PrometheusMetrics
# from prometheus_flask_exporter.multiprocess import GunicornPrometheusMetrics, MultiprocessPrometheusMetrics, MultiprocessInternalPrometheusMetrics
# from prometheus_client import CollectorRegistry, generate_latest, multiprocess, CONTENT_TYPE_LATEST

from src.const.global_map import RESOURCE_MAP
from src.api_endpoint.add_api import api_log
from src.utils.decorator import json_validate
from fastapi.responses import JSONResponse

# app = RESOURCE_MAP["flask_app"]
# os.environ["prometheus_multiproc_dir"]='/tmp'

# @app.route('/metrics')
# def metrics():
#     registry = CollectorRegistry()
#     multiprocess.MultiProcessCollector(registry)
#     data = generate_latest(registry)
#     response_headers = [
#         ('Content-type', CONTENT_TYPE_LATEST),
#         ('Content-Length', str(len(data)))
#     ]
#     return Response(response=data, status=200, headers=response_headers)

import prometheus_client
from prometheus_client.core import CollectorRegistry
from prometheus_client import Summary, Counter, Histogram, Gauge
import time

app = RESOURCE_MAP["fastapi_app"]

_INF = float("inf")

graphs = {}
graphs['c'] = Counter('python_request_operations_total', 'The total number of processed requests')
graphs['h'] = Histogram('python_request_duration_seconds', 'Histogram for the duration in seconds.', buckets=(1, 2, 5, 6, 10, _INF))


@app.route("/metrics")
async def requests_count():
    res = []
    for k,v in graphs.items():
        res.append(prometheus_client.generate_latest(v))
    return JSONResponse(content=res, mimetypes="text/plain")
