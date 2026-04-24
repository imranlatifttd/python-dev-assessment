from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# initializing without the app, init_app() will be called later in the factory
limiter = Limiter(key_func=get_remote_address, strategy="fixed-window")
