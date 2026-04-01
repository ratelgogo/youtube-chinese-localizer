#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="${0:A:h}"
SKILL_DIR="${SCRIPT_DIR:h}"
VENV_PYTHON="${SKILL_DIR}/.venv/bin/python"

if [[ -x "${VENV_PYTHON}" ]]; then
  exec "${VENV_PYTHON}" "${SCRIPT_DIR}/localize_video.py" "$@"
fi

if command -v python3 >/dev/null 2>&1; then
  exec python3 "${SCRIPT_DIR}/localize_video.py" "$@"
fi

echo "Missing Python runtime. Create ${SKILL_DIR}/.venv or install python3." >&2
exit 1
