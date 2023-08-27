import time
import datetime
from typing import Optional

def days(time_in_days: float) -> datetime.timedelta:
    """Create a timedelta duration in minutes."""
    return datetime.timedelta(days=time_in_days)


def years(time_in_years: float) -> datetime.timedelta:
    """Create a timedelta duration in median years--i.e., 365 days."""
    return days(365 * time_in_years)
