import os

MERAKI_API_KEY = os.getenv("MERAKI_API_KEY")
MERAKI_BASE_URL = "https://api.meraki.com/api/v1/"

DEVICES_URL = f"{MERAKI_BASE_URL}/devices/status"

LOW_RISK = "low risk"
MEDIUM_RISK = "medium risk"
HIGH_RISK = "high risk"
