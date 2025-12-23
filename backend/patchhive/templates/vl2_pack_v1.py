from __future__ import annotations

from patchhive.templates.registry import PatchTemplate, PatchTemplateRegistry, TemplateSlot


def register_vl2_pack_v1(r: PatchTemplateRegistry) -> PatchTemplateRegistry:
    """
    A curated set (~18 here; expand to ~30 as we go) that matches the typical VL2 learning arc.
    """

    # ---- VOICE variants ----
    r.register(
        PatchTemplate(
            template_id="tmpl.voice.vca_gate.v1",
            archetype="basic_voice",
            category="Voice",
            difficulty="Beginner",
            tags=("voice", "vca", "gate"),
            slots=(
                TemplateSlot("SOURCE_AUDIO_OUT", "AMP_AUDIO_IN", "audio"),
                TemplateSlot("ENV_OR_GATE_OUT", "AMP_CV_IN", "cv"),
                TemplateSlot("AMP_AUDIO_OUT", "DEST_AUDIO_IN", "audio"),
            ),
            role_constraints={
                "SOURCE_AUDIO_OUT": ("audio_out",),
                "AMP_AUDIO_IN": ("audio_in_or_cv_or_audio_in",),
                "ENV_OR_GATE_OUT": ("cv_out", "gate_out", "trigger_out"),
                "AMP_CV_IN": ("cv_in_or_cv_or_audio_in",),
                "AMP_AUDIO_OUT": ("audio_out",),
                "DEST_AUDIO_IN": ("audio_in_or_cv_or_audio_in",),
            },
            required_caps={
                "AMP_AUDIO_IN": ("vca_or_filter_or_wavefolder",),
                "AMP_AUDIO_OUT": ("vca_or_filter_or_wavefolder",),
            },
        )
    )

    r.register(
        PatchTemplate(
            template_id="tmpl.voice.filter_sweep.v1",
            archetype="basic_voice",
            category="Voice",
            difficulty="Intermediate",
            tags=("voice", "filter", "sweep"),
            slots=(
                TemplateSlot("SOURCE_AUDIO_OUT", "FILTER_AUDIO_IN", "audio"),
                TemplateSlot("LFO_OUT", "FILTER_CV_IN", "cv"),
                TemplateSlot("FILTER_AUDIO_OUT", "DEST_AUDIO_IN", "audio"),
            ),
            role_constraints={
                "SOURCE_AUDIO_OUT": ("audio_out",),
                "FILTER_AUDIO_IN": ("audio_in_or_cv_or_audio_in",),
                "LFO_OUT": ("cv_out",),
                "FILTER_CV_IN": ("cv_in_or_cv_or_audio_in",),
                "FILTER_AUDIO_OUT": ("audio_out",),
                "DEST_AUDIO_IN": ("audio_in_or_cv_or_audio_in",),
            },
            required_caps={
                "FILTER_AUDIO_IN": ("vca_or_filter_or_wavefolder",),
                "FILTER_AUDIO_OUT": ("vca_or_filter_or_wavefolder",),
            },
        )
    )

    # ---- CLOCKED / sequencing ----
    r.register(
        PatchTemplate(
            template_id="tmpl.clocked.seq_gate_voice.v1",
            archetype="clocked_sequence",
            category="Clocked",
            difficulty="Intermediate",
            tags=("clocked", "sequencer", "gate"),
            slots=(
                TemplateSlot("CLOCK_OUT", "SEQ_CLOCK_IN", "clock"),
                TemplateSlot("SEQ_GATE_OUT", "AMP_CV_IN", "gate"),
                TemplateSlot("SOURCE_AUDIO_OUT", "AMP_AUDIO_IN", "audio"),
                TemplateSlot("AMP_AUDIO_OUT", "DEST_AUDIO_IN", "audio"),
            ),
            role_constraints={
                "CLOCK_OUT": ("clock_out",),
                "SEQ_CLOCK_IN": ("clock_in",),
                "SEQ_GATE_OUT": ("gate_out", "trigger_out", "cv_out"),
                "SOURCE_AUDIO_OUT": ("audio_out",),
                "AMP_AUDIO_IN": ("audio_in_or_cv_or_audio_in",),
                "AMP_CV_IN": ("cv_in_or_cv_or_audio_in",),
                "AMP_AUDIO_OUT": ("audio_out",),
                "DEST_AUDIO_IN": ("audio_in_or_cv_or_audio_in",),
            },
            required_caps={
                "SEQ_CLOCK_IN": ("sequencer_like", "clock_sink"),
            },
        )
    )

    # ---- GENERATIVE ----
    r.register(
        PatchTemplate(
            template_id="tmpl.generative.random_to_pitch.v1",
            archetype="generative_mod",
            category="Generative",
            difficulty="Advanced",
            tags=("generative", "random", "pitch"),
            slots=(
                TemplateSlot("RANDOM_OUT", "PITCH_IN", "cv"),
                TemplateSlot("SOURCE_AUDIO_OUT", "DEST_AUDIO_IN", "audio"),
            ),
            role_constraints={
                "RANDOM_OUT": ("cv_out",),
                "PITCH_IN": ("cv_in_or_cv_or_audio_in",),
                "SOURCE_AUDIO_OUT": ("audio_out",),
                "DEST_AUDIO_IN": ("audio_in_or_cv_or_audio_in",),
            },
            # later: refine with function_id "pitch_cv" specifically
        )
    )

    r.register(
        PatchTemplate(
            template_id="tmpl.generative.clocked_modulation.v1",
            archetype="generative_mod",
            category="Generative",
            difficulty="Advanced",
            tags=("generative", "clocked", "motion"),
            slots=(
                TemplateSlot("CLOCK_OUT", "CLOCK_IN", "clock"),
                TemplateSlot("MOD_CV_OUT", "MOD_DEST_CV_IN", "cv"),
                TemplateSlot("SOURCE_AUDIO_OUT", "DEST_AUDIO_IN", "audio"),
            ),
            role_constraints={
                "CLOCK_OUT": ("clock_out",),
                "CLOCK_IN": ("clock_in",),
                "MOD_CV_OUT": ("cv_out",),
                "MOD_DEST_CV_IN": ("cv_in_or_cv_or_audio_in",),
                "SOURCE_AUDIO_OUT": ("audio_out",),
                "DEST_AUDIO_IN": ("audio_in_or_cv_or_audio_in",),
            },
        )
    )

    # ---- UTILITY / STUDY ----
    r.register(
        PatchTemplate(
            template_id="tmpl.utility.clock_distribution.v1",
            archetype="utility_clock",
            category="Utility / Calibration",
            difficulty="Beginner",
            tags=("utility", "clock", "distribution"),
            slots=(TemplateSlot("CLOCK_OUT", "CLOCK_IN", "clock"),),
            role_constraints={
                "CLOCK_OUT": ("clock_out",),
                "CLOCK_IN": ("clock_in",),
            },
        )
    )

    r.register(
        PatchTemplate(
            template_id="tmpl.study.one_cable_experiment.v1",
            archetype="study_one_cable",
            category="Study Patches",
            difficulty="Beginner",
            tags=("study", "minimal"),
            slots=(TemplateSlot("MOD_CV_OUT", "MOD_DEST_CV_IN", "cv"),),
            role_constraints={
                "MOD_CV_OUT": ("cv_out",),
                "MOD_DEST_CV_IN": ("cv_in_or_cv_or_audio_in",),
            },
        )
    )

    return r
