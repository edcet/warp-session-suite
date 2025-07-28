#!/usr/bin/env bash
# install.sh - One-shot installer for Warp Session Suite
# This script will:
#   1. Install mise (https://github.com/jdx/mise) if it's not already present.
#   2. Clone (or update) the Warp Session Suite repo into ~/.warp-session-suite.
#   3. Run `mise install` to install toolchain versions defined by the suite.
#   4. Ensure your ~/.zshrc activates mise automatically.
#
# After installation you can upgrade the suite at any time with:
#   mise run self:update
#
# Usage (one-liner):
#   curl -sSfL https://raw.githubusercontent.com/edcet/warp-session-suite/main/install.sh | bash
set -euo pipefail

REPO_URL="https://github.com/edcet/warp-session-suite.git"
REPO_DIR="${HOME}/.warp-session-suite"
MZ="mise"

# 1. Install mise if it's not already available
if ! command -v "${MZ}" >/dev/null 2>&1; then
  echo "[warp-session-suite] mise not found – installing…" >&2
  curl -sSf https://mise.jdx.dev/install.sh | bash
  # mise installs into ~/.local/share/mise/bin – add it for the current run
  export PATH="${HOME}/.local/share/mise/bin:${PATH}"
fi

# 2. Clone or update the repo
if [ -d "${REPO_DIR}/.git" ]; then
  echo "[warp-session-suite] Updating existing repo at ${REPO_DIR}…" >&2
  git -C "${REPO_DIR}" pull --ff-only --no-tags --quiet
else
  echo "[warp-session-suite] Cloning repo into ${REPO_DIR}…" >&2
  git clone --depth 1 "${REPO_URL}" "${REPO_DIR}" --quiet
fi

# 3. Install toolchain versions with mise
cd "${REPO_DIR}"
"${MZ}" install

# 4. Ensure automatic mise activation for zsh
ZSHRC="${HOME}/.zshrc"
ACTIVATE='eval "$(mise activate zsh)"'
if [ ! -f "${ZSHRC}" ]; then
  touch "${ZSHRC}"
fi
if ! grep -Fq "${ACTIVATE}" "${ZSHRC}"; then
  echo "${ACTIVATE}" >>"${ZSHRC}"
  echo "[warp-session-suite] Added mise activation to ${ZSHRC}." >&2
fi

echo "[warp-session-suite] Installation complete! 👉 Restart your terminal or run 'source \"${ZSHRC}\"' to load mise."
echo "[warp-session-suite] To upgrade later, run: mise run self:update"
