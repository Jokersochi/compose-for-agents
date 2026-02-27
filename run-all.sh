#!/usr/bin/env bash

set -u -o pipefail

usage() {
  cat <<'EOF'
Usage: ./run-all.sh [--dry-run]

Starts all top-level repositories that contain compose.yaml or compose.yml.

Options:
  --dry-run   Print commands without executing them
  -h, --help  Show this help message
EOF
}

dry_run=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      dry_run=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ "${dry_run}" -eq 0 ]]; then
  if ! command -v docker >/dev/null 2>&1; then
    echo "Docker CLI is not installed or not in PATH." >&2
    exit 1
  fi

  if ! docker info >/dev/null 2>&1; then
    echo "Docker daemon is not reachable. Start Docker and try again." >&2
    exit 1
  fi
fi

shopt -s nullglob
compose_files=("${script_dir}"/*/compose.yaml "${script_dir}"/*/compose.yml)
shopt -u nullglob

if [[ ${#compose_files[@]} -eq 0 ]]; then
  echo "No top-level compose files found."
  exit 0
fi

declare -a successful=()
declare -a failed=()

for compose_file in "${compose_files[@]}"; do
  repo_dir="$(dirname "${compose_file}")"
  repo_name="$(basename "${repo_dir}")"

  echo "=== START: ${repo_name} ==="
  if [[ "${dry_run}" -eq 1 ]]; then
    echo "[dry-run] (cd \"${repo_dir}\" && docker compose up -d --build)"
    successful+=("${repo_name}")
    continue
  fi

  if (cd "${repo_dir}" && docker compose up -d --build); then
    successful+=("${repo_name}")
  else
    echo "!!! FAILED: ${repo_name}" >&2
    failed+=("${repo_name}")
  fi
done

echo
echo "=== SUMMARY ==="
echo "Succeeded: ${#successful[@]}"
for repo in "${successful[@]}"; do
  echo "  - ${repo}"
done

echo "Failed: ${#failed[@]}"
for repo in "${failed[@]}"; do
  echo "  - ${repo}"
done

if [[ ${#failed[@]} -gt 0 ]]; then
  exit 1
fi

echo "All compose projects started."
