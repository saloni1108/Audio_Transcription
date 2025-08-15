#!/usr/bin/env bash
python - "$1" <<'PY'
import sys, json
p=sys.argv[1]
print(json.dumps(open(p,'r',encoding='utf-8').read()))
PY
