#!/bin/sh

# Wait for MinIO to start
until mc alias set myminio http://localhost:9000 minioadmin minioadmin; do
  echo "Waiting for MinIO to start..."
  sleep 1
done
# Create the bucket if it doesn't exist
mc mb myminio/ecommerce-data --ignore-existing

# Keep the container running
tail -f /dev/null