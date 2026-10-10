# Reignited AP world — maintenance + packaging targets.
#
# `world_version` (archipelago.json) and `ap_world_version` (__init__.py) must
# stay in lockstep. `make check-version` fails loudly on drift (CI hook);
# `make bump VERSION=x.y.z` updates both in one step and re-checks.

ARCHIPELAGO_JSON := archipelago.json
WORLD_INIT := __init__.py
WORLD_NAME := reignited
APWORLD := $(WORLD_NAME).apworld

.DEFAULT_GOAL := check-version
.PHONY: check-version bump package compile lint options-doc options-doc-force clean

check-version:
	@json_v=$$(sed -n 's/.*"world_version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' $(ARCHIPELAGO_JSON)); \
	py_v=$$(sed -n 's/.*ap_world_version[[:space:]]*=[[:space:]]*"\([^"]*\)".*/\1/p' $(WORLD_INIT)); \
	if [ -z "$$json_v" ]; then echo "ERROR: no world_version found in $(ARCHIPELAGO_JSON)" >&2; exit 1; fi; \
	if [ -z "$$py_v" ]; then echo "ERROR: no ap_world_version found in $(WORLD_INIT)" >&2; exit 1; fi; \
	if [ "$$json_v" != "$$py_v" ]; then \
		echo "ERROR: version drift: $(ARCHIPELAGO_JSON) world_version=$$json_v, $(WORLD_INIT) ap_world_version=$$py_v" >&2; \
		echo "Run 'make bump VERSION=x.y.z' (or edit both files) to resync." >&2; exit 1; \
	fi; \
	echo "version check OK: $$json_v"

bump:
	@if [ -z "$(VERSION)" ]; then echo "ERROR: usage: make bump VERSION=x.y.z" >&2; exit 1; fi; \
	sed -i 's/"world_version": *"[^"]*"/"world_version": "$(VERSION)"/' $(ARCHIPELAGO_JSON); \
	sed -i 's/ap_world_version *= *"[^"]*"/ap_world_version = "$(VERSION)"/' $(WORLD_INIT); \
	$(MAKE) --no-print-directory check-version

compile:
	python3 -m compileall -q .

lint:
	ruff check .

# Options reference: regenerate docs/options.md from Options.py.
# Needs ARCHIPELAGO_ROOT pointing at an AP source checkout (see
# scripts/gen_options_doc.py header).
options-doc:
	ARCHIPELAGO_ROOT=$(ARCHIPELAGO_ROOT) python3 scripts/gen_options_doc.py docs/options.md
options-doc-force:
	ARCHIPELAGO_ROOT=$(ARCHIPELAGO_ROOT) python3 scripts/gen_options_doc.py docs/options.md --force

# Package the world into an installable .apworld (zip with the world package
# at its root). Respects per-directory .apignore files; __pycache__ and
# previous .apworld artifacts never ship. Used by CI as a smoke test.
package: compile lint $(APWORLD)

$(APWORLD):
	python3 scripts/package_apworld.py "$@" "$(WORLD_NAME)"

clean:
	rm -f $(APWORLD)
	find . -name __pycache__ -type d -exec rm -rf {} +