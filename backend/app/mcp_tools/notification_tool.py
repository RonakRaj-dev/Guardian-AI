import time
from typing import Dict, Any, List

class NotificationMCPTool:
    """
    Notification MCP Tool Adapter: Handles multi-channel emergency alert dispatches
    (SMS, Email, WhatsApp, Emergency Dispatch Desk).
    """
    def dispatch_alert(
        self, 
        recipients: List[str], 
        message: str, 
        channels: List[str] = ["SMS", "DASHBOARD", "EMAIL"]
    ) -> Dict[str, Any]:
        
        dispatched_logs = []
        for channel in channels:
            log_entry = {
                "timestamp": time.time(),
                "channel": channel,
                "recipients": recipients,
                "status": "DELIVERED",
                "message_preview": message[:100] + "..." if len(message) > 100 else message
            }
            dispatched_logs.append(log_entry)
            print(f"[NotificationMCP] [{channel}] Dispatched to {recipients}: {message[:60]}...")
            
        return {
            "success": True,
            "channels_used": channels,
            "dispatches": dispatched_logs
        }

notification_mcp = NotificationMCPTool()
