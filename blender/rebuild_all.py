from pathlib import Path
root=Path(__file__).resolve().parent
for filename in ['build_town.py','add_residents.py','export_web.py','finalize_scene.py']:
 exec(compile((root/filename).read_text(),filename,'exec'))
