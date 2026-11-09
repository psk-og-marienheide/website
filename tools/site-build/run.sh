#!/usr/bin/env bash
# (C) PSK OG Marienheide e.V., VR/Köln 1369
set -euo pipefail

mode="${1:?Expected serve or build}"
case "$mode" in serve|build) ;; *) echo 'Expected serve or build' >&2; exit 2 ;; esac

# Append a sentinel so command substitution preserves a trailing-space checkout.
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && printf '%s/' "$PWD")"
root="${root%/}"
cd -- "$root"
engine="${CONTAINER_ENGINE:-}"
if [[ -z "$engine" ]]; then
    if command -v podman >/dev/null 2>&1; then engine=podman
    elif command -v docker >/dev/null 2>&1; then engine=docker
    else echo 'Install/configure Podman or Docker before using serve/build.' >&2; exit 1
    fi
fi
command -v "$engine" >/dev/null 2>&1 || { echo "Container engine unavailable: $engine" >&2; exit 1; }
image_hash="$(sha256sum tools/site-build/Containerfile | cut -d ' ' -f 1)"
image="localhost/psk-site-builder:${image_hash}"
if ! "$engine" image inspect "$image" >/dev/null 2>&1; then
    echo 'Preparing the pinned Hugo builder: downloads base image/Hugo and writes engine image storage.'
    echo 'The builder occupies several hundred MB; later calls reuse it until Containerfile inputs change.'
    "$engine" build --tag "$image" --file tools/site-build/Containerfile tools/site-build
fi

mkdir -p build
user_flags=(--user "$(id -u):$(id -g)")
if [[ "$("$engine" --version)" == *podman* ]]; then user_flags+=(--userns=keep-id); fi
common=(run --rm "${user_flags[@]}" --read-only --cap-drop=ALL
    --security-opt=no-new-privileges --tmpfs /tmp:rw,nosuid,nodev
    --env HOME=/tmp --env HUGO_CACHEDIR=/work/cache --env HUGO_RESOURCEDIR=/work/resources
    --mount "type=bind,source=$root,target=/site,readonly"
    --mount "type=bind,source=$root/build,target=/work"
    --workdir /site)

if [[ "$mode" == serve ]]; then
    port="${PORT:-1313}"
    [[ "$port" =~ ^[0-9]+$ ]] && (( port >= 1024 && port <= 65535 )) || {
        echo 'PORT must be an integer from 1024 to 65535.' >&2; exit 2;
    }
    echo "Preview: http://127.0.0.1:$port/ (Ctrl+C stops it)"
    exec "$engine" "${common[@]}" --publish "127.0.0.1:$port:1313" "$image" \
        hugo server --bind 0.0.0.0 --port 1313 --baseURL "http://127.0.0.1:$port/" \
        --appendPort=false --liveReloadPort "$port" --poll 700ms --noBuildLock --renderToMemory --buildDrafts
fi

base_url="${BASE_URL:-https://www.psk-og-marienheide.de/}"
stage="$(mktemp -d "$root/build/output.XXXXXXXX")"
stage_name="${stage##*/}"
trap 'rm -rf -- "$stage"' EXIT
"$engine" "${common[@]}" --network none "$image" \
    hugo --baseURL "$base_url" --destination "/work/$stage_name" \
    --noBuildLock --minify --panicOnWarning
"$engine" "${common[@]}" --network none "$image" \
    python3 tools/check-site.py "/work/$stage_name" "$base_url"
# public is reserved for generated output; never follow an unexpected symlink.
[[ ! -L public ]] || { echo 'Refusing to replace a public symlink.' >&2; exit 1; }
rm -rf -- public
mv -- "$stage" public
trap - EXIT
echo 'Production build and static checks passed: public/'
