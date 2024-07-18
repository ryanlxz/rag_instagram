import logging
import logging.config
import yaml
from pathlib import Path

log_path = Path("./logs/log_files")
log_path.mkdir(parents=True, exist_ok=True)

with open("./logs/logging_conf.yml", "r") as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

logger = logging.getLogger("Rag_Instagram")
