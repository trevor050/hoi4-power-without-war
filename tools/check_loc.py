"""Static check: every localization_key in scripted localisation resolves to a
loc key in mod/localisation/english. Raw keys on screen (for example a nested
defined_text used as a localization_key) fail this check. Exit 1 on failure.
Usage: python tools/check_loc.py
"""
import glob
import re
import sys

keys = set()
for f in glob.glob("mod/localisation/english/*.yml"):
    for line in open(f, encoding="utf-8-sig"):
        m = re.match(r"\s+([A-Za-z0-9_.\-]+):\d*\s", line)
        if m:
            keys.add(m.group(1))
missing = []
for f in glob.glob("mod/common/scripted_localisation/*.txt"):
    for k in re.findall(r"localization_key\s*=\s*([A-Za-z0-9_.\-]+)", open(f, encoding="utf-8-sig").read()):
        if k not in keys:
            missing.append((f, k))
for f, k in missing:
    print(f"MISSING {k} (in {f})")
print(f"check_loc: {len(missing)} missing")
sys.exit(1 if missing else 0)
