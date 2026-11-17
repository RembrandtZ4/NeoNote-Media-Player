"""Erzeugt version_info.txt für PyInstaller (Dateibeschreibung „NeoNote Media Player“ – so heißt der Player
in der Taskleiste, im Task-Manager und in der Windows-Mediensteuerung)."""
import re, sys
from pathlib import Path
src = Path(sys.argv[1] if len(sys.argv) > 1 else "../neonote.py").read_text(encoding="utf-8")
ver = re.search(r'^APP_VERSION = "([^"]+)"', src, re.M).group(1)
nums = (list(map(int, re.findall(r"\d+", ver))) + [0, 0, 0, 0])[:4]
t = tuple(nums)
Path("version_info.txt").write_text(f"""VSVersionInfo(
  ffi=FixedFileInfo(filevers={t}, prodvers={t}, mask=0x3f, flags=0x0, OS=0x40004, fileType=0x1, subtype=0x0, date=(0, 0)),
  kids=[
    StringFileInfo([StringTable('040704B0', [
      StringStruct('CompanyName', 'NeoNote'),
      StringStruct('FileDescription', 'NeoNote Media Player'),
      StringStruct('FileVersion', '{ver}'),
      StringStruct('InternalName', 'NeoNote'),
      StringStruct('OriginalFilename', 'NeoNote.exe'),
      StringStruct('ProductName', 'NeoNote Media Player'),
      StringStruct('ProductVersion', '{ver}')])]),
    VarFileInfo([VarStruct('Translation', [0x0407, 1200])])
  ]
)
""", encoding="utf-8")
print("version_info.txt:", ver)
