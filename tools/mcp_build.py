import asyncio,sys,json,os
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
ROOT=Path(__file__).resolve().parents[1]
async def main():
 params=StdioServerParameters(command=str(ROOT/'tools/.venv/bin/blender-mcp'),env={**os.environ,'BLENDER_HOST':'localhost','BLENDER_PORT':'9876','DISABLE_TELEMETRY':'true'})
 async with stdio_client(params) as (read,write):
  async with ClientSession(read,write) as session:
   await session.initialize()
   ts=await session.list_tools();print('MCP tools:',[t.name for t in ts.tools],flush=True)
   if '--info' in sys.argv:
    r=await session.call_tool('get_scene_info',{} )
   else:
    script=Path(sys.argv[sys.argv.index('--script')+1]).resolve() if '--script' in sys.argv else ROOT/'blender/build_town.py'
    code="exec(compile(open("+repr(str(script))+").read(), "+repr(str(script))+", 'exec'), {'__file__': "+repr(str(script))+"})"
    r=await session.call_tool('execute_blender_code',{'code':code})
   print(r.model_dump_json(),flush=True)
   (ROOT/'evidence/mcp-result.json').write_text(r.model_dump_json(indent=2))
asyncio.run(main())
