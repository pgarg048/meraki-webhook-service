import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse


from app.utils.logger import get_logger
from app.meraki_adaptors.adaptors import normalize_meraki_events
from meraki_acr_framework.app.plugin_manager import AnalyzerFactory, ResolverFactory


logger = get_logger(__name__)
app = FastAPI()

analyzer_factory = AnalyzerFactory()
resolver_factory = ResolverFactory()

app.mount("/static", StaticFiles(directory="static"), name="static")
# Initialize an in-memory list to store recent issues
app.state.recent_issues = []

@app.get("/alerts-ui")
async def get_alerts_ui():
    # Serve the alerts_dashboard.html file
    file_path = os.path.join("static", "alerts_dashboard.html")
    return FileResponse(file_path, media_type="text/html")

@app.post("/meraki/webhook")
async def meraki_webhooks(request: Request):
    """Entry Point"""
    try:
        payload = await request.json()
        logger.info("Received payload: %s", payload)
        # Normalize event through adaptor
        event = normalize_meraki_events(payload)
        result_payload = analyze_event_and_analyzer(event)
        if not result_payload["issue"]:
            return {"root_causes": "No issue detected on the cluster, kindly verify the event and try again."}

        resolution = analyze_issue_and_resolver(result_payload)
        result_payload["resolution_summary"] = resolution

        # Store the issue in recent_issues for UI retrieval
        app.state.recent_issues.append(result_payload)
        if len(app.state.recent_issues) > 20:
            app.state.recent_issues.pop(0)
        return result_payload
        
    except Exception as e:
        logger.error("Error processing webhook: %s", e)
        raise HTTPException(status_code=500)


@app.get("/alerts")
async def get_alerts():
    recent_issues = getattr(app.state, "recent_issues", [])
    alerts_list = []

    for issue_obj in recent_issues:
        alert_entry = {
            "alert_type": issue_obj.get("alert_type"),
            "severity": issue_obj.get("severity"),
            "root_causes": issue_obj.get("root_causes", []),
            "resolver": issue_obj.get("resolution_summary", None),
        }
        alerts_list.append(alert_entry)

    return alerts_list

def analyze_event_and_analyzer(event):
    analyzer = analyzer_factory.get_analyzer(event["event_type_id"])
    if analyzer:
        result = analyzer.analyze(event)
        if result and result.get("issue"):
            return result
    return {"issue": None}

def analyze_issue_and_resolver(issue_obj):
    resolution = []
    resolver = resolver_factory.get_resolver(issue_obj["issue"])
    if resolver:
        resolution_summary = resolver.resolve(issue_obj)
        if resolution_summary and resolution_summary.get("resolutions"):
            resolution["resolutions"] = resolution_summary["resolutions"]
            resolution["manual_steps"] = resolution_summary.get("manual_steps", [])
            resolution["recommendation"] = resolution_summary.get("recommendation", "")
            return resolution
    return {"resolutions": [], "manual_steps": ["No Auto resolution present, please contact Cisco TAC for further assistance."], "recommendation": "Please contact Cisco TAC for further assistance."}
