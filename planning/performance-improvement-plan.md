## **Performance Plan**

- Capture real startup metrics before changes by timing ApplicationWindow._ensure_loaded and the splash callbacks in src/testpad/testpad_main.py:54 and src/testpad/testpad_main.py:198; log module load durations coming through _progress_imports so you can compare first-load wins after each tweak.
- Keep the default tab lightweight: swap the first entry in tabs_spec (src/testpad/testpad_main.py:198) for a new “Home” dashboard with no heavy scientific deps, and move the current matching box tab behind a lazy loader so pandas/matplotlib aren’t imported on startup.
- Defer import of plotting stacks until users actually request graphs: replace the top-level from testpad.core.matching_box.csv_graphs_hioki import csv_graph in src/testpad/ui/tabs/matching_box_tab.py:7 with an on-demand import inside printCSVGraphs, and do the same pattern for other tabs (src/testpad/ui/tabs/vol2press_tab.py:10, src/testpad/ui/tabs/nanobubbles_tab.py:11, etc.) whose helpers pull in pandas and matplotlib (src/testpad/core/*/*.py like csv_graphs_hioki.py:8 and vol2press_calcs.py:3).
- After the main window is visible, spin up a background QThreadPool job that warms up the remaining tab modules using the existing progress callbacks in src/testpad/testpad_main.py:149; this preserves quick first paint but keeps later tab switches snappy.
- Trim bundled payloads: audit what really needs to ship under src/testpad/resources/mpl_cache and the large JPEG schematics in src/testpad/core/matching_box—keeping only the newest fontlist or converting images to optimized WebP/PNG shortens disk reads during startup.
- Refresh the PyInstaller spec (build_config/testpad_main-release.spec) to exclude dev notebooks (src/testpad/utils/trace_outputs.ipynb) and rely on the existing Matplotlib hook (build_config/runtime_hook_mpl.py:59) so frozen builds don’t re-scan fonts every run.

## **UX/UI Plan**

- Centralize styling instead of repeated inline rules like background-color: #66A366 across the tabs (src/testpad/ui/tabs/matching_box_tab.py:43, src/testpad/ui/tabs/vol2press_tab.py:171, etc.); create a QSS theme module and reuse tokens so the dark palette (src/testpad/resources/palette/custom_palette.py:6) and button states feel intentional.
- Introduce structure and breathing room: many grids (e.g., src/testpad/ui/tabs/matching_box_tab.py:59 and src/testpad/ui/tabs/vol2press_tab.py:96) cram controls edge-to-edge—add section headers, consistent spacing, and helper text to align with modern desktop app patterns.
- Give the shell more polish by enabling QMainWindow affordances already available: add a toolbar/status area for progress and file context (src/testpad/testpad_main.py:17), surface recent files, and expose app actions with icons alongside text.
- Refine the splash/branding path so assets resolve reliably and scale crisply; consider pre-rendering the SVG in src/testpad/ui/splash.py:53 once at a higher resolution and caching it, and align typography with the rest of the app.

## **Quality & Tests**

- Stand up startup regression coverage (e.g., a pytest-qt smoke test under tests/ that spins the app and asserts the first tab loads) so future performance work doesn’t regress stability; once the lazy imports land, run the full test suite (pytest) after every change to honor the “don’t skip any tests” request.

## Next steps: 
1) baseline startup metrics and UX screenshots; 
2) prototype the lightweight home tab plus lazy imports; 
3) centralize styling and add the new regression test before iterating on further UX polish.