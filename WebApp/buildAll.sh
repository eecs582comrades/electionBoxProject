#!/bin/bash

./scripts/setup.sh
npm install
echo "create database `electonbox`" | mysql -u root -p
node ./scripts/load-database.js
