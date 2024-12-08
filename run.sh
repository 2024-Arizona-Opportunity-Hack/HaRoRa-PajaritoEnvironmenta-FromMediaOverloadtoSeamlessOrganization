#!/bin/bash

source .release.env
cd frontend/web_app_2
rm -rf dist
npm i
npm run build
cp -r dist/* ../../nginx/release/html/*
cd ../../
docker-compose -f docker-compose.yml -f docker-compose.release.yml up -d
