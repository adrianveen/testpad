from typing import Sequence, Optional
from matplotlib.figure import Figure

def build_do2_time_series(measurements: Sequence[tuple[int, float]],
                          temperature_c: Optional[float]) -> Figure:
    fig = Figure(figsize=(5, 3), tight_layout=True)
    ax = fig.add_subplot(111)
    if measurements:
        mins, vals = zip(*sorted(measurements))
        ax.plot(mins, vals, marker="o")
    ax.set_xlabel("Minute")
    ax.set_ylabel("Dissolved O₂ (mg/L)")
    if temperature_c is not None:
        ax.set_title(f"Dissolved O₂ vs Time (Temp {temperature_c:.1f}°C)")
    else:
        ax.set_title("Dissolved O₂ vs Time")
    ax.grid(alpha=0.3)
    return fig