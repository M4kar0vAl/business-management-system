#!/bin/bash

# Apply migrations
alembic upgrade head || exit 1

exec "$@"
