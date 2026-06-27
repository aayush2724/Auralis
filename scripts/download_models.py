import logging
from transformers import pipeline

# We only use langchain_huggingface or sentence-transformers indirectly, 
# but we can download it via HuggingFace transformers directly
from transformers import AutoModel, AutoTokenizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("download_models")

def download_models():
    logger.info("Downloading facebook/bart-large-mnli...")
    pipeline("zero-shot-classification", model="facebook/bart-large-mnli", device=-1)
    
    logger.info("Downloading distilbert-base-uncased-finetuned-sst-2-english...")
    pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english", device=-1)
    
    logger.info("Downloading sentence-transformers/all-MiniLM-L6-v2...")
    AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
    AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
    
    logger.info("All models downloaded successfully.")

if __name__ == "__main__":
    download_models()
