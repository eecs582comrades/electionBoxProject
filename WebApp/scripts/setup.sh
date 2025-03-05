#!/bin/bash

# Name of code artifact: All of them
# Description: Script for setting up the local database after installing required packages from npm on MacOS
# Name(s): William Johnson
# Date Created: 10-25-24
# Dates Revised:
# Brief description of each revision & author:


# Check for Homebrew and install if not found
if ! command -v brew &> /dev/null; then
    echo "Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "Homebrew is already installed."
fi

# Install MySQL
echo "Installing MySQL..."
brew install mysql

# Start MySQL service
echo "Starting MySQL service..."
brew services start mysql

# Wait a few seconds for MySQL to fully start
sleep 5

# Set MySQL root password and create database
MYSQL_ROOT_PASSWORD="" # Replace with your desired password

# Initialize MySQL (only required for first-time MySQL installations)
if [ ! -f ~/.mysql_initialized ]; then
    echo "Initializing MySQL with root password..."
    mysql -u root -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '$MYSQL_ROOT_PASSWORD';"
    touch ~/.mysql_initialized
fi

# Create the database
echo "Creating database electionbox..."
mysql -u root -p$MYSQL_ROOT_PASSWORD -e "CREATE DATABASE IF NOT EXISTS electionbox; USE electionbox;"

# Run setup and build scripts
echo "Running npm setup and build scripts..."
npm run setup:mac
npm run build

echo "Setup completed successfully!"
