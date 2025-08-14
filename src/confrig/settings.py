"""
Confrigration management of the AAutonoumous knowledge worker Agent.
Handles environment variables, validation, and provides typed configuration objects.

"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Setting:
    """
    Setting class for autonomus agents

    """
    def __init__(self):
        self.openai_api_key=os.getenv("OPENAI_API_KEY")
        self.antropic_api_key=os.getenv("ANTHROPIC_API_KEY")

        self.default_model=os.getenv("DEFAULT_MODEL","gpt-4o-mini")
        self.backup_model= os.getenv("BACKUP_MODEL","gpt-3.5-turbo")

        self.max_token = os.getenv("MAX-TOKEN","2000")
        self.temperature=os.getenv("TEMPERATURE","0.1")

        self.project_name = os.getenv("PROJECT_NAME", "Autonomous Knowledge Agent")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO")

        self.data_dir = Path(os.getenv("DATA_DIR", "./data"))
        self.docs_dir = Path(os.getenv("DOCS_DIR", "./data/documents"))
        self.vector_store_dir = Path(os.getenv("VECTOR_STORE_DIR", "./data/vector_store"))
        self.output_dir = Path(os.getenv("OUTPUT_DIR", "./data/outputs"))

        self.vector_db_name = os.getenv("VECTOR_DB_NAME", "agent_knowledge")
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

        self.create_directories()
        self.validate()
    
    def create_directories(self):
        """
        CREATE THE NECESSARY DIRECTORIES IF NOT EXIST

        """
        directories=[
            self.data_dir,
            self.docs_dir,
            self.vector_store_dir,
            self.output_dir,
            self.output_dir / "reports",
            self.output_dir / "analysis",
            ]
        for directory in directories:
            directory.mkdir(parents=True,exist_ok=True)

    def validate(self):
        """
        Validate the required settings

        """
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required. Please provide or set it in the .env file")
        
        print(f"✅ Settings loaded for: {self.project_name}")
        print(f"📁 Data directory: {self.data_dir}")
        print(f"🤖 Default model: {self.default_model}")

    
    def get_model_confrig(self):
        """
        GET MODEL CONFRIGURATION FOR AUTOGEN

        """
        return{
            "model": self.default_model,
            "api_key": self.openai_api_key,
            "max_tokens": self.max_token,
            "temperature": self.temperature,
            }
    
settings=Setting()





