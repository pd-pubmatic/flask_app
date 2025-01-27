import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Flask Config
    JSON_SORT_KEYS = False
    
    # Processing configs
    MAX_PARALLEL_PROCESSES = 3
    VIDEO_DOWNLOAD_TIMEOUT = 30  # seconds
    
    # AWS Settings
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')
    S3_BUCKET = 'snowflake-dev-analytics'
    S3_RESULTS_FOLDER = 'AdWise/test/results/'
    
    # OpenAI Settings
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OPENAI_TEMPERATURE = 0.7
    OPENAI_MAX_TOKENS = 10000
    
    # Callback Settings
    CALLBACK_TIMEOUT = int(os.getenv('CALLBACK_TIMEOUT', '30'))
    CALLBACK_RETRIES = int(os.getenv('CALLBACK_RETRIES', '3'))
    
    # Resource Paths
    RESOURCES_PATH = os.path.join('app', 'resources')
    TAG_MAPPING_FILE = 'tag_id_mapping.csv'
