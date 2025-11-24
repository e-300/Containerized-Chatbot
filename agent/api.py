# LAYER 3 - API Layer
# Pydantic-> Validates Response message exists, is str and if not returns error prior to code exec
# Request -> validation -> processing -> response   

from fastapi import FastAPI, Response
from pydantic import BaseModel
from agent.claude import AnthropicAgent
import os
from dotenv import load_dotenv
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time

load_dotenv()


class ChatRequest(BaseModel):
    message: str


app = FastAPI()

api_key = os.getenv("ANTHROPIC_API_KEY")

if api_key is None:
    raise ValueError("ANTHROPIC_API_KEY environment variable is missing.")

#request counter
request_count = Counter(
    'agent_requests_total', 
    'Total number of chat requests',
    ['status'] 
)

#histogram
# Histogram: Tracks distribution of values (response times)
response_time = Histogram(
    'agent_response_seconds', 
    'Response time in seconds'
)


# Cache effectiveness metrics
cache_hits = Counter(
    'agent_cache_hits_total',
    'Total number of cache hits'
)

cache_misses = Counter(
    'agent_cache_misses_total', 
    'Total number of cache misses'
)

error_count = Counter(
    'agent_errors_total',
    'Total number of errors',
    ['error_type']
)

# loading redis vars from from environment variables
redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = int(os.getenv("REDIS_PORT", "6379"))

# Agent initialized with Redis config
agent = AnthropicAgent(
    api_key=api_key, 
    system_prompt=None,
    redis_host=redis_host,
    redis_port=redis_port
)


# Prometheus metrics endpoint
@app.get("/metrics")
async def metrics():
    """Expose metrics for Prometheus to scrape"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )



@app.post("/chat")
async def chat(req: ChatRequest):
    """Chat endpoint wrapped with Prometheus metrics"""
    
    start_time = time.time()
    
    try:
        # Process the request
        response = agent.process(req.message)
        
        # Track successful request
        request_count.labels(status='success').inc()
        
        # Check if response came from cache (simple heuristic)
        # You could enhance agent.process() to return this info
        if "error" in response.lower() or "api error" in response.lower():
            error_count.labels(error_type='api_error').inc()
            request_count.labels(status='error').inc()
        
        return {"response": response}
    
    except Exception as e:
        # Track failed request
        request_count.labels(status='error').inc()
        error_count.labels(error_type='exception').inc()
        
        return {"response": f"Error: {str(e)}"}
    
    finally:
        # Always track response time
        duration = time.time() - start_time
        response_time.observe(duration)





# @app.post("/chat")
# async def chat(req: ChatRequest):
    
#     response = agent.process(req.message)
    
#     return {"response": response}





@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}
