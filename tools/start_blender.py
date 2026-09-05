import importlib.util,bpy
from pathlib import Path
p=Path(__file__).resolve().with_name('blender_mcp_addon.py')
spec=importlib.util.spec_from_file_location('blender_mcp_addon',p)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.register()
server=m.BlenderMCPServer(host='127.0.0.1',port=9876);server.start()
bpy.context.scene.blendermcp_server_running=True
print('POKEPIA MCP READY',flush=True)
