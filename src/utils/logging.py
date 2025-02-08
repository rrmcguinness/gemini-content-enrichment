# Copyright 2025 Google, LLC
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os
from pythonjsonlogger.json import JsonFormatter

from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_INSTANCE_ID, SERVICE_NAME, Resource
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

import grpc
import google.auth
import google.auth.transport.grpc
import google.auth.transport.requests
from google.auth.transport.grpc import AuthMetadataPlugin


TRACE_PROVIDER: TracerProvider = None
SPAN_PROCESSOR: BatchSpanProcessor = None
METER_PROVIDER: MeterProvider = None


def setup_logging():
    LoggingInstrumentor().instrument()

    logHandler = logging.StreamHandler()
    formatter = JsonFormatter(
        "%(asctime)s %(levelname)s %(message)s %(otelTraceID)s %(otelSpanID)s %(otelTraceSampled)s",
        rename_fields={
            "levelname": "severity",
            "asctime": "timestamp",
            "otelTraceID": "logging.googleapis.com/trace",
            "otelSpanID": "logging.googleapis.com/spanId",
            "otelTraceSampled": "logging.googleapis.com/trace_sampled",
            },
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )
    logHandler.setFormatter(formatter)
    logging.basicConfig(
        level=logging.INFO,
        handlers=[logHandler],
    )
    


def setup_tracer():
    credentials, project_id = google.auth.default()
    logging.info(f"Project Name: {project_id}")
    
    request = google.auth.transport.requests.Request()
    
    resource = Resource.create(attributes={
        SERVICE_NAME: "gemini-enrichment",
        SERVICE_INSTANCE_ID: f"worker-{os.getpid()}",
    })
    
    auth_metadata_plugin = AuthMetadataPlugin(
        credentials=credentials, request=request
    )
    channel_creds = grpc.composite_channel_credentials(
        grpc.ssl_channel_credentials(),
        grpc.metadata_call_credentials(auth_metadata_plugin),
    )
    
    TRACE_PROVIDER = TracerProvider(shutdown_on_exit=True)
    SPAN_PROCESSOR = BatchSpanProcessor(OTLPSpanExporter(credentials=channel_creds))
    TRACE_PROVIDER.add_span_processor(SPAN_PROCESSOR)
    trace.set_tracer_provider(TRACE_PROVIDER)
    
    reader = PeriodicExportingMetricReader(
        OTLPMetricExporter()
    )
    METER_PROVIDER = MeterProvider(metric_readers=[reader], resource=resource)
    metrics.set_meter_provider(METER_PROVIDER)
