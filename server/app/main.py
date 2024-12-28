import datetime
import json
import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from logger import get_logger
from logger.unified_tracer import initialize_tracer
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from routers.chitchat import router as chat_router

load_dotenv()
# Create logger instance for this module
logger = get_logger(__name__)

# Initialize the unified tracer at application startup
initialize_tracer(
    service_name="hray-service",
    environment="development",
    jaeger_endpoint=f"http://{os.getenv('JAEGER_HOST', '127.0.0.1')}:4318/v1/traces",
    phoenix_endpoint=f"http://{os.getenv('PHOENIX_HOST', '127.0.0.1')}:6006/v1/traces"
)

# Create FastAPI app and instrument it
app = FastAPI()
FastAPIInstrumentor.instrument_app(app)

# Add a more comprehensive test endpoint
@app.get("/test-trace")
async def test_trace():
    try:
        from app.logger.jaeger_tracer import get_tracer
        tracer = get_tracer(__name__)
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

app.include_router(chat_router)

logger.info("FastAPI instrumentation completed")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
