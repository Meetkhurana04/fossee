#!/usr/bin/env bash
set -o errexit

echo "=========================================="
echo "Step 1: Installing Python dependencies..."
echo "=========================================="
pip install -r requirements.txt

echo "=========================================="
echo "Step 2: Installing Node.js and npm..."
echo "=========================================="
# Install Node.js using nodeenv
pip install nodeenv
nodeenv -p --node=18.17.0

echo "=========================================="
echo "Step 3: Building React frontend..."
echo "=========================================="
# Go to frontend folder
cd ../frontend-web

# Install npm packages
npm install

# Build React app
npm run build

# Move build to backend/frontend folder
echo "Moving build files to backend..."
rm -rf ../backend/frontend
mkdir -p ../backend/frontend
cp -r build/* ../backend/frontend/

# Go back to backend
cd ../backend

echo "=========================================="
echo "Step 4: Collecting Django static files..."
echo "=========================================="
python manage.py collectstatic --no-input

echo "=========================================="
echo "Step 5: Running database migrations..."
echo "=========================================="
python manage.py migrate

echo "=========================================="
echo "Build completed successfully!"
echo "=========================================="