#!/bin/bash

./scripts/setup.sh
npm install
node ./scripts/load-database.js
