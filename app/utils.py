import csv
import os
import time
from typing import Iterable, Dict, List
import logging


logger = logging.getLogger(__name__)


def read_csv_as_dicts(file_path: str, delay: int) -> Iterable[Dict[str, str]]:
    """
    Read CSV file row by row and yield each row as a dictionary.
    Uses CSV header fields as keys.

    -> Memory efficient (streams rows instead of loading full file)
    -> Use inside Celery task while extracting

    Example output:
    {"name": "John", "role": "Dev", "loc": "NY", "extra": "..."}
    """

    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        time.sleep(delay)

        for row in reader:
            yield {
                k.strip(): v.strip() if isinstance(v, str) else v
                for k, v in row.items()
            }
        f.close()


def validate_csv_columns(file_path: str, required_cols: List[str]) -> bool:
    """
    Check if CSV contains required column headers.

    returns True if valid else False
    """

    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader)

        return all(col in headers for col in required_cols)


def is_csv(filename: str) -> bool:
    """Quick extension check"""
    return filename.lower().endswith(".csv")


def delete_file_safe(file_path: str):
    """
    Safely delete file if exists with error handling and logging.
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"🗑️ [CLEANUP] Deleted file: {file_path}")
        else:
            logger.warning(f"⚠️ [CLEANUP] File to delete not found: {file_path}")
    except Exception as e:
        logger.error(f"❌ [CLEANUP ERROR] Could not delete file: {e}")