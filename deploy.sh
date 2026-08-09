#!/usr/bin/env bash
# deploy.sh — deploy di produzione per LinkBay-CMS.
#
# Va eseguito SUL SERVER, dalla root del repo (/var/www/linkbay-cms).
# Stack: Flask (gunicorn) + Postgres + Traefik, orchestrato da compose.prod.yml.
#
# Cosa fa:
#   1. (opzionale) git pull dell'ultimo codice da origin
#   2. build dell'immagine web con le modifiche correnti (Dockerfile/requirements)
#   3. up -d dello stack (ricrea solo i container cambiati)
#   4. healthcheck sull'app + stato container
#
# Uso:
#   ./deploy.sh              # build + restart usando il codice GIA' presente sul disco
#   ./deploy.sh --pull       # fa prima 'git pull origin main', poi build + restart
#   ./deploy.sh --no-build   # solo restart, senza rebuild dell'immagine
#
# Nota: compose.prod.yml monta il codice come bind-mount (.:/app), quindi le
# modifiche al codice Python sono gia' nel container; il rebuild serve quando
# cambiano requirements.txt o Dockerfile. Il restart e' comunque necessario per
# far ripartire gunicorn e caricare il nuovo codice.

set -euo pipefail

# Sempre dalla directory dello script (root del repo)
cd "$(dirname "${BASH_SOURCE[0]}")"

COMPOSE_FILE="compose.prod.yml"
COMPOSE=(docker compose -f "${COMPOSE_FILE}")

DO_PULL=0
DO_BUILD=1
for arg in "$@"; do
  case "${arg}" in
    --pull)     DO_PULL=1 ;;
    --no-build) DO_BUILD=0 ;;
    -h|--help)
      grep '^#' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    *)
      echo "Opzione sconosciuta: ${arg}" >&2
      echo "Uso: ./deploy.sh [--pull] [--no-build]" >&2
      exit 2 ;;
  esac
done

# ── Preflight: file indispensabili ──────────────────────────────────────────
if [[ ! -f "${COMPOSE_FILE}" ]]; then
  echo "FALLITO: ${COMPOSE_FILE} non trovato. Sei nella root del repo?" >&2
  exit 1
fi
if [[ ! -f ".env" ]]; then
  echo "FALLITO: .env mancante. Serve per l'app (env_file) e per CF_DNS_API_TOKEN di Traefik." >&2
  echo "Crealo a mano prima di procedere — questo script non genera segreti." >&2
  exit 1
fi

if [[ "${DO_PULL}" == "1" ]]; then
  echo "==> git pull origin main"
  # Salvaguardia: se ci sono modifiche non committate importanti (es. Dockerfile
  # con gunicorn) le teniamo — git rifiuta il pull in caso di conflitto invece di
  # sovrascriverle silenziosamente.
  git pull origin main
fi

if [[ "${DO_BUILD}" == "1" ]]; then
  echo "==> Build dell'immagine web (nessun downtime: i container restano su finche' non facciamo up)"
  "${COMPOSE[@]}" build web
fi

echo "==> Avvio/aggiornamento dello stack (ricrea solo i container cambiati)"
"${COMPOSE[@]}" up -d

echo "==> Attendo che gunicorn risponda sulla porta 3000 dentro al container web"
OK=0
for i in $(seq 1 30); do
  if "${COMPOSE[@]}" exec -T web python -c \
    "import urllib.request,sys; urllib.request.urlopen('http://127.0.0.1:3000/', timeout=3); " \
    >/dev/null 2>&1; then
    OK=1
    break
  fi
  sleep 2
done

if [[ "${OK}" == "1" ]]; then
  echo "OK: l'app risponde su :3000."
else
  # Un 4xx/5xx sull'endpoint radice non e' per forza un guasto: verifichiamo che
  # il processo gunicorn sia comunque vivo prima di dichiarare fallimento.
  echo "AVVISO: nessuna risposta 2xx da / entro il timeout. Controllo se gunicorn e' vivo..."
  if "${COMPOSE[@]}" exec -T web pgrep -f gunicorn >/dev/null 2>&1; then
    echo "OK (parziale): gunicorn e' in esecuzione. Controlla i log se il sito non risponde:"
    echo "  ${COMPOSE[*]} logs -f web"
  else
    echo "FALLITO: gunicorn non risulta in esecuzione nel container web."
    echo "Log recenti:"
    "${COMPOSE[@]}" logs --tail 40 web || true
    exit 1
  fi
fi

echo "==> Pulizia immagini dangling (libera spazio, non tocca quelle in uso)"
docker image prune -f >/dev/null 2>&1 || true

echo "==> Stato finale dei container"
"${COMPOSE[@]}" ps

echo "==> Fatto."
