#!/bin/bash
set -e

if [ "$1" = 'flask' ]; then
    echo "=== Initializing Database ==="
    python -c "
from app import create_app, extensions, models
app = create_app()
app.app_context().push()
models.base.Base.metadata.create_all(bind=extensions.engine)
"
    echo "=== Database Initialization Complete ==="
else
    echo "=== Skipping Database Init for Worker ==="
fi

# Execute the main container command (passed from docker-compose)
exec "$@"