"""
Deterministic Patch Generation Engine.
Generates plausible patch configurations based on module types and connections.
"""
import random
from typing import List, Dict, Any, Literal, Optional
from dataclasses import dataclass, field
from sqlalchemy.orm import Session

from core import settings, generate_patch_name
from racks.models import Rack, RackModule
from modules.models import Module


PatchCategory = Literal["pad", "lead", "bass", "percussion", "fx", "generative", "utility"]


@dataclass
class Connection:
    """Represents a cable connection between two module ports."""

    from_module_id: int
    from_port: str
    to_module_id: int
    to_port: str
    cable_type: str  # "audio", "cv", "gate", "clock"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "from_module_id": self.from_module_id,
            "from_port": self.from_port,
            "to_module_id": self.to_module_id,
            "to_port": self.to_port,
            "cable_type": self.cable_type,
        }


@dataclass
class PatchSpec:
    """Specification for a patch."""

    name: str
    category: PatchCategory
    connections: List[Connection] = field(default_factory=list)
    description: str = ""
    generation_seed: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "category": self.category,
            "connections": [c.to_dict() for c in self.connections],
            "description": self.description,
            "generation_seed": self.generation_seed,
        }


@dataclass
class PatchEngineConfig:
    """Configuration for patch generation."""

    max_patches: int = 20
    allow_feedback: bool = False
    prefer_simple: bool = False


class ModuleAnalyzer:
    """Analyzes modules in a rack to categorize them by function."""

    def __init__(self, db: Session, rack: Rack):
        self.db = db
        self.rack = rack
        self._analyze()

    def _analyze(self) -> None:
        """Categorize modules by type."""
        rack_modules = (
            self.db.query(RackModule).filter(RackModule.rack_id == self.rack.id).all()
        )

        self.all_modules: List[Module] = []
        self.vcos: List[Module] = []
        self.vcfs: List[Module] = []
        self.vcas: List[Module] = []
        self.envelopes: List[Module] = []
        self.lfos: List[Module] = []
        self.sequencers: List[Module] = []
        self.mixers: List[Module] = []
        self.effects: List[Module] = []
        self.utilities: List[Module] = []
        self.noise_sources: List[Module] = []

        for rm in rack_modules:
            module = self.db.query(Module).filter(Module.id == rm.module_id).first()
            if not module:
                continue

            self.all_modules.append(module)

            # Categorize by type
            mtype = module.module_type.upper()
            if "VCO" in mtype or "OSCILLATOR" in mtype:
                self.vcos.append(module)
            if "VCF" in mtype or "FILTER" in mtype:
                self.vcfs.append(module)
            if "VCA" in mtype or "AMPLIFIER" in mtype:
                self.vcas.append(module)
            if "ENV" in mtype or "ENVELOPE" in mtype or "ADSR" in mtype:
                self.envelopes.append(module)
            if "LFO" in mtype:
                self.lfos.append(module)
            if "SEQ" in mtype or "SEQUENCER" in mtype:
                self.sequencers.append(module)
            if "MIX" in mtype or "MIXER" in mtype:
                self.mixers.append(module)
            if "FX" in mtype or "EFFECT" in mtype or "REVERB" in mtype or "DELAY" in mtype:
                self.effects.append(module)
            if "UTIL" in mtype or "MULT" in mtype:
                self.utilities.append(module)
            if "NOISE" in mtype:
                self.noise_sources.append(module)


class PatchGenerator:
    """Generates patches based on module availability."""

    def __init__(self, analyzer: ModuleAnalyzer, seed: int, config: PatchEngineConfig):
        self.analyzer = analyzer
        self.seed = seed
        self.config = config
        self.rng = random.Random(seed)

    def generate_patches(self) -> List[PatchSpec]:
        """Generate all possible patches for the rack."""
        patches: List[PatchSpec] = []

        # Try different patch types based on available modules
        if self._can_generate_subtractive_voice():
            patches.extend(self._generate_subtractive_voices())

        if self._can_generate_generative():
            patches.extend(self._generate_generative_patches())

        if self._can_generate_percussion():
            patches.extend(self._generate_percussion())

        if self._can_generate_fx_chain():
            patches.extend(self._generate_fx_chains())

        # Limit to max patches
        return patches[: self.config.max_patches]

    def _can_generate_subtractive_voice(self) -> bool:
        """Check if we can generate a basic subtractive synthesis voice."""
        return len(self.analyzer.vcos) > 0 and len(self.analyzer.vcas) > 0

    def _generate_subtractive_voices(self) -> List[PatchSpec]:
        """Generate subtractive synthesis patches."""
        patches: List[PatchSpec] = []

        for i, vco in enumerate(self.analyzer.vcos[: min(3, len(self.analyzer.vcos))]):
            connections: List[Connection] = []

            # VCO → VCF → VCA → OUT (if filter available, otherwise VCO → VCA)
            current_module = vco

            # Optional filter
            if self.analyzer.vcfs:
                vcf = self.rng.choice(self.analyzer.vcfs)
                connections.append(
                    Connection(
                        from_module_id=current_module.id,
                        from_port="Audio Out",
                        to_module_id=vcf.id,
                        to_port="Audio In",
                        cable_type="audio",
                    )
                )
                current_module = vcf

            # VCA (required)
            if self.analyzer.vcas:
                vca = self.rng.choice(self.analyzer.vcas)
                connections.append(
                    Connection(
                        from_module_id=current_module.id,
                        from_port="Audio Out",
                        to_module_id=vca.id,
                        to_port="Audio In",
                        cable_type="audio",
                    )
                )

                # Envelope to VCA
                if self.analyzer.envelopes:
                    env = self.rng.choice(self.analyzer.envelopes)
                    connections.append(
                        Connection(
                            from_module_id=env.id,
                            from_port="Envelope Out",
                            to_module_id=vca.id,
                            to_port="CV In",
                            cable_type="cv",
                        )
                    )

            # LFO modulation (50% chance)
            if self.analyzer.lfos and self.rng.random() > 0.5:
                lfo = self.rng.choice(self.analyzer.lfos)
                target = self.rng.choice([vco, current_module])
                connections.append(
                    Connection(
                        from_module_id=lfo.id,
                        from_port="LFO Out",
                        to_module_id=target.id,
                        to_port="CV In",
                        cable_type="cv",
                    )
                )

            # Determine category based on envelope characteristics
            category: PatchCategory = "lead"
            if len(connections) > 5:
                category = "pad"  # More complex = pad-like
            elif len(self.analyzer.envelopes) > 0:
                category = self.rng.choice(["lead", "bass", "pad"])
            else:
                category = "drone"  # type: ignore

            patch_seed = self.seed + i
            patch = PatchSpec(
                name=generate_patch_name(patch_seed, category),
                category=category,
                connections=connections,
                description=f"Subtractive synthesis voice using {vco.name}",
                generation_seed=patch_seed,
            )
            patches.append(patch)

        return patches

    def _can_generate_generative(self) -> bool:
        """Check if we can generate generative patches."""
        return len(self.analyzer.sequencers) > 0 or len(self.analyzer.lfos) > 1

    def _generate_generative_patches(self) -> List[PatchSpec]:
        """Generate generative/evolving patches."""
        patches: List[PatchSpec] = []

        if not self.analyzer.sequencers and not self.analyzer.lfos:
            return patches

        connections: List[Connection] = []

        # Use sequencer or LFO as clock/modulation source
        if self.analyzer.sequencers:
            seq = self.rng.choice(self.analyzer.sequencers)

            # Sequence to VCO pitch
            if self.analyzer.vcos:
                vco = self.rng.choice(self.analyzer.vcos)
                connections.append(
                    Connection(
                        from_module_id=seq.id,
                        from_port="CV Out",
                        to_module_id=vco.id,
                        to_port="V/Oct",
                        cable_type="cv",
                    )
                )

        # Multiple LFOs for generative modulation
        if len(self.analyzer.lfos) >= 2:
            lfo1, lfo2 = self.analyzer.lfos[0], self.analyzer.lfos[1]

            if self.analyzer.vcos:
                vco = self.rng.choice(self.analyzer.vcos)
                connections.append(
                    Connection(
                        from_module_id=lfo1.id,
                        from_port="LFO Out",
                        to_module_id=vco.id,
                        to_port="FM In",
                        cable_type="cv",
                    )
                )

            if self.analyzer.vcfs:
                vcf = self.rng.choice(self.analyzer.vcfs)
                connections.append(
                    Connection(
                        from_module_id=lfo2.id,
                        from_port="LFO Out",
                        to_module_id=vcf.id,
                        to_port="Cutoff CV",
                        cable_type="cv",
                    )
                )

        if connections:
            patch_seed = self.seed + 1000
            patch = PatchSpec(
                name=generate_patch_name(patch_seed, "generative"),
                category="generative",
                connections=connections,
                description="Self-evolving generative patch with modulation",
                generation_seed=patch_seed,
            )
            patches.append(patch)

        return patches

    def _can_generate_percussion(self) -> bool:
        """Check if we can generate percussion patches."""
        return len(self.analyzer.noise_sources) > 0 or len(self.analyzer.envelopes) > 0

    def _generate_percussion(self) -> List[PatchSpec]:
        """Generate percussion-style patches."""
        patches: List[PatchSpec] = []

        if not (self.analyzer.noise_sources or self.analyzer.envelopes):
            return patches

        connections: List[Connection] = []

        # Noise → VCF → VCA (classic snare/hi-hat)
        if self.analyzer.noise_sources and self.analyzer.vcas:
            noise = self.analyzer.noise_sources[0]
            vca = self.rng.choice(self.analyzer.vcas)

            if self.analyzer.vcfs:
                vcf = self.rng.choice(self.analyzer.vcfs)
                connections.append(
                    Connection(
                        from_module_id=noise.id,
                        from_port="Noise Out",
                        to_module_id=vcf.id,
                        to_port="Audio In",
                        cable_type="audio",
                    )
                )
                connections.append(
                    Connection(
                        from_module_id=vcf.id,
                        from_port="Audio Out",
                        to_module_id=vca.id,
                        to_port="Audio In",
                        cable_type="audio",
                    )
                )
            else:
                connections.append(
                    Connection(
                        from_module_id=noise.id,
                        from_port="Noise Out",
                        to_module_id=vca.id,
                        to_port="Audio In",
                        cable_type="audio",
                    )
                )

            # Short envelope
            if self.analyzer.envelopes:
                env = self.analyzer.envelopes[0]
                connections.append(
                    Connection(
                        from_module_id=env.id,
                        from_port="Envelope Out",
                        to_module_id=vca.id,
                        to_port="CV In",
                        cable_type="cv",
                    )
                )

        if connections:
            patch_seed = self.seed + 2000
            patch = PatchSpec(
                name=generate_patch_name(patch_seed, "percussion"),
                category="percussion",
                connections=connections,
                description="Percussion voice using noise and envelope",
                generation_seed=patch_seed,
            )
            patches.append(patch)

        return patches

    def _can_generate_fx_chain(self) -> bool:
        """Check if we can generate FX processing chains."""
        return len(self.analyzer.effects) > 0

    def _generate_fx_chains(self) -> List[PatchSpec]:
        """Generate FX processing patches."""
        patches: List[PatchSpec] = []

        if not self.analyzer.effects:
            return patches

        connections: List[Connection] = []

        # Simple FX chain: IN → FX → OUT
        fx = self.analyzer.effects[0]

        # If there's a mixer, use it
        if self.analyzer.mixers:
            mixer = self.analyzer.mixers[0]
            connections.append(
                Connection(
                    from_module_id=mixer.id,
                    from_port="Mix Out",
                    to_module_id=fx.id,
                    to_port="FX In",
                    cable_type="audio",
                )
            )

        if connections:
            patch_seed = self.seed + 3000
            patch = PatchSpec(
                name=generate_patch_name(patch_seed, "fx"),
                category="fx",
                connections=connections,
                description=f"FX processing chain using {fx.name}",
                generation_seed=patch_seed,
            )
            patches.append(patch)

        return patches


def generate_patches_for_rack(
    db: Session, rack: Rack, seed: Optional[int] = None, config: Optional[PatchEngineConfig] = None
) -> List[PatchSpec]:
    """
    Main entry point for patch generation.

    Args:
        db: Database session
        rack: Rack to generate patches for
        seed: Random seed for deterministic generation
        config: Engine configuration

    Returns:
        List of generated patch specifications
    """
    if seed is None:
        seed = settings.default_generation_seed

    if config is None:
        config = PatchEngineConfig()

    # Analyze rack modules
    analyzer = ModuleAnalyzer(db, rack)

    # Check if rack has enough modules
    if len(analyzer.all_modules) < 2:
        return []

    # Generate patches
    generator = PatchGenerator(analyzer, seed, config)
    patches = generator.generate_patches()

    return patches
