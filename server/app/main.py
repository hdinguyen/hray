import datetime
import json
import logging

import uvicorn
from fastapi import FastAPI
# OpenTelemetry instrumentation
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import \
    OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (BatchSpanProcessor,
                                            ConsoleSpanExporter)
from routers.chitchat.amk_badminton import router as amk_badminton_router

# Add more detailed logging for troubleshooting
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s [%(name)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Configure tracer with detailed logging
try:
    logger.info("Setting up tracer...")
    resource = Resource.create({
        "service.name": "amk-badminton-service",
        "deployment.environment": "development"
    })
    tracer = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer)

    # Configure OTLP exporter with explicit HTTP protocol
    otlp_exporter = OTLPSpanExporter(
        endpoint="http://localhost:4318/v1/traces",
        headers={
            "Content-Type": "application/x-protobuf"
        },
        timeout=30,
    )

    # Create processor with more aggressive settings
    processor = BatchSpanProcessor(
        otlp_exporter,
        max_queue_size=512,
        max_export_batch_size=64,  # Smaller batch size for testing
        schedule_delay_millis=1000,  # More frequent exports
    )
    tracer.add_span_processor(processor)

    # Add console exporter with immediate export
    debug_processor = BatchSpanProcessor(
        ConsoleSpanExporter(),
        max_queue_size=512,
        schedule_delay_millis=100,  # Very quick console output
    )
    tracer.add_span_processor(debug_processor)

    logger.info("Tracer setup completed successfully")

    # Test the configuration immediately
    with trace.get_tracer(__name__).start_as_current_span("startup-test") as span:
        span.set_attribute("startup.test", "true")
        span.set_attribute("timestamp", str(datetime.datetime.now()))
        logger.info("Created startup test span")

except Exception as e:
    logger.error(f"Failed to configure tracer: {e}", exc_info=True)

# Create FastAPI app and instrument it
app = FastAPI()
FastAPIInstrumentor.instrument_app(app)

# Add a more comprehensive test endpoint
@app.get("/test-trace")
async def test_trace():
    try:
        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span("test-operation") as span:
            # Add multiple attributes for better visibility
            current_time = datetime.datetime.now()
            span.set_attribute("test.attribute", "test-value")
            span.set_attribute("test.timestamp", str(current_time))
            span.set_attribute("test.type", "manual-test")

            # Add an event to the span
            span.add_event(
                name="test.event",
                attributes={"event.type": "test", "timestamp": str(current_time)}
            )

            logger.info(f"Test span created at {current_time}")
            return {
                "message": "Test trace created",
                "timestamp": str(current_time),
                "status": "success"
            }
    except Exception as e:
        logger.error(f"Error creating test span: {e}", exc_info=True)
        return {"error": str(e)}, 500

# Add health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": str(datetime.datetime.now())}

app.include_router(amk_badminton_router)

# After tracer setup
logger.info("OpenTelemetry tracer configured")

# After instrumenting FastAPI
FastAPIInstrumentor.instrument_app(app)
logger.info("FastAPI instrumentation completed")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
