import logging
import sys
import os 
from datetime import datetime, timezone

class _JsonishFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        base = {
            "ts": ts,
            "lvl": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        # Attach extras if provided (e.g., run_id, table)
        for k, v in getattr(record, "__dict__", {}).items():
            if k not in ("args", "msg", "levelname", "levelno", "name"):
                # keep a small whitelist of custom keys
                if k in ("run_id", "table", "job", "path"):
                    base[k] = v
        return " ".join(f'{k}="{str(v).replace("\"","\'")} for k, v in base.items())

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:  # avoid duplicate handlers in notebooks/REPL
        return logger
    logger.setLevel(logging.INFO)
# --- KEEP YOUR EXISTING CONSOLE HANDLER ---
    # This handler prints your JSON-style logs to the terminal.
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(_JsonishFormatter())
    logger.addHandler(console_handler)

    # --- ADDED: Code to set up file logging ---
    # 1. Define the absolute path to the logs directory
    log_directory = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        '..',
        '..',
        'MKM_Data_Validation_and_cleaning',
        'logs'
    ))
    os.makedirs(log_directory, exist_ok=True)

    # 2. Create a unique, timestamped log file name for each run
    log_file_name = f"pipeline_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_file_path = os.path.join(log_directory, log_file_name)

    # 3. Create a file handler to write logs to this new file
    file_handler = logging.FileHandler(log_file_path)
    # We'll use your same custom formatter for consistency in the log file
    file_handler.setFormatter(_JsonishFormatter())
    logger.addHandler(file_handler)
    # --- END of added code ---

    logger.propagate = False
    return logger


