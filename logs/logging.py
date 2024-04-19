import logging
import logging.config
import yaml

with open("./logs/logging_conf.yml", "r") as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

logger = logging.getLogger("Rag_Instagram")
