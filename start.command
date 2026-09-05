#!/bin/zsh
cd "${0:A:h}"
POKEPIA_NODE="$(command -v node)"
if [[ -z "$POKEPIA_NODE" ]]; then
  echo "Node.js 22.12 or newer is required. Install it from https://nodejs.org/"
  read -r "?Press Return to close."
  exit 1
fi
if [[ ! -d node_modules ]]; then
  npm install || exit 1
fi
exec "$POKEPIA_NODE" node_modules/vite/bin/vite.js --host 127.0.0.1 --port 5178
