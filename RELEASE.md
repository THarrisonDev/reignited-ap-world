# Release Checklist

Three repos move in lockstep for every release. Parent repo holds the
submodule pointers; the submodules hold the actual code and versions.

## Version touchpoints

| What | Where | Bumped when |
|------|-------|-------------|
| World version | `reignited-ap-world` → `archipelago.json` (`world_version`) + `world/__init__.py` (`ap_world_version`) | Any change to world logic, items, locations, or options |
| `version` / `compatible_version` | `reignited-ap-world` → `archipelago.json` | Only when save/patch format changes (data schema version, currently `7`) |
| `data_version` | `reignited-ap-world` → `world/__init__.py` | Only when slot data semantics change for already-generated seeds |
| Client protocol version | `reignited-ap-client` → `ue4ss_mod/srt_bridge/Scripts/main.lua` (`client_version`) and `launcher/feed.go` (`"version"`); `make audit` (scripts/audit_client_version.py) fails on drift | Any change to the mod ↔ server handshake surface |
| `minimum_ap_version` | `reignited-ap-world` → `archipelago.json` | Only when a new AP server feature becomes required |
| `required_client_version` | `reignited-ap-world` → `world/__init__.py` | When the world requires newer client behavior than `(0, 5, 0)` |

## Release order

1. **reignited-ap-world**
   - Land all world changes on `main`.
   - Bump the version: `make bump VERSION=x.y.z` (updates both files; the
     target fails if they drift — see `Makefile`).
   - Tag `vX.Y.Z` and push.
2. **reignited-ap-client**
   - Land all client changes on `main`; ensure `client_version` in `main.lua`
     matches `feed.go` if the handshake changed.
   - Build the binaries (`checkd`, `launcher`) and package the UE4SS mod
     (`srt_bridge/Scripts` only — `ue4ss_mod/api/` never ships).
   - Tag `vX.Y.Z` and push.
3. **reignited-ap (parent)**
   - Bump both submodule pointers to the freshly tagged commits
     (`git submodule update --remote`, then commit the pointer bump).
   - Build the single release artifact from the parent repo at the tagged
     commit: **`make bundle`** packages the world (`world/`), builds the
     client (`client/`), fetches the pinned UE4SS, and assembles
     `dist/reignited-ap_<version>_bundle.zip` — `START-HERE.txt`, `client/`
     (both launchers, `srtap_checkd.exe`, `srt_bridge.zip` with
     `lua-apclientpp.dll`, `install.bat`/`install.sh`, `INSTALL.md`,
     `THIRD-PARTY-NOTICES.md`), `world/reignited_<version>.apworld`, and the
     `UE4SS/` fallback. Attach it to the GitHub release. Override
     `UE4SS_ZIP=<path>` to use a local UE4SS copy instead of downloading.
     The mod's `lua-apclientpp.dll` is gitignored; place it in
     `client/ue4ss_mod/` before building or the client packaging step fails.
   - Write release notes: world version, client version, minimum AP version,
     upgrade notes (players must regenerate patches if `version`/`data_version`
     changed), and known limitations.

## Sanity checks before tagging

- [ ] `cd world && make check-version` — no drift.
- [ ] `cd client/checkd && go test ./...` and
      `cd client/launcher && go test ./...` — green.
- [ ] `cd client && make lua-tests && make audit` — green.
- [ ] `make bundle` (parent) builds cleanly and produces the bundle zip.
- [ ] The packaged `.apworld` installs into a real Archipelago checkout and
      generates a seed.
- [ ] One live boot with the shipped UE4SS mod + `checkd`: connect, send and
      receive an item.