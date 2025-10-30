"""
WebSocket server for real-time notifications
Handles commission alerts, payment status updates, and live dashboard updates
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Set
from aiohttp import web, WSMsgType
import aiohttp_cors
from supabase_client import get_supabase

# Connected clients by user_id
connected_clients: Dict[str, Set[web.WebSocketResponse]] = {}


# Event types
class EventTypes:
    COMMISSION_CREATED = "commission_created"
    COMMISSION_UPDATED = "commission_updated"
    PAYMENT_CREATED = "payment_created"
    PAYMENT_STATUS_CHANGED = "payment_status_changed"
    SALE_CREATED = "sale_created"
    DASHBOARD_UPDATE = "dashboard_update"


async def websocket_handler(request):
    """Handle WebSocket connections"""
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    user_id = None

    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)

                    # Handle authentication
                    if data.get("type") == "auth":
                        user_id = data.get("user_id")
                        if user_id:
                            if user_id not in connected_clients:
                                connected_clients[user_id] = set()
                            connected_clients[user_id].add(ws)

                            # Send confirmation
                            await ws.send_json(
                                {
                                    "type": "auth_success",
                                    "message": "Authenticated successfully",
                                    "timestamp": datetime.now().isoformat(),
                                }
                            )
                            print(f"User {user_id} connected")

                    # Handle ping/pong for keepalive
                    elif data.get("type") == "ping":
                        await ws.send_json(
                            {"type": "pong", "timestamp": datetime.now().isoformat()}
                        )

                except json.JSONDecodeError:
                    await ws.send_json({"type": "error", "message": "Invalid JSON"})

            elif msg.type == WSMsgType.ERROR:
                print(f"WebSocket error: {ws.exception()}")

    finally:
        # Clean up on disconnect
        if user_id and user_id in connected_clients:
            connected_clients[user_id].discard(ws)
            if not connected_clients[user_id]:
                del connected_clients[user_id]
            print(f"User {user_id} disconnected")

    return ws


async def broadcast_to_user(user_id: str, event_type: str, data: dict):
    """Send event to specific user"""
    if user_id not in connected_clients:
        return

    message = {"type": event_type, "data": data, "timestamp": datetime.now().isoformat()}

    # Send to all connections for this user
    disconnected = set()
    for ws in connected_clients[user_id]:
        try:
            await ws.send_json(message)
        except Exception as e:
            print(f"Error sending to user {user_id}: {e}")
            disconnected.add(ws)

    # Clean up disconnected clients
    for ws in disconnected:
        connected_clients[user_id].discard(ws)


async def broadcast_to_all(event_type: str, data: dict):
    """Send event to all connected users"""
    message = {"type": event_type, "data": data, "timestamp": datetime.now().isoformat()}

    for user_id in list(connected_clients.keys()):
        disconnected = set()
        for ws in connected_clients[user_id]:
            try:
                await ws.send_json(message)
            except Exception as e:
                print(f"Error broadcasting to user {user_id}: {e}")
                disconnected.add(ws)

        # Clean up disconnected clients
        for ws in disconnected:
            connected_clients[user_id].discard(ws)


async def listen_to_database_changes():
    """Listen to Supabase realtime changes (simulated with polling)"""
    supabase = get_supabase()
    last_check = datetime.now()

    while True:
        try:
            # Check for new commissions
            response = (
                supabase.table("commissions")
                .select("*")
                .gte("created_at", last_check.isoformat())
                .execute()
            )

            for commission in response.data:
                affiliate_id = commission.get("affiliate_id")
                if affiliate_id:
                    await broadcast_to_user(
                        str(affiliate_id),
                        EventTypes.COMMISSION_CREATED,
                        {
                            "commission_id": commission["id"],
                            "amount": commission["amount"],
                            "sale_id": commission["sale_id"],
                        },
                    )

            # Check for payment status changes
            response = (
                supabase.table("payments")
                .select("*")
                .gte("updated_at", last_check.isoformat())
                .execute()
            )

            for payment in response.data:
                affiliate_id = payment.get("affiliate_id")
                if affiliate_id:
                    await broadcast_to_user(
                        str(affiliate_id),
                        EventTypes.PAYMENT_STATUS_CHANGED,
                        {
                            "payment_id": payment["id"],
                            "status": payment["status"],
                            "amount": payment["amount"],
                        },
                    )

            last_check = datetime.now()

        except Exception as e:
            print(f"Error listening to database: {e}")

        # Check every 5 seconds
        await asyncio.sleep(5)


async def init_app():
    """Initialize aiohttp application"""
    app = web.Application()

    # Configure CORS
    cors = aiohttp_cors.setup(
        app,
        defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True, expose_headers="*", allow_headers="*", allow_methods="*"
            )
        },
    )

    # Add WebSocket route
    app.router.add_get("/ws", websocket_handler)

    # Configure CORS on all routes
    for route in list(app.router.routes()):
        cors.add(route)

    # Start database listener
    app["db_listener"] = asyncio.create_task(listen_to_database_changes())

    return app


async def cleanup(app):
    """Cleanup on shutdown"""
    if "db_listener" in app:
        app["db_listener"].cancel()
        try:
            await app["db_listener"]
        except asyncio.CancelledError:
            pass

    # Close all WebSocket connections
    for user_id in list(connected_clients.keys()):
        for ws in connected_clients[user_id]:
            await ws.close()


if __name__ == "__main__":
    app = web.run_app(init_app(), host="localhost", port=8080, shutdown_timeout=60.0)
