#!/usr/bin/env python3
"""ZoneWise MCP Server for Claude Integration"""
from fastapi import FastAPI
import httpx
import os

app = FastAPI(title="ZoneWise MCP Server")

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

@app.get("/zoning/{parcel_account}")
async def get_parcel_zoning(parcel_account: str):
    """Get zoning info for a parcel"""
    async with httpx.AsyncClient(verify=False) as client:
        resp = await client.get(
            f"{SUPABASE_URL}/rest/v1/parcels",
            params={"account": f"eq.{parcel_account}"},
            headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
        )
        parcel = resp.json()
        if parcel:
            zoning_code = parcel[0].get("zoning_code")
            if zoning_code:
                resp = await client.get(
                    f"{SUPABASE_URL}/rest/v1/zoning_districts",
                    params={"code": f"eq.{zoning_code}"},
                    headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
                )
                district = resp.json()
                return {"parcel": parcel[0], "district": district[0] if district else None}
        return {"error": "Parcel not found"}

@app.get("/districts/{jurisdiction_id}")
async def get_districts(jurisdiction_id: int):
    """Get all zoning districts for a jurisdiction"""
    async with httpx.AsyncClient(verify=False) as client:
        resp = await client.get(
            f"{SUPABASE_URL}/rest/v1/zoning_districts",
            params={"jurisdiction_id": f"eq.{jurisdiction_id}"},
            headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
        )
        return resp.json()
