"""End-to-end test: launch the AcuityMD MCP server over stdio and call every tool.

Run from command-center/:  python -m pytest tests/test_mcp_server.py
(or plain: python tests/test_mcp_server.py)
"""
import asyncio
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[1]
# A dedicated exports folder, as the README tells users to set up (folder mode
# reads the newest CSV, so it must hold AcuityMD exports only).
EXPORTS = Path(tempfile.mkdtemp(prefix="acuitymd-exports-"))
shutil.copy(ROOT / "sample_data" / "acuitymd_targets.csv", EXPORTS)
ENV = {
    **os.environ,
    "PYTHONPATH": str(ROOT / "src"),
    "ACUITYMD_TARGETS": str(EXPORTS),
    "COMMAND_CENTER_SETTINGS": str(ROOT / "config" / "settings.example.yaml"),
    "COMMAND_CENTER_REPS": str(ROOT / "config" / "reps.example.yaml"),
    "POWERBI_METRICS": str(ROOT / "sample_data" / "powerbi_metrics.csv"),
    "NPI_OFFLINE": "1",
}
EXPECTED_TOOLS = {"dataset_info", "find_targets", "get_target", "territory_summary",
                  "whitespace", "verify_npi", "rep_performance", "reload_export"}


async def _call(session, name, **args):
    res = await session.call_tool(name, args)
    assert not res.isError, f"{name} failed: {res.content}"
    return json.loads(res.content[0].text)


async def _run():
    params = StdioServerParameters(command=sys.executable,
                                   args=["-m", "command_center.mcp_server"], env=ENV)
    async with stdio_client(params) as (r, w), ClientSession(r, w) as s:
        await s.initialize()
        tools = {t.name for t in (await s.list_tools()).tools}
        assert EXPECTED_TOOLS <= tools, tools

        info = await _call(s, "dataset_info")
        assert info["targets"] > 0 and info["columns_ignored"] == []

        top = await _call(s, "find_targets", limit=3)
        scores = [t["score"] for t in top["targets"]]
        assert scores == sorted(scores, reverse=True)

        rep = info["reps"][0]
        mine = await _call(s, "find_targets", rep=rep.split()[0].lower(), limit=200)
        assert mine["matched"] > 0 and all(t["rep"] == rep for t in mine["targets"])

        implant = await _call(s, "find_targets", profile="implant", limit=200)
        assert implant["matched"] == info["targets"]

        npi = top["targets"][0]["npi"]
        one = await _call(s, "get_target", query=npi)
        assert one["matched"] == 1 and one["targets"][0]["rank_in_export"] == 1

        summ = await _call(s, "territory_summary", group_by="rep")
        assert sum(g["targets"] for g in summ["groups"]) == info["targets"]

        ws = await _call(s, "whitespace", min_competitor_share=0.0)
        assert "conquest" in ws and "at_risk" in ws

        v = await _call(s, "verify_npi", npi="1234567890")
        assert v["status"] in ("invalid", "unchecked")

        perf = await _call(s, "rep_performance")
        assert perf["trends"] and "quota_attainment" in perf

        bad = await s.call_tool("find_targets", {"sort_by": "nonsense"})
        assert bad.isError

        return info, top


def test_mcp_server_end_to_end():
    asyncio.run(_run())


if __name__ == "__main__":
    info, top = asyncio.run(_run())
    print("OK:", info["targets"], "targets; top =", top["targets"][0]["name"], top["targets"][0]["score"])
