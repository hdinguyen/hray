from typing import Optional

from openinference.instrumentation.dspy import DSPyInstrumentor
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import \
    OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (BatchSpanProcessor,
                                            SimpleSpanProcessor)

from .log import get_logger

logger = get_logger(__name__)

class UnifiedTracerConfig:
    """Configuration for unified OpenTelemetry tracer supporting both Jaeger and Phoenix"""
    def __init__(
        self,
        service_name: str,
        environment: str = "development",
        jaeger_endpoint: str = "http://localhost:4318/v1/traces",
        phoenix_endpoint: str = "http://127.0.0.1:6006/v1/traces",
        enable_console_export: bool = True
    ):
        self.service_name = service_name
        self.environment = environment
        self.jaeger_endpoint = jaeger_endpoint
        self.phoenix_endpoint = phoenix_endpoint
        self.enable_console_export = enable_console_export
        self.tracer_provider: Optional[TracerProvider] = None

    def setup_tracer(self) -> None:
        """Initialize and configure the unified tracer"""
        try:
            logger.info("Setting up unified tracer...")

            # Create resource
            resource = Resource.create({
                "service.name": self.service_name,
                "deployment.environment": self.environment
            })

            # Initialize tracer provider
            self.tracer_provider = TracerProvider(resource=resource)
            trace.set_tracer_provider(self.tracer_provider)

            # Configure Jaeger exporter
            jaeger_exporter = OTLPSpanExporter(
                endpoint=self.jaeger_endpoint,
                headers={"Content-Type": "application/x-protobuf"},
                timeout=30,
            )

            # Configure Phoenix exporter
            phoenix_exporter = OTLPSpanExporter(
                endpoint=self.phoenix_endpoint,
                timeout=30,
            )

            # Add processors for both exporters
            self.tracer_provider.add_span_processor(
                BatchSpanProcessor(
                    jaeger_exporter,
                    max_queue_size=512,
                    max_export_batch_size=64,
                    schedule_delay_millis=1000,
                )
            )

            self.tracer_provider.add_span_processor(
                SimpleSpanProcessor(phoenix_exporter)
            )

            # Initialize DSPy instrumentation for Phoenix
            DSPyInstrumentor().instrument()

            logger.info("Unified tracer setup completed successfully")

        except Exception as e:
            logger.error(f"Failed to configure unified tracer: {e}", exc_info=True)
            raise

# Create default tracer configuration
default_tracer_config = UnifiedTracerConfig(service_name="hray-service")

def initialize_tracer(
    service_name: Optional[str] = None,
    environment: Optional[str] = None,
    jaeger_endpoint: Optional[str] = None,
    phoenix_endpoint: Optional[str] = None,
    enable_console_export: Optional[bool] = None
) -> None:
    """
    Initialize the global unified tracer with the specified configuration.

    Args:
        service_name: Name of the service
        environment: Deployment environment
        jaeger_endpoint: Endpoint for Jaeger OTLP exporter
        phoenix_endpoint: Endpoint for Phoenix OTLP exporter
        enable_console_export: Whether to enable console export
    """
    if service_name:
        default_tracer_config.service_name = service_name
    if environment:
        default_tracer_config.environment = environment
    if jaeger_endpoint:
        default_tracer_config.jaeger_endpoint = jaeger_endpoint
    if phoenix_endpoint:
        default_tracer_config.phoenix_endpoint = phoenix_endpoint
    if enable_console_export is not None:
        default_tracer_config.enable_console_export = enable_console_export

    default_tracer_config.setup_tracer()

def get_tracer(name: str) -> trace.Tracer:
    """
    Get a tracer instance for the specified name.

    Args:
        name: The name of the tracer (usually __name__ of the calling module)

    Returns:
        trace.Tracer: Configured tracer instance
    """
    return trace.get_tracer(name)
