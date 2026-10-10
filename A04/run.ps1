# Create virtual environment
python -m venv venv

# Activate your virtual environment
.\venv\Scripts\Activate.ps1

# Install the required packages
pip install flask openai python-dotenv gunicorn

# Run the app
python app.py