# Name of code artifact: All of them
# Description: Script for setting up the local database after installing required packages from npm on Windows
# Name(s): William Johnson
# Date Created: 10-25-24
# Dates Revised:
# Brief description of each revision & author:

# Check if Chocolatey is installed and install it if necessary
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Output "Chocolatey not found. Installing Chocolatey..."
    Set-ExecutionPolicy Bypass -Scope Process -Force;
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072;
    iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'));
} else {
    Write-Output "Chocolatey is already installed."
}

# Install MySQL via Chocolatey
Write-Output "Installing MySQL..."
choco install mysql -y

# Start MySQL service
Write-Output "Starting MySQL service..."
Start-Service -Name MySQL

# Wait for MySQL to start (optional, adjust the sleep time if necessary)
Start-Sleep -Seconds 10

# Connect to MySQL, create the database, and use it
$mysqlPassword = ""
$createDbCommand = "CREATE DATABASE IF NOT EXISTS dontkillplants; USE dontkillplants;"
Write-Output "Creating database dontkillplants..."

# Run MySQL command to create the database
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p$mysqlPassword -e $createDbCommand

# Run setup and build scripts
Write-Output "Running npm setup and build scripts..."
npm run setup:win

Write-Output "Setup completed successfully!"
