
from llm.tool.search_tool import SearchResult
from openinference.instrumentation.dspy import DSPyInstrumentor
from opentelemetry import trace as trace_api
from opentelemetry.exporter.otlp.proto.http.trace_exporter import \
    OTLPSpanExporter
from opentelemetry.sdk import trace as trace_sdk
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from phoenix.otel import register


def setup_tracer():
    tracer_provider = register(
        project_name="my-llm-app", # Default is 'default'
        endpoint="http://127.0.0.1:6006/v1/traces",
    )

    resource = Resource.create({
                    "service.name": "hray_llm",
                    "deployment.environment": "development"
                })


    endpoint = "http://127.0.0.1:6006/v1/traces"
    tracer_provider = trace_sdk.TracerProvider(resource=resource)
    trace_api.set_tracer_provider(tracer_provider)
    tracer_provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter(endpoint)))

    DSPyInstrumentor().instrument()
