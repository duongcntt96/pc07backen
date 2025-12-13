import os
import multiprocessing

# Gunicorn configuration for production deployment on Render.

# Bind to all interfaces and the port provided by Render.
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"

# Number of Gunicorn workers. Defaults to WEB_CONCURRENCY if set by Render,
# otherwise, it's calculated based on CPU cores.
# A common formula is (2 * CPU) + 1.
workers = int(os.environ.get("WEB_CONCURRENCY", (multiprocessing.cpu_count() * 2) + 1))

# Worker class: 'sync' is suitable for most Django applications.
worker_class = "sync"

# Logging: Log access and errors to stdout/stderr, which Render captures.
accesslog = "-" # Log to stdout
errorlog = "-"  # Log to stderr
loglevel = "info"

# Timeout for workers. Adjust if you have long-running requests.
timeout = 120

# Daemonize the Gunicorn process: False, as Render manages the process.
daemon = False

# Allow forwarded IP addresses (e.g., from Render's load balancer).
forwarded_allow_ips = "*"

# Preload application: Set to True to load the application code before forking workers.
# Can save memory but may cause issues with certain libraries; start with False.
preload_app = False

# Max requests per worker: Restart workers after a certain number of requests
# to prevent potential memory leaks.
max_requests = 1000
max_requests_jitter = 50
