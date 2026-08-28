"""Built-in paper appearance presets."""

from __future__ import annotations

from dataclasses import dataclass

from paperize.config import UnitAmount


@dataclass(frozen=True, slots=True)
class RgbColor:
    """An RGB color whose channels are normalized to 0 through 1."""

    red: float
    green: float
    blue: float

    def __post_init__(self) -> None:
        """Reject invalid channel values."""
        for channel in (self.red, self.green, self.blue):
            UnitAmount(channel)


@dataclass(frozen=True, slots=True)
class PaperPreset:
    """Data controlling a paper-colored multiply overlay."""

    name: str
    paper: RgbColor
    base_opacity: UnitAmount
    default_texture: UnitAmount
    texture_ink: RgbColor
    texture_seed: int


PRESETS: dict[str, PaperPreset] = {
    "cream": PaperPreset(
        name="cream",
        paper=RgbColor(0.98, 0.91, 0.72),
        base_opacity=UnitAmount(0.42),
        default_texture=UnitAmount(0.03),
        texture_ink=RgbColor(0.62, 0.49, 0.31),
        texture_seed=1103,
    ),
    "parchment": PaperPreset(
        name="parchment",
        paper=RgbColor(0.95, 0.80, 0.53),
        base_opacity=UnitAmount(0.48),
        default_texture=UnitAmount(0.08),
        texture_ink=RgbColor(0.50, 0.34, 0.19),
        texture_seed=2207,
    ),
    "sepia": PaperPreset(
        name="sepia",
        paper=RgbColor(0.88, 0.68, 0.40),
        base_opacity=UnitAmount(0.38),
        default_texture=UnitAmount(0.12),
        texture_ink=RgbColor(0.40, 0.25, 0.13),
        texture_seed=3313,
    ),
}


def get_preset(name: str) -> PaperPreset:
    """Return a preset by its public name."""
    return PRESETS[name]
