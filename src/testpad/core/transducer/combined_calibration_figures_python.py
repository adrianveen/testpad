import re
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from PySide6.QtWidgets import QTextBrowser

from testpad.core.transducer.calibration_resources import (
    create_sweep_file,
    fetch_data,
    field_graph,
    fwhmx,
    line_graph,
)

"""
A script to write voltage sweep txts and to generate axial and lateral
field/line plots as SVGs.

- Cheap construction; heavy work done in run()
- Strong typing via a small config dataclass
- Pathlib and regex-based filename parsing
- Safer file selection and validation
- Stable natural sorting of filenames
- Centralized logging helper

Legacy compatibility is preserved via a thin wrapper class 'combined_calibration'.
"""


@dataclass
class CombinedCalibrationConfig:
    files: Sequence[Path]
    save_folder: Path | None
    eb50_file: Path | None
    sweep_data: bool
    axial_field: bool
    axial_line: bool
    lateral_field: bool
    lateral_line: bool
    save: bool
    ax_left_field_length: float
    ax_right_field_length: float
    ax_field_height: float
    ax_left_line_length: float
    ax_right_line_length: float
    lat_field_length: float
    interp_step: float


def _natural_key(p: Path) -> list[object]:
    name = p.name if isinstance(p, Path) else str(p)
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", name)]


def _parse_transducer_and_freq(
    filename: Path,
) -> tuple[str | None, str | None, float | None]:
    """Return (transducer_label, freq_label_str, freq_mhz_float).

    - transducer_label like '320-T1500H750'
    - freq_label_str like '500kHz' or '1.65MHz' (for display/legacy downstream use)
    - freq_mhz_float is the numeric frequency in MHz (for internal computations)
    """
    stem = filename.name
    # Transducer pattern: 320_T1500H750 or 320-T1500H750
    m_tx = re.search(r"(?P<num>\d+)[-_](?P<spec>T\d+H\d+)", stem)
    transducer = None
    if m_tx:
        transducer = f"{m_tx.group('num')}-{m_tx.group('spec')}"

    # Frequency patterns
    m_k = re.search(r"(?P<k>\d+(?:\.\d+)?)\s*kHz", stem, re.IGNORECASE)
    m_m = re.search(r"(?P<m>\d+(?:\.\d+)?)\s*MHz", stem, re.IGNORECASE)
    freq_label = None
    freq_mhz = None
    if m_k:
        val = float(m_k.group("k"))
        freq_label = f"{val:g}kHz"
        freq_mhz = val / 1000.0
    if m_m:
        valm = float(m_m.group("m"))
        # Prefer explicit MHz if present
        freq_label = f"{valm:g}MHz"
        freq_mhz = valm

    return transducer, freq_label, freq_mhz


class _CombinedCalibrationImpl:
    """Generates sweep/field/line graphs from calibration files.

    Construction is cheap; call run() to perform the work.
    getGraphs() lazily calls run() if needed, preserving legacy call sites
    that instantiate then immediately request graphs.
    """

    def __init__(
        self, config: CombinedCalibrationConfig, textbox: QTextBrowser | None = None
    ) -> None:
        self.config = config
        self.textbox = textbox
        self.graph_list: list[object | None] = [None] * 9
        self._ran = False

    # Logging helper for easy future swap to a logger
    def _log(self, msg: str) -> None:
        if self.textbox is not None:
            self.textbox.append(msg)
        else:
            print(msg)

    def run(self) -> None:
        if self._ran:
            return

        plt.close("all")  # closes previous graphs
        self._log("\n*******************GENERATING GRAPHS***********************\n")

        # Ensure textbox is available for required function calls
        if self.textbox is None:
            msg = "Textbox required for graph generation"
            raise ValueError(msg)
        textbox = self.textbox  # Create non-optional reference

        cfg = self.config

        # Normalize and sort files
        files_list: list[Path] = [Path(f) for f in cfg.files]
        files_list = sorted(files_list, key=_natural_key)

        offsets = [0.0, 0.0, 0.0]
        sweep_list: list[Path] = []
        axial_filename: Path | None = None
        lateral_filename: Path | None = None
        x_line_scan: Path | None = None
        y_line_scan: Path | None = None
        z_line_scan: Path | None = None

        # AUTOMATIC FILE DETECTION
        for f in files_list:
            n = f.name
            if "_sweep_" in n:
                sweep_list.append(f)
            elif "_yz_" in n:
                axial_filename = f
            elif "_xz_" in n:
                lateral_filename = f
            elif "_x_" in n:
                x_line_scan = f
            elif "_y_" in n:
                y_line_scan = f
            elif "_z_" in n:
                z_line_scan = f

        # Validate required files based on toggles
        try:
            trans_freq_filename: Path | None = None
            if cfg.sweep_data:
                self._log(f"Sweeps: {[p.name for p in sweep_list]}")
                if sweep_list:
                    trans_freq_filename = sweep_list[-1]
                else:
                    msg = "No sweep files found among selections."
                    raise NameError(msg)
            if cfg.axial_field:
                if axial_filename is None:
                    msg = "Missing axial (yz) field scan file."
                    raise NameError(msg)
                self._log(f"Axial: {axial_filename}")
                trans_freq_filename = axial_filename
            if cfg.axial_line:
                if y_line_scan is None:
                    msg = "Missing y-axis linear scan file."
                    raise NameError(msg)
                self._log(f"y linear: {y_line_scan}")
                trans_freq_filename = y_line_scan
            if cfg.lateral_field:
                if lateral_filename is None:
                    msg = "Missing lateral (xz) field scan file."
                    raise NameError(msg)
                self._log(f"Lateral: {lateral_filename}")
                trans_freq_filename = lateral_filename
            if cfg.lateral_line:
                if x_line_scan is None or z_line_scan is None:
                    msg = "Missing x or z linear scan files."
                    raise NameError(msg)
                self._log(f"x linear: {x_line_scan}")
                self._log(f"z linear: {z_line_scan}")
                trans_freq_filename = x_line_scan
            if not any(
                [
                    cfg.sweep_data,
                    cfg.axial_field,
                    cfg.axial_line,
                    cfg.lateral_field,
                    cfg.lateral_line,
                ]
            ):
                msg = "No outputs requested. Toggle at least one graph."
                raise NameError(msg)
        except NameError as e:
            self._log(
                f"\nNameError: {e}\n"
                "Oops! One or more of the scan files does not exist.\n"
                "Did you input the right folder?\nAre there scans missing?\n"
                "Did you select the correct checkboxes?\n"
            )
            self._ran = True
            return

        # TXT FILE OF FILES USED
        if cfg.save and cfg.save_folder:
            counter = 1
            save_dir = Path(cfg.save_folder)
            while True:
                try:
                    full_filename1 = save_dir / f"files_used_{counter}.txt"
                    with full_filename1.open("x") as f:
                        self._log(f"\nSaving files used to {full_filename1}...")
                        f.writelines(str(file) + "\n" for file in files_list)
                    break
                except FileExistsError:
                    counter += 1

        # TRANSDUCER AND FREQUENCY DETAILS
        transducer = None
        freq_label = None
        if trans_freq_filename is not None:
            transducer, freq_label, _freq_mhz = _parse_transducer_and_freq(
                trans_freq_filename
            )
        if transducer:
            self._log(f"\nTransducer: {transducer}")
        if freq_label:
            self._log(f"Frequency: {freq_label}\n")

        # VOLTAGE SWEEP
        if cfg.sweep_data and sweep_list:
            sweep_graph = create_sweep_file(
                [str(p) for p in sweep_list],
                str(cfg.save_folder) if cfg.save_folder else "",
                transducer if transducer else "",
                freq_label if freq_label else "",
                cfg.save,
                str(cfg.eb50_file) if cfg.eb50_file else "",
                textbox,
            )
            self.graph_list[0] = sweep_graph

        # FIELD GRAPHS
        if cfg.axial_field and axial_filename is not None:
            x_data, y_data, z_data, pressure, intensity, _ = fetch_data(
                str(axial_filename), "axial"
            )
            # Pressure field
            ax_pressure_field_graph = field_graph(
                y_data,
                z_data,
                pressure,
                cfg.ax_left_field_length,
                cfg.ax_right_field_length,
                cfg.ax_field_height,
                f"{transducer}_{freq_label}_pressure_axial_",
                "Axial ",
                "Pressure",
                cfg.interp_step,
                cfg.save,
                str(cfg.save_folder) if cfg.save_folder else "",
                textbox,
            )
            self.graph_list[1] = ax_pressure_field_graph
            # Intensity field
            ax_intensity_field_graph = field_graph(
                y_data,
                z_data,
                intensity,
                cfg.ax_left_field_length,
                cfg.ax_right_field_length,
                cfg.ax_field_height,
                f"{transducer}_{freq_label}_intensity_axial_",
                "Axial ",
                "Intensity",
                cfg.interp_step,
                cfg.save,
                str(cfg.save_folder) if cfg.save_folder else "",
                self.textbox,
            )
            self.graph_list[2] = ax_intensity_field_graph

        if cfg.lateral_field and lateral_filename is not None:
            x_data, y_data, z_data, pressure, intensity, _ = fetch_data(
                str(lateral_filename), "lateral"
            )
            # Pressure field
            lat_pressure_field_graph = field_graph(
                x_data,
                z_data,
                pressure,
                cfg.lat_field_length,
                cfg.lat_field_length,
                cfg.lat_field_length,
                f"{transducer}_{freq_label}_pressure_lateral_",
                "Lateral ",
                "Pressure",
                cfg.interp_step,
                cfg.save,
                str(cfg.save_folder) if cfg.save_folder else "",
                self.textbox,
            )
            self.graph_list[3] = lat_pressure_field_graph
            # Intensity field
            lat_intensity_field_graph = field_graph(
                x_data,
                z_data,
                intensity,
                cfg.lat_field_length,
                cfg.lat_field_length,
                cfg.lat_field_length,
                f"{transducer}_{freq_label}_intensity_lateral_",
                "Lateral ",
                "Intensity",
                cfg.interp_step,
                cfg.save,
                str(cfg.save_folder) if cfg.save_folder else "",
                self.textbox,
            )
            self.graph_list[4] = lat_intensity_field_graph

        # LINEAR GRAPHS
        # Y LINE SCAN LINE GRAPH
        if cfg.axial_line and y_line_scan is not None:
            x_data, y_data, z_data, pressure, intensity, pointer_location = fetch_data(
                str(y_line_scan), "axial"
            )
            # Pressure line
            y_pressure_line_graph = line_graph(
                y_data,
                pressure,
                cfg.ax_left_line_length,
                cfg.ax_right_line_length,
                f"{transducer}_{freq_label}_pressure_axial_",
                "Axial ",
                "Pressure",
                cfg.save,
                str(cfg.save_folder) if cfg.save_folder else "",
                self.textbox,
            )
            self.graph_list[5] = y_pressure_line_graph
            y_pressure_fwhmx, y_pressure_offset = fwhmx(
                y_data,
                pressure,
                cfg.ax_left_line_length,
                cfg.ax_right_line_length,
                "Y",
                "Axial ",
                "Pressure",
                self.textbox,
            )
            if pointer_location is not None and not isinstance(y_pressure_offset, str):
                offsets[1] = -1.0 * (pointer_location[1] - y_pressure_offset)
            # Intensity line
            y_intensity_line_graph = line_graph(
                y_data,
                intensity,
                cfg.ax_left_line_length,
                cfg.ax_right_line_length,
                f"{transducer}_{freq_label}_intensity_axial_",
                "Axial ",
                "Intensity",
                cfg.save,
                str(cfg.save_folder) if cfg.save_folder else "",
                self.textbox,
            )
            self.graph_list[6] = y_intensity_line_graph
            y_intensity_fwhmx, _ = fwhmx(
                y_data,
                intensity,
                cfg.ax_left_line_length,
                cfg.ax_right_line_length,
                "Y",
                "Axial ",
                "Intensity",
                self.textbox,
            )

            # PRINT AXIAL FWHMX
            if not isinstance(y_pressure_fwhmx, str) and not isinstance(
                y_intensity_fwhmx, str
            ):
                self._log("Axial FWHMX:")
                self._log(f"Pressure Axial Diameter: {y_pressure_fwhmx:0.1f} mm")
                self._log(f"Intensity Axial Diameter: {y_intensity_fwhmx:0.1f} mm")
            else:
                self._log("Couldn't output FWHMX for y-axis. Your data may be faulty.")

        if cfg.lateral_line and x_line_scan is not None and z_line_scan is not None:
            # X LINE SCAN
            x_data, y_data, z_data, pressure, intensity, pointer_location = fetch_data(
                str(x_line_scan), "lateral"
            )
            # Pressure line plot
            x_pressure_line_graph = line_graph(
                x_data,
                pressure,
                cfg.lat_field_length,
                cfg.lat_field_length,
                f"{transducer}_{freq_label}_pressure_lateral_",
                "Lateral ",
                "Pressure",
                cfg.save,
                str(cfg.save_folder) if cfg.save_folder else "",
                self.textbox,
            )
            self.graph_list[7] = x_pressure_line_graph
            x_pressure_fwhmx, x_pressure_offset = fwhmx(
                x_data,
                pressure,
                cfg.lat_field_length,
                cfg.lat_field_length,
                "X",
                "Lateral ",
                "Pressure",
                self.textbox,
            )
            if pointer_location is not None and not isinstance(x_pressure_offset, str):
                offsets[0] = pointer_location[0] - x_pressure_offset
            # Intensity line plot
            x_intensity_line_graph = line_graph(
                x_data,
                intensity,
                cfg.lat_field_length,
                cfg.lat_field_length,
                f"{transducer}_{freq_label}_intensity_lateral_",
                "Lateral ",
                "Intensity",
                cfg.save,
                str(cfg.save_folder) if cfg.save_folder else "",
                self.textbox,
            )
            self.graph_list[8] = x_intensity_line_graph
            x_intensity_fwhmx, _ = fwhmx(
                x_data,
                intensity,
                cfg.lat_field_length,
                cfg.lat_field_length,
                "X",
                "Lateral ",
                "Intensity",
                self.textbox,
            )

            # Z LINE SCAN
            x_data, y_data, z_data, pressure, intensity, pointer_location = fetch_data(
                str(z_line_scan), "lateral"
            )
            z_pressure_fwhmx, z_pressure_offset = fwhmx(
                z_data,
                np.transpose(pressure),
                cfg.lat_field_length,
                cfg.lat_field_length,
                "Z",
                "Lateral ",
                "Pressure",
                self.textbox,
            )
            if pointer_location is not None and not isinstance(z_pressure_offset, str):
                offsets[2] = pointer_location[2] - z_pressure_offset

            z_intensity_fwhmx, _ = fwhmx(
                z_data,
                np.transpose(intensity),
                cfg.lat_field_length,
                cfg.lat_field_length,
                "Z",
                "Lateral ",
                "Intensity",
                self.textbox,
            )

            # LATERAL FWHMX (AVERAGE OF X AND Z)
            if (
                not isinstance(x_pressure_fwhmx, str)
                and not isinstance(x_intensity_fwhmx, str)
                and not isinstance(z_pressure_fwhmx, str)
                and not isinstance(z_intensity_fwhmx, str)
            ):
                averaged_pressure_fwhmx = (x_pressure_fwhmx + z_pressure_fwhmx) / 2.0
                averaged_intensity_fwhmx = (x_intensity_fwhmx + z_intensity_fwhmx) / 2.0
                self._log("\nLateral FWHMX (averaged):")
                self._log(
                    f"Pressure Lateral Diameter: {averaged_pressure_fwhmx:0.1f} mm"
                )
                self._log(
                    f"Intensity Lateral Diameter: {averaged_intensity_fwhmx:0.1f} mm"
                )
            else:
                self._log(
                    "Couldn't output FWHMX for x-axis and z-axis. "
                    "Your data may be faulty."
                )

            offsets_str = [f"{i:0.2f}" for i in offsets]
            self._log(f"Offsets: [{','.join(offsets_str)}]")

        self._ran = True

    def get_graphs(self) -> list[object | None]:
        # Preserve legacy behavior: compute on first request
        """Return the list of graphs computed by the run() method.

        Preserves the legacy behavior of computing the graphs on the first request.
        Subsequent calls will return the cached result.

        Returns:
            list[FigureCanvas]: A list of FigureCanvas objects representing
                the computed graphs.

        """
        if not self._ran:
            self.run()
        return self.graph_list


# Backwards-compatible wrapper for existing call sites
class CombinedCalibration:
    """Public API that accepts CombinedCalibrationConfig or legacy list signature.

    Supports both modern and legacy usage:
    - Modern: CombinedCalibration(config_obj, textbox).get_graphs()
    - Legacy: CombinedCalibration(var_dict_list, textbox).get_graphs()
    """

    def __init__(
        self,
        variables_dict: CombinedCalibrationConfig | list,
        textbox: QTextBrowser | None = None,
    ) -> None:
        """Initialize the CombinedCalibration object."""
        # Check if already a config object (modern API)
        if isinstance(variables_dict, CombinedCalibrationConfig):
            cfg = variables_dict
        else:
            # Parse legacy variables list into config with typing
            files, save_folder, eb50_file = list(variables_dict[:3])
            sweep_data, axial_field, axial_line, lateral_field, lateral_line, save = [
                bool(i) for i in variables_dict[3:9]
            ]
            (
                ax_left_field_length,
                ax_right_field_length,
                ax_field_height,
                ax_left_line_length,
                ax_right_line_length,
                lat_field_length,
                interp_step,
            ) = [float(i) if i != "" else 0.0 for i in variables_dict[9:]]

            cfg = CombinedCalibrationConfig(
                files=[Path(p) for p in files],
                save_folder=Path(save_folder) if save_folder else None,
                eb50_file=Path(eb50_file) if eb50_file else None,
                sweep_data=sweep_data,
                axial_field=axial_field,
                axial_line=axial_line,
                lateral_field=lateral_field,
                lateral_line=lateral_line,
                save=save,
                ax_left_field_length=ax_left_field_length,
                ax_right_field_length=ax_right_field_length,
                ax_field_height=ax_field_height,
                ax_left_line_length=ax_left_line_length,
                ax_right_line_length=ax_right_line_length,
                lat_field_length=lat_field_length,
                interp_step=interp_step,
            )

        self._impl = _CombinedCalibrationImpl(cfg, textbox)

    def get_graphs(self) -> list[object | None]:
        """Return the list of graphs computed by the run() method."""
        return self._impl.get_graphs()


# (Legacy commented QML/init sections intentionally
# retained in original file were removed for clarity
# in this refactor. If needed, those sections can be
# restored without affecting current functionality.)
