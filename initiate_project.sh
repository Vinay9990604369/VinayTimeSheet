#!/bin/bash
set -e

# Create virtual environment if it doesn't exist
if [ ! -d "env" ]; then
  echo "Virtual environment not found. Creating one now..."
  python3 -m venv env
  echo "Virtual environment created."
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source env/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install/update dependencies from requirements.txt (without torch)
echo "Installing/updating requirements..."
pip install -r requirements.txt

# Install PyTorch CPU version separately using official wheels URL
echo "Installing PyTorch CPU version..."
pip install torch==2.7.0+cpu -f https://download.pytorch.org/whl/torch_stable.html

# Apply Django migrations
echo "Applying database migrations..."
python3 manage.py migrate

# Collect static files (optional)
echo "Collecting static files..."
python3 manage.py collectstatic --noinput

# Optionally start server (default yes)
START_SERVER=${1:-yes}
if [ "$START_SERVER" = "yes" ]; then
  echo "Starting development server..."
  python3 manage.py runserver
else
  echo "Setup done. Development server not started."
fi
