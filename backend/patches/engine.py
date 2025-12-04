"""
Deterministic Patch Generation Engine.
Generates plausible patch configurations based on module types and connections.

ABX-Core v1.3: This engine now produces first-class IR objects and full provenance
tracking for every generation run. The IR is serializable and replayable.
"""
import random
import time
from typing import List, Dict, Any, Literal, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from core import (
    settings,
    generate_patch_name,
    Provenance,
    PatchGenerationIR,
    RackStateIR,
    ModuleIR,
    PatchGenerationParams,
    PatchGraphIR,
    ConnectionIR,
    get_git_commit,
)
from racks.models import Rack, RackModule
from modules.models import Module
from cases.models import Case


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


# ================================================================================
# ABX-Core v1.3: IR-Aware Generation with Provenance
# ================================================================================


def build_rack_state_ir(db: Session, rack: Rack) -> RackStateIR:
    """
    Build a RackStateIR from a Rack model.

    This extracts the complete rack state into a deterministic IR representation.
    """
    # Get rack modules
    rack_modules = db.query(RackModule).filter(RackModule.rack_id == rack.id).all()

    modules_ir: List[ModuleIR] = []
    for rm in rack_modules:
        module = db.query(Module).filter(Module.id == rm.module_id).first()
        if module:
            modules_ir.append(
                ModuleIR(
                    module_id=module.id,
                    module_name=module.name,
                    module_type=module.module_type,
                    position_hp=rm.position_hp,
                    row=rm.row,
                )
            )

    # Get case info
    case = db.query(Case).filter(Case.id == rack.case_id).first()
    case_hp = case.hp if case else 104
    case_rows = case.rows if case else 1

    return RackStateIR(
        rack_id=rack.id,
        rack_name=rack.name,
        case_hp=case_hp,
        case_rows=case_rows,
        modules=modules_ir,
    )


def generate_patches_with_ir(
    db: Session,
    rack: Rack,
    seed: Optional[int] = None,
    config: Optional[PatchEngineConfig] = None,
) -> Tuple[PatchGenerationIR, List[PatchGraphIR], Provenance]:
    """
    ABX-Core v1.3 compliant patch generation with full IR and provenance.

    This function:
    1. Creates a PatchGenerationIR (deterministic IR)
    2. Tracks provenance for the run
    3. Calls the existing generation logic
    4. Converts output to PatchGraphIR format
    5. Returns (IR, patches, provenance) for storage

    Args:
        db: Database session
        rack: Rack to generate patches for
        seed: Random seed
        config: Engine configuration

    Returns:
        Tuple of (generation_ir, patch_graphs, provenance)
    """
    start_time = time.time()

    # Default seed and config
    if seed is None:
        seed = settings.default_generation_seed
    if config is None:
        config = PatchEngineConfig()

    # Build IR
    rack_state = build_rack_state_ir(db, rack)
    params = PatchGenerationParams(
        max_patches=config.max_patches,
        allow_feedback=config.allow_feedback,
        prefer_simple=config.prefer_simple,
    )

    generation_ir = PatchGenerationIR(
        run_id=f"patchgen-{rack.id}-{seed}",  # Deterministic run_id
        rack_state=rack_state,
        seed=seed,
        params=params,
        engine_version=settings.patch_engine_version,
        abx_core_version=settings.abx_core_version,
        created_at=datetime.now(timezone.utc).isoformat(),
        git_commit=get_git_commit(),
        host=None,  # Will be filled by Provenance
    )

    # Create provenance
    provenance = Provenance.create(
        entity_type="patch_batch",
        pipeline="patch_generation",
        engine_version=settings.patch_engine_version,
        git_commit=get_git_commit(),
    )

    # Generate patches using existing logic
    patch_specs = generate_patches_for_rack(db, rack, seed, config)

    # Convert to PatchGraphIR
    patch_graphs: List[PatchGraphIR] = []
    ir_hash = generation_ir.get_canonical_hash()

    for spec in patch_specs:
        connections_ir = [
            ConnectionIR(
                from_module_id=c.from_module_id,
                from_port=c.from_port,
                to_module_id=c.to_module_id,
                to_port=c.to_port,
                cable_type=c.cable_type,
            )
            for c in spec.connections
        ]

        graph = PatchGraphIR(
            patch_name=spec.name,
            category=spec.category,  # type: ignore
            connections=connections_ir,
            description=spec.description,
            generation_ir_hash=ir_hash,
            generation_seed=spec.generation_seed,
        )
        patch_graphs.append(graph)

    # Complete provenance
    end_time = time.time()
    provenance.mark_completed()
    provenance.add_metric("duration_ms", (end_time - start_time) * 1000)
    provenance.add_metric("patch_count", len(patch_graphs))
    provenance.add_metric(
        "connection_count", sum(len(p.connections) for p in patch_graphs)
    )

    return generation_ir, patch_graphs, provenance
