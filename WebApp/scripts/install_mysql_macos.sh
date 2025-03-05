#!/bin/bash

# Name of code artifact: All of them
# Description: Script for installing MySQL conveniently on MacOS
# Name(s): William Johnson
# Date Created: 10-25-24
# Dates Revised:
# Brief description of each revision & author:


# Check if MySQL is installed, if not install it
if ! command -v mysql &> /dev/null
then
    echo "MySQL not found. Installing..."
    brew install mysql
    brew services start mysql
else
    echo "MySQL is already installed."
fi
