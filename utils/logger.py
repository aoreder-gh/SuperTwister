
import logging, os
def setup_logger(profile):
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        filename=f"logs/{profile}.log",
        level=logging.INFO,
        format="%(asctime)s %(message)s",
        force=True
    )
