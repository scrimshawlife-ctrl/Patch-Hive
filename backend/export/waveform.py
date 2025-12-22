"""
Waveform approximation generator.
Creates SVG waveform visualizations based on patch characteristics.
"""
import math
from typing import Literal, Optional
from dataclasses import dataclass


WaveformType = Literal["sine", "saw", "square", "triangle", "noise", "complex"]


@dataclass
class WaveformParams:
    """Parameters for waveform generation."""

    waveform_type: WaveformType = "sine"
    frequency: float = 1.0  # Cycles per viewport
    amplitude: float = 0.8  # 0-1
    modulation_amount: float = 0.0  # 0-1
    modulation_rate: float = 0.2  # Cycles per viewport
    attack_time: float = 0.1  # 0-1
    decay_time: float = 0.3  # 0-1
    sustain_level: float = 0.7  # 0-1
    release_time: float = 0.2  # 0-1
    noise_amount: float = 0.0  # 0-1


def generate_waveform_svg(
    params: WaveformParams,
    width: int = 800,
    height: int = 200,
    samples: int = 500,
    seed: int = 42,
) -> str:
    """
    Generate an SVG waveform visualization.

    Args:
        params: Waveform parameters
        width: SVG width in pixels
        height: SVG height in pixels
        samples: Number of sample points
        seed: Random seed for noise

    Returns:
        SVG string
    """
    # Generate waveform samples
    points = []
    center_y = height / 2

    for i in range(samples):
        t = i / samples  # Time 0-1

        # Base waveform
        phase = t * params.frequency * 2 * math.pi
        if params.waveform_type == "sine":
            y = math.sin(phase)
        elif params.waveform_type == "saw":
            y = 2 * (t * params.frequency % 1) - 1
        elif params.waveform_type == "square":
            y = 1 if math.sin(phase) >= 0 else -1
        elif params.waveform_type == "triangle":
            y = 2 * abs(2 * (t * params.frequency % 1) - 1) - 1
        elif params.waveform_type == "noise":
            # Pseudo-random noise (deterministic)
            y = (hash((seed, i)) % 2000 - 1000) / 1000
        else:  # complex
            # Multiple harmonics
            y = (
                math.sin(phase)
                + 0.3 * math.sin(2 * phase)
                + 0.2 * math.sin(3 * phase)
                + 0.1 * math.sin(5 * phase)
            ) / 1.6

        # Apply modulation
        if params.modulation_amount > 0:
            mod = math.sin(t * params.modulation_rate * 2 * math.pi)
            y *= 1 - params.modulation_amount * 0.5 * (1 - mod)

        # Apply envelope
        envelope = calculate_envelope(t, params)
        y *= envelope

        # Add noise
        if params.noise_amount > 0:
            noise = (hash((seed + 1000, i)) % 200 - 100) / 1000
            y += noise * params.noise_amount

        # Scale and center
        y *= params.amplitude * (height * 0.4)
        y = center_y - y  # Flip Y axis for SVG

        # Calculate X position
        x = (i / samples) * width

        points.append((x, y))

    # Build SVG path
    path_data = f"M {points[0][0]} {points[0][1]}"
    for x, y in points[1:]:
        path_data += f" L {x} {y}"

    # Create SVG
    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <!-- Background -->
  <rect width="{width}" height="{height}" fill="#0a0a0a"/>

  <!-- Grid lines -->
  <line x1="0" y1="{center_y}" x2="{width}" y2="{center_y}" stroke="#333" stroke-width="1" stroke-dasharray="5,5"/>

  <!-- Waveform -->
  <path d="{path_data}" stroke="#00ff88" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>

  <!-- Glow effect -->
  <path d="{path_data}" stroke="#00ff88" stroke-width="4" fill="none" opacity="0.3" filter="url(#glow)"/>

  <!-- Filters -->
  <defs>
    <filter id="glow">
      <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
</svg>"""

    return svg


def calculate_envelope(t: float, params: WaveformParams) -> float:
    """
    Calculate ADSR envelope value at time t (0-1).

    Args:
        t: Time 0-1
        params: Waveform parameters

    Returns:
        Envelope amplitude 0-1
    """
    attack = params.attack_time
    decay = params.decay_time
    sustain = params.sustain_level
    release = params.release_time

    # Normalize times
    total_time = attack + decay + release
    if total_time > 1:
        # Scale down if times exceed 1
        scale = 1 / total_time
        attack *= scale
        decay *= scale
        release *= scale

    sustain_time = 1 - (attack + decay + release)

    if t < attack:
        # Attack phase
        return t / attack if attack > 0 else 1

    elif t < attack + decay:
        # Decay phase
        t_decay = (t - attack) / decay if decay > 0 else 1
        return 1 - (1 - sustain) * t_decay

    elif t < attack + decay + sustain_time:
        # Sustain phase
        return sustain

    else:
        # Release phase
        t_release = (t - attack - decay - sustain_time) / release if release > 0 else 1
        return sustain * (1 - t_release)


def infer_waveform_params_from_patch(
    patch_category: str, has_lfo: bool, has_envelope: bool
) -> WaveformParams:
    """
    Infer waveform parameters from patch characteristics.

    Args:
        patch_category: Category of the patch
        has_lfo: Whether patch uses LFO modulation
        has_envelope: Whether patch uses envelope

    Returns:
        WaveformParams instance
    """
    params = WaveformParams()

    category = normalize_patch_category(patch_category)

    # Base characteristics by category
    if category == "Voice":
        params.waveform_type = "complex"
        params.frequency = 2.0
        params.attack_time = 0.3
        params.decay_time = 0.2
        params.sustain_level = 0.8
        params.release_time = 0.4

    elif category == "Modulation":
        params.waveform_type = "saw"
        params.frequency = 4.0
        params.attack_time = 0.05
        params.decay_time = 0.15
        params.sustain_level = 0.6
        params.release_time = 0.15

    elif category == "Clock-Rhythm":
        params.waveform_type = "square"
        params.frequency = 1.5
        params.attack_time = 0.01
        params.decay_time = 0.3
        params.sustain_level = 0.4
        params.release_time = 0.1

    elif category == "Generative":
        params.waveform_type = "noise"
        params.frequency = 3.0
        params.attack_time = 0.01
        params.decay_time = 0.15
        params.sustain_level = 0.1
        params.release_time = 0.05
        params.noise_amount = 0.4

    elif category == "Texture-FX":
        params.waveform_type = "complex"
        params.frequency = 0.6
        params.attack_time = 0.1
        params.decay_time = 0.2
        params.sustain_level = 0.7
        params.release_time = 0.3
        params.noise_amount = 0.25

    elif category == "Utility":
        params.waveform_type = "sine"
        params.frequency = 1.0

    elif category == "Performance Macro":
        params.waveform_type = "triangle"
        params.frequency = 1.2
        params.modulation_amount = 0.4
        params.modulation_rate = 0.4

    elif category == "Study":
        params.waveform_type = "sine"
        params.frequency = 0.9

    elif category == "Experimental-Feedback":
        params.waveform_type = "complex"
        params.frequency = 1.8
        params.modulation_amount = 0.8
        params.modulation_rate = 0.6
        params.noise_amount = 0.5

    else:
        params.waveform_type = "sine"
        params.frequency = 1.0

    # Modify based on features
    if has_lfo:
        params.modulation_amount = max(params.modulation_amount, 0.4)

    if not has_envelope:
        params.attack_time = 0.0
        params.sustain_level = 1.0
        params.release_time = 0.0

    return params


def normalize_patch_category(category: str) -> str:
    if not category:
        return "Study"
    lower = category.strip().lower()
    mapping = {
        "pad": "Voice",
        "lead": "Voice",
        "bass": "Voice",
        "drone": "Voice",
        "clocked": "Clock-Rhythm",
        "percussion": "Clock-Rhythm",
        "fx": "Texture-FX",
        "fx/textures": "Texture-FX",
        "generative": "Generative",
        "utility": "Utility",
        "processing": "Utility",
    }
    return mapping.get(lower, category)
