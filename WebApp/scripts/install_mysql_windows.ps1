# Name of code artifact: All of them
# Description: Script for installing MySQL conveniently on Windows
# Name(s): William Johnson
# Date Created: 10-25-24
# Dates Revised:
# Brief description of each revision & author:

# Check if MySQL is installed, if not install it via Chocolatey
Write-Host "Checking MySQL status..."
if (-Not (Get-Command mysql -ErrorAction SilentlyContinue)) {
    Write-Host "MySQL not found. Installing..."
    choco install mysql -y
    Start-Service mysql
} else {
    Write-Host "MySQL is already installed."
}
