#!/bin/bash

# Apply migrations
alembic upgrade head

exec "$@"
