# Test harness

`tools/run_hoi4.py` runs the real Hearts of Iron IV (v1.20) against the mod in an isolated
user directory, waits for result markers in `game.log`, shuts the game down and reports.
`tools/map_tables.py` computes map tables (state regions, sea approaches) offline.

Requirements: Python 3.10+, `psutil` (optional), `numpy` and `Pillow` (map tables, screenshots).
A run takes 35 to 75 s (about 25 s to load vanilla, 60 s with Road to 56; 10 in-game days take about 4 s).

## Common commands

```
# Load test the mod and report script errors (3 in-game days, then quit)
python tools/run_hoi4.py
python tools/run_hoi4.py --r56                 # with The Road to 56 loaded first
python tools/run_hoi4.py --days 60             # longer soak

# Run a scenario test (a mod folder that logs "PWW_DONE <folder name>"), with the main mod
python tools/run_hoi4.py --test tests/engine/t1_resource_flows
# Several tests in one session, without the main mod
python tools/run_hoi4.py --no-pww --test tests/engine/t7_embargo --test tests/engine/t5_resource_rights

# Save and reload: run past the 1st of a month with autosave, then continue the save
python tools/run_hoi4.py --test <dir> --autosave MONTHLY --clear-saves
python tools/run_hoi4.py --test <dir> --continue-last-save
```

For a reload, pass exactly the same `--test`/`--mod` folders (descriptor names come from the
folder names and the save records them; a mismatch stops at a "Missing mods" dialog).
`--continue-last-save` drops `-start_tag` automatically (it overrides the reload).

Other options: `--tag POR` (start tag, default POR), `--speed 4` (0-indexed, 4 = fastest,
default), `--until REGEX`, `--timeout S` (default 900), `--screenshot` (game window only, at
completion), `--leave-running` (keep the game open for manual poking), `--dry-run`,
`--flags nosound nofilewatcher ...`, `--restore-user-files [DIR]`.

Output: `.hoi4-userdir/runs/<stamp>_<name>/` with `error.log`, `game.log`, `system.log`,
`setup.log`, `text.log`, `summary.json` (and `screen.png`).

Stale logs: at launch the harness deletes (or rotates to `game.prev.log`) the previous
`game.log`, and ignores any line whose wall-clock stamp is older than the launch, so a killed
run's or another session's `PWW_DONE` can never end a new run early.

## Log protocol

Emit from mod script with the `log` effect (it writes to `logs/game.log`):

```
log = "PWW_RESULT <test>.<check> PASS|FAIL|INFO <text; may use [?global.var], [THIS.GetTag], [GetDateText]>"
log = "PWW_DONE <test folder name>"
```

Drive a test from `on_daily` with a global day counter (for example `limit = { tag = GER }`,
`add_to_variable = { global.my_day = 1 }`, then branch on the day). Do not rely on
`on_startup`: it has no scope and does not fire when a save is loaded.

| exit code | meaning |
|---|---|
| 0 | completed, no FAIL, no error.log line containing `pww` |
| 1 | a FAIL result, or any error.log line containing `pww` |
| 2 | timeout (also says whether the game ever started) |
| 3 | refused: a game not started by the harness is running, lock held, bad path, or isolation failed |
| 4 | the game exited early (crash or manual close) |

## Start flow (verified 2026-11-25)

`hoi4.exe -gdpr-compliant -start_tag=POR -start_speed=4 -nosound -nofilewatcher -disableoutdatedmodwarning`
loads straight into a running single-player game as the tag, at full speed, with no clicks.
`-continuelastsave` (without `-start_tag`) loads the newest save in the user dir with no clicks.
Findings from probing:
- `-start_speed` is 0-indexed (0..4). 5 is out of range and runs at the slowest speed.
- `-userdir=` is ignored: `launcher-settings.json` `gameDataPath` (`%USER_DOCUMENTS%/...`) wins. A
  `userdir.txt`, a shadow install with its own launcher-settings, quoting and `-settings=` all
  failed. The game resolves `%USER_DOCUMENTS%` from the process `USERPROFILE`, which is what the
  harness redirects.
- The scripted test bundles (`<game>/tests`, `scenario_testing.*` console commands) are not
  available in the release build. Not used.
- `-hands_off` makes `HAI` the player (`NGame.HANDS_OFF_START_TAG`). Not needed.

## Isolation and safety: exactly what the harness writes

The game is launched with `USERPROFILE=<repo>/.hoi4-userdir/home`, so its user dir is
`.hoi4-userdir/home/Documents/Paradox Interactive/Hearts of Iron IV`. In it the harness writes
`dlc_load.json`, `mod/<name>.mod` descriptors (absolute `path=`), `settings.txt` (seeded by
reading the real one; windowed 1280x720, volume 0, autosave as requested, text saves) and
`pdx_settings.txt`. The game writes its logs, saves, caches and `crashes/` there. Other files in
`.hoi4-userdir/`: `harness.lock`, `harness_mods/` (generated sentinel mod), `backups/`, `runs/`,
and `home/appdata/...` (the GPU shader cache follows `USERPROFILE`).

The real user dir (`Documents/Paradox Interactive/Hearts of Iron IV`) is never written by the
harness. As a second guard:
- Before each launch, `dlc_load.json`, `settings.txt`, `pdx_settings.txt`,
  `gameplaysettings.txt` and `continue_game.json` are copied to `.hoi4-userdir/backups/<stamp>/`
  with a sha256 manifest and the list of `mod/` entries (the newest 30 backups are kept).
- After every run, including timeout, crash and kill (`finally`), each file is compared by
  sha256 and restored byte for byte if it differs; the result is printed
  (`real user files: unchanged (verified by sha256)`).
- If the real `logs/system.log` changes during a run, the run aborts and kills its game (exit 3).
- Manual recovery: `python tools/run_hoi4.py --restore-user-files` (latest backup) or pass a
  backup folder.
- Never touched: `launcher-v2*.sqlite`, save games, mod descriptors, everything else.

Process rules: one run at a time (`.hoi4-userdir/harness.lock`, stale locks cleared, an orphaned
harness game is killed). If any `hoi4.exe` runs that was not started by the harness (its command
line lacks the harness `-userdir=` tag), the run is refused and that game is never touched.
Timeouts kill only the harness's own process tree.

Do not delete `.hoi4-userdir` with a tool that follows NTFS junctions (none are created now, but
older builds created `.hoi4-userdir/_game` junctions into the install; that folder was removed).

## Map tables

```
python tools/map_tables.py --tag POR --resource tungsten          # vanilla
python tools/map_tables.py --r56 --tag POR --resource tungsten    # Road to 56
python tools/map_tables.py --json out.json                        # full per-state table
```

Script has no trigger for "sea regions adjacent to a state"; this tool derives them from
`provinces.bmp` pixel adjacency, `definition.csv`, `map/strategicregions` and `history/states`
(R56 replaces the last two and ships its own `provinces.bmp`/`definition.csv`). Runs in about 1.5 s.
Resource amounts it prints are the raw file values; in game `has_resources_amount` includes
modifiers (Guarda: 95 in file, 123 in game vanilla, 195 with R56).
