from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address


limiter = Limiter(key_func=get_remote_address, 
                      default_limits=["1/2 seconds"], # глобальний, а індивідуальний/endpoint - @limiter.limit("5/minute") 
                      enabled=True)

def setup_rate_limiter(app): 
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)