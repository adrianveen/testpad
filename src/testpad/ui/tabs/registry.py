from dataclasses import dataclass
from importlib import import_module
from typing import Dict, Iterable, Iterator, Optional


@dataclass(frozen=True)
class TabSpec:
    module: str
    cls: str
    label: str
    feature_flag: Optional[str] = None
    lazy: bool = True

# TODO: Re-enable other tabs before release
TABS_SPEC = [
    TabSpec("testpad.ui.tabs.matching_box_tab", "MatchingBoxTab", "Matching Box"),
    TabSpec("testpad.ui.tabs.transducer_calibration_tab", "TransducerCalibrationTab", "Transducer Calibration Report"),
    TabSpec("testpad.ui.tabs.transducer_linear_tab", "TransducerLinearTab", "Transducer Linear Graphs"),
    TabSpec("testpad.ui.tabs.rfb_tab", "RFBTab", "Radiation Force Balance"),
    TabSpec("testpad.ui.tabs.vol2press_tab", "Vol2PressTab", "Sweep Analysis"),
    TabSpec("testpad.ui.tabs.burnin_tab", "BurninTab", "Burn-in Graph Viewer"),
    TabSpec("testpad.ui.tabs.nanobubbles_tab", "NanobubblesTab", "Nanobubbles Tab"),
    TabSpec("testpad.ui.tabs.temp_analysis_tab", "TempAnalysisTab", "Temperature Analysis"),
    TabSpec("testpad.ui.tabs.hydrophone_tab", "HydrophoneAnalysisTab", "Hydrophone Analysis"),
    TabSpec("testpad.ui.tabs.sweep_plot_tab", "SweepGraphTab", "Sweep Graphs"),
    TabSpec("testpad.ui.tabs.degasser_tab", "create_degasser_tab", "Degasser Data", feature_flag="degasser_tab")
]

def enabled_tabs(specs: Iterable[TabSpec], flags: Optional[Dict[str, bool]] = None) -> Iterator[TabSpec]:
    """Yield tabs whose feature_flag is unset or enabled in flags."""
    if flags is None:
        yield from specs
        return
    for spec in specs:
        if spec.feature_flag is None or flags.get(spec.feature_flag, False):
            yield spec

def load_tab_class(spec: TabSpec) -> type:
    """Import and return the tab class for a spec."""
    mod = import_module(spec.module)
    return getattr(mod, spec.cls)

__all__ = ["TabSpec", "TABS_SPEC", "enabled_tabs", "load_tab_class"]
