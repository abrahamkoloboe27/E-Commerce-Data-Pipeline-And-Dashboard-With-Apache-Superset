#!/bin/sh

# Wait for MinIO to start
until mc alias set myminio http://minio:9000 minioserver minioserver; do
  echo "Waiting for MinIO to start..."
  sleep 1
done

mc mb myminio/ecommerce-data --ignore-existing

tail -f /dev/null