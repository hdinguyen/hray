# from openinference.instrumentation.dspy import DSPyInstrumentor
# from opentelemetry import trace
# from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import \
#     OTLPSpanExporter
# from opentelemetry.sdk.resources import Resource
# from opentelemetry.sdk.trace import TracerProvider
# from opentelemetry.sdk.trace.export import BatchSpanProcessor


# def init_phoenix_tracer():
#     # Create a TracerProvider
#     resource = Resource.create({"service.name": "your-service-name"})
#     trace_provider = TracerProvider(resource=resource)

#     # Configure the OTLP exporter to send traces to Phoenix
#     otlp_exporter = OTLPSpanExporter(
#         endpoint="http://localhost:4317",  # Phoenix OTLP endpoint
#         insecure=True
#     )

#     # Add BatchSpanProcessor with OTLP exporter
#     trace_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

#     # Set the TracerProvider
#     trace.set_tracer_provider(trace_provider)

#     # Initialize DSPy instrumentation
#     DSPyInstrumentor().instrument()

#     return trace.get_tracer(__name__)
import os

from dotenv import load_dotenv

load_dotenv()

from openinference.instrumentation.dspy import DSPyInstrumentor
from openinference.instrumentation.litellm import LiteLLMInstrumentor

collector_endpoint = os.getenv("COLLECTOR_ENDPOINT", "localhost")


def instrument():
    # resource = Resource(attributes={})
    # tracer_provider = trace_sdk.TracerProvider(resource=resource)
    # span_exporter = OTLPSpanExporter(endpoint=collector_endpoint)
    # span_processor = SimpleSpanProcessor(span_exporter=span_exporter)
    # tracer_provider.add_span_processor(span_processor=span_processor)
    # trace_api.set_tracer_provider(tracer_provider=tracer_provider)
    # DSPyInstrumentor().instrument()
    from phoenix.otel import register

    tracer_provider = register(
        project_name="hray-dspy", # Default is 'default'
        endpoint="http://localhost:6006/v1/traces",
    )
    DSPyInstrumentor().instrument(tracer_provider=tracer_provider)
    LiteLLMInstrumentor().instrument(tracer_provider=tracer_provider)
