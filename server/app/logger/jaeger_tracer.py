import datetime
from typing import Optional

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import \
    OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (BatchSpanProcessor,
                                            ConsoleSpanExporter)

from .log import get_logger

logger = get_logger(__name__)

class TracerConfig:
    """Configuration for OpenTelemetry tracer"""
    def __init__(
        self,
        service_name: str,
        environment: str = "development",
        otlp_endpoint: str = "http://localhost:4318/v1/traces",
        enable_console_export: bool = True
    ):
        self.service_name = service_name
        self.environment = environment
        self.otlp_endpoint = otlp_endpoint
        self.enable_console_export = enable_console_export
        self.tracer_provider: Optional[TracerProvider] = None

    def setup_tracer(self) -> None:
        """Initialize and configure the tracer"""
        try:
            logger.info("Setting up tracer...")

            # Create resource
            resource = Resource.create({
                "service.name": self.service_name,
                "deployment.environment": self.environment
            })

            # Initialize tracer provider
            self.tracer_provider = TracerProvider(resource=resource)
            trace.set_tracer_provider(self.tracer_provider)

            # Configure OTLP exporter
            otlp_exporter = OTLPSpanExporter(
                endpoint=self.otlp_endpoint,
                headers={"Content-Type": "application/x-protobuf"},
                timeout=30,
            )

            # Create and add OTLP processor
            otlp_processor = BatchSpanProcessor(
                otlp_exporter,
                max_queue_size=512,
                max_export_batch_size=64,
                schedule_delay_millis=1000,
            )
            self.tracer_provider.add_span_processor(otlp_processor)

            # Add console exporter if enabled
            if self.enable_console_export:
                console_processor = BatchSpanProcessor(
                    ConsoleSpanExporter(),
                    max_queue_size=512,
                    schedule_delay_millis=100,
                )
                self.tracer_provider.add_span_processor(console_processor)

            logger.info("Tracer setup completed successfully")


        except Exception as e:
            logger.error(f"Failed to configure tracer: {e}", exc_info=True)
            raise

def get_tracer(name: str) -> trace.Tracer:
    """
    Get a tracer instance for the specified name.

    Args:
        name: The name of the tracer (usually __name__ of the calling module)

    Returns:
        trace.Tracer: Configured tracer instance
    """
    return trace.get_tracer(name)

# Create default tracer configuration
default_tracer_config = TracerConfig(service_name="hray-service")

def initialize_tracer(
    service_name: Optional[str] = None,
    environment: Optional[str] = None,
    otlp_endpoint: Optional[str] = None,
    enable_console_export: Optional[bool] = None
) -> None:
    """
    Initialize the global tracer with the specified configuration.

    Args:
        service_name: Name of the service
        environment: Deployment environment
        otlp_endpoint: Endpoint for OTLP exporter
        enable_console_export: Whether to enable console export
    """
    if service_name:
        default_tracer_config.service_name = service_name
    if environment:
        default_tracer_config.environment = environment
    if otlp_endpoint:
        default_tracer_config.otlp_endpoint = otlp_endpoint
    if enable_console_export is not None:
        default_tracer_config.enable_console_export = enable_console_export

    default_tracer_config.setup_tracer()
