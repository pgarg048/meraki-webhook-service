from fastapi import FastAPI, Request, HTTPException # pyright: ignore[reportMissingImports]

from app.utils.logger import get_logger
from app.meraki_adaptors.adaptors import normalize_meraki_event
from meraki_acr_framework.plugin_manager import PluginManager

logger = get_logger(__name__)
app = FastAPI()

plugin_manager = PluginManager()

@app.post("/meraki/webhook")
async def meraki_webhooks(request: Request):
    """Entry Point"""
    try:
        payload = await request.json()
        logger.info("Received payload: %s", payload)
        # Normalize event through adaptor
        event = normalize_meraki_events(payload)
        analyzer_payload = analyze_event_and_analyzer(event)
        if not analyzer_payload["issue"]:
            return {"message": "No issue detected."}
        analyze_issue_and_resolver(analyzer_payload)
        return {
            "message": "Issue Resolved",
            "issue": analyzer_payload["issue"]
        }
    except Exception as e:
        raise HTTPException(status_code=500)


def analyze_event_and_analyzer(event):
    logger.info("Analyzing event: %s", event["event_type_id"])
    analyzer = plugin_manager.get_analyzer(event["event_type_id"])
    logger.info("Analyzer found: %s", bool(analyzer))
    if analyzer:
        result = analyzer.analyze(event)
        if result and result.get("issue"):
            return result
    return {"issue": None}

def analyze_issue_and_resolver(issue_obj):
    resolver = plugin_manager.get_resolver(issue_obj["issue"])
    if resolver:
        resolver.resolve(issue_obj)
