#!/usr/bin/env python3
# Author: Tim Harrison
# Created: 2026-09-26
# Updated: 2026-10-31

"""Generate the options reference for the game info page.

Walks option_groups (the same grouping the AP web host renders) and emits a
markdown table per group from each option's dataclass docstring, display
name, and choices — mirroring what the Archipelago options page shows, but
in a form that lives in the repo.

Setup:
    ARCHIPELAGO_ROOT must point at an Archipelago source checkout (the
    directory containing Options.py / BaseClasses.py) — e.g.
        git clone --depth 1 https://github.com/ArchipelagoMW/Archipelago
    plus the few packages AP's Options module imports (no full AP install):
        pip install schema pathspec PyYAML typing_extensions
    Only AP's Options module and this world's Options layer are imported —
    the full World package (BaseClasses/AutoWorld) is not required.

Usage (run from world/):
    python3 scripts/gen_options_doc.py            # emit markdown to stdout
    python3 scripts/gen_options_doc.py FILE       # verify FILE matches (CI)
    python3 scripts/gen_options_doc.py FILE --force  # overwrite FILE
"""
import importlib.util
import inspect
import os
import sys

ap_root = os.environ.get('ARCHIPELAGO_ROOT')
if not ap_root:
    print('ERROR: set ARCHIPELAGO_ROOT to your Archipelago source checkout '
          '(the directory containing Options.py and BaseClasses.py)',
          file=sys.stderr)
    sys.exit(1)
sys.path.insert(0, ap_root)

from Options import Option  # type: ignore[import-not-found]  # noqa: E402

# Load this repo's Options.py (which defines option_groups) as part of a
# synthetic package so its relative imports (spyro1/spyro2/spyro3) resolve.
# The world's __init__.py (the full World class) is NOT imported: it needs
# BaseClasses and worlds.AutoWorld, i.e. a complete AP dev environment.
_here = os.getcwd()
if os.path.basename(_here) == 'scripts':
    _here = os.path.dirname(_here)
_spec_pkg = importlib.util.spec_from_file_location(
    'srt_world', os.path.join(_here, '__init__.py'),
    submodule_search_locations=[_here])
_pkg = importlib.util.module_from_spec(_spec_pkg)
sys.modules['srt_world'] = _pkg
# Execute only a stub __init__ that imports the options layer.
_pkg_code = compile('from .Options import option_groups\n',
                    '__init__ (stub for gen_options_doc)', 'exec')
exec(_pkg_code, _pkg.__dict__)
option_groups = _pkg.option_groups


def default_text(default: object, choices: dict[str, int] | None) -> str:
    """Render a default as the YAML value a player would write for it."""
    # Sets stringify in hash order (PYTHONHASHSEED-dependent): render the YAML
    # list a player writes instead, sorted so the verify step is byte-stable
    # across runs.
    if isinstance(default, (set, frozenset)):
        return '[' + ', '.join(repr(v) for v in sorted(default)) + ']'
    # Choice/Toggle defaults are the int value, so the bare str() would show an
    # ordinal ("0"). Name them from the same table the Choices column prints.
    if choices:
        for choice_name, value in choices.items():
            if value == default:
                return choice_name
    return str(default)


def option_rows(opt: type[Option]) -> list[str]:
    name = getattr(opt, 'display_name', opt.__name__)
    doc = inspect.cleandoc(opt.__doc__ or '')
    # AP Choice/Toggle options expose options as dict[name] -> int value
    # (aliases included); the names are what a YAML accepts.
    choices = getattr(opt, 'options', None)
    choice_str = ', '.join(choices) if choices is not None else ''
    default_str = default_text(getattr(opt, 'default', None), choices)
    return [name, choice_str, default_str, doc.replace('\n', ' ')]


def main() -> None:
    lines = ['# Slot Options', '',
             'The options as grouped on the Archipelago settings page. '
             'Per-game options carry their game prefix in the YAML key.', '']
    for group in option_groups:
        lines.append(f'## {group.name}')
        lines.append('')
        lines.append('| Option | Choices | Default | Description |')
        lines.append('|---|---|---|---|')
        for opt in group.options:
            rows = option_rows(opt)
            lines.append('| ' + ' | '.join(
                c.replace('|', '\\|') for c in rows) + ' |')
        lines.append('')
    out = '\n'.join(lines)

    if len(sys.argv) > 1:
        path = sys.argv[1]
        if len(sys.argv) > 2 and sys.argv[2] == '--force':
            with open(path, 'w') as f:
                f.write(out)
            print(f'{path} written')
        else:
            with open(path) as f:
                if f.read() != out:
                    print(f'ERROR: {path} is stale — regenerate with: '
                          f'python3 scripts/gen_options_doc.py {path} --force',
                          file=sys.stderr)
                    sys.exit(1)
            print(f'{path} up to date')
    else:
        sys.stdout.write(out)


if __name__ == '__main__':
    main()
