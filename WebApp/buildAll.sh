#!/bin/bash

./scripts/setup.sh
npm install
CREATE DATABASE electionbox;
node ./scripts/load-database.js
