#!/bin/sh
set -eu

# Extract dependencies to local disk instead of importing over the content share.
runtime=$(mktemp -d /tmp/wanted-layout.XXXXXX)
tar -xzf /home/site/wwwroot/app.tar.gz -C "$runtime"
export PYTHONPATH="$runtime/.python_packages/lib/site-packages"
cd "$runtime"
exec python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 1 --no-access-log
