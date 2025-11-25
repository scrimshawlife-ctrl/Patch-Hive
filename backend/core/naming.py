"""
Deterministic naming service for racks and patches.
Generates fun, memorable names based on seeds and hashing.
"""
import hashlib
from typing import Literal

# Word lists for generating names
ADJECTIVES = [
    "Midnight", "Solar", "Cosmic", "Quantum", "Crystal", "Digital", "Analog",
    "Warm", "Cold", "Deep", "Bright", "Dark", "Neon", "Vintage", "Future",
    "Chaotic", "Ordered", "Strange", "Harmonic", "Dissonant", "Rhythmic",
    "Melodic", "Textural", "Ambient", "Industrial", "Organic", "Synthetic",
    "Ethereal", "Gritty", "Smooth", "Rough", "Glitchy", "Flowing", "Frozen",
    "Burning", "Electric", "Magnetic", "Gravitational", "Temporal", "Spatial",
    "Fractal", "Recursive", "Modular", "Linear", "Circular", "Spiral",
    "Prismatic", "Monochrome", "Iridescent", "Phosphorescent"
]

NOUNS = [
    "Swarm", "Lattice", "Matrix", "Cascade", "Vortex", "Nexus", "Prism",
    "Echo", "Pulse", "Wave", "Drift", "Storm", "Shimmer", "Resonance",
    "Sequence", "Pattern", "Circuit", "Signal", "Field", "Spectrum",
    "Harmonics", "Overtones", "Frequencies", "Oscillations", "Modulations",
    "Envelope", "Filter", "Distortion", "Reverb", "Delay", "Chorus",
    "Phaser", "Flanger", "Tremolo", "Vibrato", "Arpeggio", "Glissando",
    "Cluster", "Texture", "Atmosphere", "Landscape", "Terrain", "Horizon",
    "Nebula", "Galaxy", "Constellation", "Aurora", "Eclipse", "Supernova"
]

PATCH_PREFIXES = [
    "Deep", "Bright", "Warm", "Cold", "Soft", "Hard", "Wide", "Narrow",
    "Fast", "Slow", "Evolving", "Static", "Random", "Sequenced", "Clocked",
    "Free", "Chaotic", "Ordered", "Dense", "Sparse", "Rich", "Minimal"
]

PATCH_TYPES = [
    "Bass", "Lead", "Pad", "Pluck", "Drone", "Percussion", "FX", "Noise",
    "Sweep", "Stab", "Chord", "Arpeggio", "Sequence", "Texture", "Atmosphere",
    "Glitch", "Loop", "Burst", "Pulse", "Wave", "Grain", "Cloud"
]


def generate_rack_name(seed: int) -> str:
    """
    Generate a deterministic rack name from a seed.

    Args:
        seed: Integer seed for deterministic generation

    Returns:
        A name like "Midnight Swarm" or "Solar Lattice"
    """
    # Use hash of seed to pick words
    hash_bytes = hashlib.sha256(str(seed).encode()).digest()
    adj_idx = int.from_bytes(hash_bytes[0:4], 'big') % len(ADJECTIVES)
    noun_idx = int.from_bytes(hash_bytes[4:8], 'big') % len(NOUNS)

    return f"{ADJECTIVES[adj_idx]} {NOUNS[noun_idx]}"


def generate_patch_name(
    seed: int,
    category: Literal["pad", "lead", "bass", "percussion", "fx", "generative", "utility"]
) -> str:
    """
    Generate a deterministic patch name from a seed and category.

    Args:
        seed: Integer seed for deterministic generation
        category: Patch category to influence naming

    Returns:
        A name like "Deep Evolving Pad" or "Bright Fast Lead"
    """
    # Use hash of seed to pick words
    hash_bytes = hashlib.sha256(str(seed).encode()).digest()
    prefix_idx = int.from_bytes(hash_bytes[0:4], 'big') % len(PATCH_PREFIXES)
    type_idx = int.from_bytes(hash_bytes[4:8], 'big') % len(PATCH_TYPES)

    # Sometimes add a prefix, sometimes just use type
    use_prefix = int.from_bytes(hash_bytes[8:9], 'big') % 2 == 0

    if use_prefix:
        return f"{PATCH_PREFIXES[prefix_idx]} {PATCH_TYPES[type_idx]}"
    else:
        # Use category-based name
        category_names = {
            "pad": "Pad",
            "lead": "Lead",
            "bass": "Bass",
            "percussion": "Percussion",
            "fx": "FX",
            "generative": "Generative",
            "utility": "Utility"
        }
        return f"{PATCH_PREFIXES[prefix_idx]} {category_names.get(category, 'Patch')}"


def hash_string_to_seed(input_str: str) -> int:
    """Convert a string to a deterministic integer seed."""
    return int.from_bytes(hashlib.sha256(input_str.encode()).digest()[:4], 'big')
