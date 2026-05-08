import os
from dotenv import load_dotenv
from app import create_app

# Load environment variables from .env file
load_dotenv()

# Determine config environment (default to development)
config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    # Run on port 5001
    debug = config_name == 'development'
    app.run(debug=debug, host='0.0.0.0', port=5001)
