#!/bin/bash

docker build -t grocery-god:dev .

docker run --rm \
  -v "$PWD/data:/app/data" grocery-god:dev