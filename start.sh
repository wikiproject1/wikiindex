#!/bin/bash
cd app
npm install
npm run build
npm run preview -- --host 0.0.0.0 --port 8000
