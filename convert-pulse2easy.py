#!/usr/bin/env python3
import json
import sys
import os
import copy

"""
MIT License

Copyright          (c) 2025 Lukas-Alexander
Creator:           Lukas Alexander Pruski
License:           MIT License
GitHub Repository: https://github.com/[your-username]/pulseeffects-to-easyeffects-converter

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

=== Changelog ===

Version 0.1:   Initial release! Functionality is, lets be honest, pretty basic. It only
          renames the tagsand even that isnt error-free.
Version 0.1[a-f]: Small tweaks, minor improvements, and a few lessons learned.
Version 0.2:   Added Equalizer interpretation and fixed some tag issues. Unfortunately,
          managed to introduce a few new bugs along the way.
Version 0.2[a-d]: Bug fixes. The usual.
Version 0.3:   A real challenge. Spent hours untangling the syntax and structure
          of the new format. Modules refused to migrate to Easy Effects, but I pushed
          through! Still, ran into trouble with invalid parameters for compressors.
Version 0.4:   Found even more bugs (of course). Faced the classic developer dilemma:
          keep going or just walk away? Fixed the parameter issuesbut somehow,
          the equalization stopped working.
Version 0.4a:   Cleaned up the existing code and added missing comments for clarity.
Version 0.4b:   Added user feedback improvements to the processing flow.
Version 0.5:   Discovered Id been working with an outdated version of Easy Effects
          (oops). Turns out there have been major updates. Fixed spelling and
          grammar in the comments while recovering from the shock.
Version 0.5a:   Added licensing information.
Version 0.5b:   Redesigned the interface. Added emojis, smileys, and icons
          becauseapparentlythats how software feels friendly now.
Version 0.5c:   Tested on 120 settings with a 60% success rate. Not all settings could
          be tested. Extensive debugging logs were used to analyze and reprocess
          results.
Version 0.5d:   At this point, not sure if hope is still alive. Every fix seems
          to break something else. *Insert mild existential crisis here.*
Version 0.5e:   Running low on motivation. Easy Effects documentation is lets say,
          incomplete. Everything is trial and error now.
Version 0.5f:   Finally! It works! When specifying a preset name explicitly, the file
          processes correctly. All modules are now included, though inactive ones
          stay disabled by default.
Version 0.5g:   Discovered a major bug: batch processing deletes all original
          PulseEffects files. Thats not ideal.
Version 0.6:   Fixed the major bugs, cleaned up the code, andfinallyused proper
          indentation. Improved spelling and tested across multiple distros: Mint,

Note:       OpenSUSE, Ubuntu, Fedora, and macOS. Works great on Linux systems, but
          failed on macOS (10.15). Not sure if thats my setup or something deeper.
          If any macOS experts want to help, please reach out! Oh, andposted it
          on GitHub.
                   
Version 0.6b:  Documentation time! Its not a 900-page enterprise manual or anything,
          but as an Enterprise Security Architect, I had to practice what I preach:
          document your work. Its like flossingnobody enjoys it, but it
          prevents problems later. 
Version 0.7:   Programmatically, things were stable, but Easy Effects introduced new
          algorithms and rewritten internals. That meant lots of readjustmentsmany
          presets sounded distorted or overpowered. Rewrote the EQ processing from
          scratch and added CLI parameters for volume control.
Version 0.8:   Big update! Now you can select which parts of an old settings file to
          migrateEQ, compressor, or specific plugin sets. Fixed countless bugs
          (and discovered just as many).
Version 0.9:   Volume handling in Easy Effects is challenging.
          From an architectural standpoint (PipeWire vs PulseAudio), it makes sense,
          but from a users point of viewits painful.
Version 0.9a:   Added more comments for future reference.
Version 0.9b:   Called for help from AI tools. Hello Claude, Mutable, ChatGPT, and
          Gemini. Fingers crossed.
Version 0.9c:   AI agents helped build proper test setups and evaluate results.
          Their solutions were not impressive, but at least we learned something.
Version 1.0:   Breakthrough! With help from human programmers and Linux audiophiles,

                   --- Decided to share with Github :-) ---

Version 1.0a:   Tested 500 presetseverything worked well! Easy Effects sometimes
          processes things differently, so some presets sounded meh, but small
          tweaks fixed them all.
Version 1.0b:   Final refinements based on my own testing and experience.
Version 1.1:   Code shared with the world
"""

import json
import sys
import os
import copy
import argparse  # Used for command-line arguments


def convert_value(v):
    """
    Recursively convert string values ("true", "false", "1.0")
    from the old preset format to native Python types.
    """
    if isinstance(v, str):
        v_low = v.lower()
        if v_low == "true":
            return True
        if v_low == "false":
            return False
        try:
            # Check for '.' or 'e' to decide float vs int
            if "." in v or "e" in v.lower():
                return float(v)
            else:
                return int(v)
        except ValueError:
            return v  # Keep as string if it's not a number (e.g., "RMS")
    elif isinstance(v, list):
        return [convert_value(i) for i in v]
    elif isinstance(v, dict):
        return {k: convert_value(val) for k, val in v.items()}
    return v


# Helper function to fix float type errors
def _ensure_floats(data, keys):
    """Ensures all keys in the list are floats, if they exist."""
    for key in keys:
        if key in data:
            try:
                data[key] = float(data[key])
            except (ValueError, TypeError):
                if not isinstance(data[key], (float, int)):
                    print(f"        Could not convert {key}: {data[key]} to float.")
    return data


# MODIFIED: Now only ensures floats. Headroom logic is centralized
# in the main conversion function.
def _add_headroom_and_floats(data, args, float_keys=None):
    """
    Ensures specified keys are floats.
    Gain logic is no longer handled here.
    """
    if float_keys:
        data = _ensure_floats(data, float_keys)

    # We still set default 0.0dB gains, which will be
    # overwritten by the new "force-set" logic if needed.
    data.setdefault("input-gain", 0.0)
    data.setdefault("output-gain", 0.0)
    return data


# NEW: List of all known gain/level keys to reset for --volume-reset
GAIN_KEYS_TO_RESET = {
    # This list is intentionally small to avoid resetting
    # mix levels (wet/dry) or effect amounts (intensity).
    "input-gain",
    "output-gain",
    "gain",
    "makeup",
    "ir-gain",
}


# NEW: Recursive function for --volume-reset
def _recursive_reset_gains(data, value):
    """
    Recursively traverses a dict/list and overwrites any key
    from GAIN_KEYS_TO_RESET with the new value.
    """
    if isinstance(data, dict):
        for key, val in data.items():
            if key in GAIN_KEYS_TO_RESET:
                data[key] = value
            else:
                # Recurse into nested objects
                data[key] = _recursive_reset_gains(val, value)
    elif isinstance(data, list):
        # Recurse into lists
        return [_recursive_reset_gains(item, value) for item in data]

    return data


# --- Special Converters for Incompatible Parameters ---
# All converters now accept 'args'


# NEW: updated logic
def _convert_autogain(data, args):
    """
    Converts old autogain parameters.
    """
    if data.pop("use-geometric-mean", False):
        data["reference"] = "Geometric Mean (MSI)"
    else:
        data["reference"] = "RMS"  # Default fallback

    [data.pop(k, None) for k in ["detect-silence", "weight-m", "weight-s", "weight-i"]]

    float_keys = [
        "input-gain",
        "output-gain",
        "maximum-history",
        "silence-threshold",
        "target",
    ]
    data = _ensure_floats(data, float_keys)
    # Autogain manages its own level, so we don't use _add_headroom
    data.setdefault("input-gain", 0.0)
    data.setdefault("output-gain", 0.0)
    return data


def _convert_maximizer(data, args):
    """
    Converts old 'limiter' OR 'maximizer' plugins to the new 'maximizer'.
    """
    if "limit" in data:
        data["threshold"] = data.pop("limit")
        [
            data.pop(k, None)
            for k in ["lookahead", "auto-level", "asc", "asc-level", "oversampling"]
        ]

    if "ceiling" in data:
        data["output-gain"] = data.pop("ceiling")

    float_keys = ["threshold", "output-gain", "release", "input-gain"]
    data = _ensure_floats(data, float_keys)
    # Maximizer should not get headroom
    data.setdefault("input-gain", 0.0)
    data.setdefault("output-gain", 0.0)
    return data


def _convert_loudness(data, args):
    """
    Converts old loudness parameters.
    """
    if "input" in data:
        data["input-gain"] = data.pop("input")

    if "fft" in data:
        data["fft"] = str(data["fft"])

    float_keys = [
        "input-gain",
        "link-gain",
        "makeup-gain",
        "output-gain",
        "volume",
        "clipping-range",
    ]
    data = _ensure_floats(data, float_keys)
    # Loudness manages its own level
    data.setdefault("input-gain", 0.0)
    data.setdefault("output-gain", 0.0)
    return data


def _convert_compressor(data, args):
    """
    Converts old compressor parameters and builds a new valid sidechain.
    """
    if data.get("release-threshold", 0) < -100.0:
        data["release-threshold"] = -100.0
        print(f"        Clamped compressor 'release-threshold' to -100.0 dB.")

    float_keys = [
        "attack",
        "release",
        "ratio",
        "threshold",
        "knee",
        "makeup",
        "release-threshold",
        "dry",
        "wet",
        "boost-amount",
        "boost-threshold",
        "hpf-frequency",
        "lpf-frequency",
    ]
    data = _add_headroom_and_floats(data, args, float_keys)

    # Rebuild the sidechain structure completely
    detection_mode = data.pop("detection", "RMS")
    data.pop("sidechain", None)

    lookahead = data.pop("lookahead", 0.0)
    preamp = data.pop("preamp", 0.0)
    reactivity = data.pop("reactivity", 10.0)

    data["sidechain"] = {
        "lookahead": float(lookahead),
        "mode": detection_mode,
        "preamp": float(preamp),
        "reactivity": float(reactivity),
        "source": "Middle",
        "stereo-split-source": "Left/Right",
        "type": "Feed-forward",
    }

    # Add other missing top-level keys
    data.setdefault("dry", -100.0)
    data.setdefault("wet", 0.0)
    data.setdefault("mode", "Downward")
    data.setdefault("boost-amount", 0.0)
    data.setdefault("boost-threshold", -72.0)
    data.setdefault("hpf-mode", "off")
    data.setdefault("hpf-frequency", 10.0)
    data.setdefault("lpf-mode", "off")
    data.setdefault("lpf-frequency", 20000.0)
    data.setdefault("stereo-split", False)

    return data


def _convert_filter(data, args):
    """
    Remaps old filter 'mode' to new 'type' and 'slope'.
    """
    old_mode = data.pop("mode", "12dB/oct Lowpass")

    # Map Type
    if "Lowpass" in old_mode:
        data["type"] = "Low-pass"
    elif "Highpass" in old_mode:
        data["type"] = "High-pass"
    elif "Bandpass" in old_mode:
        data["type"] = "Band-pass"
    elif "Notch" in old_mode:
        data["type"] = "Notch"
    else:
        data["type"] = "Low-pass"  # Safe default

    # Map Slope
    if "6dB" in old_mode:
        data["slope"] = "x1"
    elif "12dB" in old_mode:
        data["slope"] = "x2"
    elif "24dB" in old_mode:
        data["slope"] = "x4"
    elif "48dB" in old_mode:
        data["slope"] = "x8"
    else:
        data["slope"] = "x2"  # Default for old "Lowpass"

    if "resonance" in data:
        data["quality"] = data.pop("resonance")

    data.pop("inertia", None)
    data["mode"] = "RLC (BT)"  # Set new default filter mode

    float_keys = ["frequency", "gain", "quality", "balance", "width"]
    data = _add_headroom_and_floats(data, args, float_keys)

    data.setdefault("gain", 0.0)
    data.setdefault("balance", 0.0)
    data.setdefault("width", 4.0)
    data.setdefault("frequency", 1000.0)
    return data


def _convert_gate(data, args):
    """
    Remaps old 'gate' parameters to the new structure.
    """
    if "range" in data:
        data["reduction"] = data.pop("range")
    if "threshold" in data:
        data["curve-threshold"] = data.pop("threshold")
    if "knee" in data:
        data["curve-zone"] = data.pop("knee")

    float_keys = [
        "attack",
        "hold",
        "release",
        "reduction",
        "curve-threshold",
        "curve-zone",
        "dry",
        "wet",
        "makeup",
        "hysteresis-threshold",
        "hysteresis-zone",
    ]
    data = _add_headroom_and_floats(data, args, float_keys)

    detection_mode = data.pop("detection", "RMS")
    data.pop("stereo-link", None)

    data["sidechain"] = {
        "input": "Internal",
        "lookahead": 0.0,
        "mode": detection_mode,
        "preamp": 0.0,
        "reactivity": 10.0,
        "source": "Middle",
        "stereo-split-source": "Left/Right",
    }

    data.setdefault("dry", -100.0)
    data.setdefault("wet", 0.0)
    data.setdefault("makeup", 0.0)
    data.setdefault("hysteresis", False)
    data.setdefault("hpf-mode", "off")
    data.setdefault("lpf-mode", "off")

    return data


def _convert_convolver(data, args):
    """
    Maps old 'kernel-path' to new 'kernel-name'.
    """
    if "kernel-path" in data:
        data["kernel-name"] = data.pop("kernel-path")

    float_keys = ["gain", "wet", "ir-gain"]
    # Convolver has autogain, so we don't add headroom
    data = _ensure_floats(data, float_keys)

    data.setdefault("autogain", True)
    data.setdefault("gain", 0.0)
    data.setdefault("wet", 100.0)
    data.setdefault("ir-gain", 0.0)
    data.setdefault("input-gain", 0.0)
    data.setdefault("output-gain", 0.0)
    return data


def _convert_crystalizer(data, args):
    """
    Removes obsolete 'aggressive' parameter.
    """
    data.pop("aggressive", None)

    float_keys = ["intensity"]
    data = _add_headroom_and_floats(data, args, float_keys)

    if "intensity" in data:
        print(
            f"        Plugin 'crystalizer' is now multiband. Migrating 'intensity' to band0."
        )
        data["band0"] = {
            "bypass": False,
            "intensity": data.pop("intensity"),
            "mute": False,
        }

    return data


def _convert_pitch(data, args):
    """
    Removes obsolete pitch parameters.
    """
    data.pop("crispness", None)
    data.pop("formant-preserving", None)

    float_keys = [
        "pitch",
        "semitones",
        "rate-difference",
        "tempo-difference",
        "cents",
        "octaves",
    ]
    data = _add_headroom_and_floats(data, args, float_keys)

    data.setdefault("anti-alias", False)
    data.setdefault("overlap-length", 8)
    data.setdefault("quick-seek", True)
    data.setdefault("rate-difference", 0.0)
    data.setdefault("seek-window", 15)
    data.setdefault("sequence-length", 40)
    data.setdefault("tempo-difference", 0.0)
    data.setdefault("pitch", 1.0)
    data.setdefault("semitones", 0.0)
    data.setdefault("cents", 0.0)
    data.setdefault("octaves", 0.0)
    return data


def _convert_rnnoise(data, args):
    """
    Maps old 'model-path' to new 'model-name'.
    """
    if "model-path" in data:
        data["model-name"] = data.pop("model-path")
    if data.get("model-name") == "Standard RNNoise Model":
        data["model-name"] = ""

    float_keys = ["release", "vad-thres", "wet"]
    data = _add_headroom_and_floats(data, args, float_keys)

    data.setdefault("enable-vad", False)
    data.setdefault("release", 20.0)
    data.setdefault("vad-thres", 50.0)
    data.setdefault("wet", 0.0)
    return data


# --- Multiband Functions (structure confirmed OK) ---

DEFAULT_MC_BAND = {
    "attack-threshold": -12.0,
    "attack-time": 20.0,
    "boost-amount": 6.0,
    "boost-threshold": -72.0,
    "compression-mode": "Downward",
    "compressor-enable": True,
    "external-sidechain": False,
    "knee": -6.0,
    "makeup": 0.0,
    "mute": False,
    "ratio": 1.0,
    "release-threshold": -100.0,
    "release-time": 100.0,
    "sidechain-custom-highcut-filter": False,
    "sidechain-custom-lowcut-filter": False,
    "sidechain-highcut-frequency": 20000.0,
    "sidechain-lookahead": 0.0,
    "sidechain-lowcut-frequency": 10.0,
    "sidechain-mode": "RMS",
    "sidechain-preamp": 0.0,
    "sidechain-reactivity": 10.0,
    "sidechain-source": "Middle",
    "solo": False,
    "stereo-split-source": "Left/Right",
}
MC_SPLIT_FREQS = [500.0, 1000.0, 2000.0, 4000.0, 8000.0, 12000.0, 16000.0]
MC_SIDECHAIN_FREQS = [
    (10.0, 500.0),
    (500.0, 1000.0),
    (1000.0, 2000.0),
    (2000.0, 4000.0),
    (4000.0, 8000.0),
    (8000.0, 12000.0),
    (12000.0, 16000.0),
    (16000.0, 20000.0),
]


def _convert_multiband_compressor(data, args):
    """
    Resets the multiband compressor to a valid 8-band default structure.
    """
    print(
        f"        Plugin 'multiband_compressor' is incompatible; resetting bands to a valid default."
    )

    [
        data.pop(k, None)
        for k in [
            "freq0",
            "freq1",
            "freq2",
            "mode",
            "subband",
            "lowband",
            "midband",
            "highband",
        ]
    ]

    band0 = copy.deepcopy(DEFAULT_MC_BAND)
    band0["sidechain-lowcut-frequency"] = MC_SIDECHAIN_FREQS[0][0]
    band0["sidechain-highcut-frequency"] = MC_SIDECHAIN_FREQS[0][1]
    band0["enable-band"] = True
    data["band0"] = band0

    for i in range(1, 8):
        band = copy.deepcopy(DEFAULT_MC_BAND)
        band["split-frequency"] = MC_SPLIT_FREQS[i - 1]
        band["sidechain-lowcut-frequency"] = MC_SIDECHAIN_FREQS[i][0]
        band["sidechain-highcut-frequency"] = MC_SIDECHAIN_FREQS[i][1]
        band["enable-band"] = i < 4
        data[f"band{i}"] = band

    data = _add_headroom_and_floats(data, args, ["dry", "wet"])
    data.setdefault("compressor-mode", "Modern")
    data.setdefault("dry", -100.0)
    data.setdefault("envelope-boost", "None")
    data.setdefault("stereo-split", False)
    data.setdefault("wet", 0.0)
    return data


DEFAULT_MG_BAND = {
    "attack-time": 20.0,
    "curve-threshold": -24.0,
    "curve-zone": -6.0,
    "external-sidechain": False,
    "gate-enable": True,
    "hysteresis": False,
    "hysteresis-threshold": -12.0,
    "hysteresis-zone": -6.0,
    "makeup": 0.0,
    "mute": False,
    "reduction": -24.0,
    "release-time": 100.0,
    "sidechain-custom-highcut-filter": False,
    "sidechain-custom-lowcut-filter": False,
    "sidechain-highcut-frequency": 20000.0,
    "sidechain-lookahead": 0.0,
    "sidechain-lowcut-frequency": 10.0,
    "sidechain-mode": "RMS",
    "sidechain-preamp": 0.0,
    "sidechain-reactivity": 10.0,
    "sidechain-source": "Middle",
    "solo": False,
    "stereo-split-source": "Left/Right",
}


def _convert_multiband_gate(data, args):
    """
    Resets the multiband gate to a valid 8-band default structure.
    """
    print(
        f"        Plugin 'multiband_gate' is incompatible; resetting bands to a valid default."
    )

    [
        data.pop(k, None)
        for k in [
            "freq0",
            "freq1",
            "freq2",
            "mode",
            "subband",
            "lowband",
            "midband",
            "highband",
        ]
    ]

    band0 = copy.deepcopy(DEFAULT_MG_BAND)
    band0["sidechain-lowcut-frequency"] = MC_SIDECHAIN_FREQS[0][0]
    band0["sidechain-highcut-frequency"] = MC_SIDECHAIN_FREQS[0][1]
    band0["enable-band"] = True
    data["band0"] = band0

    for i in range(1, 8):
        band = copy.deepcopy(DEFAULT_MG_BAND)
        band["split-frequency"] = MC_SPLIT_FREQS[i - 1]
        band["sidechain-lowcut-frequency"] = MC_SIDECHAIN_FREQS[i][0]
        band["sidechain-highcut-frequency"] = MC_SIDECHAIN_FREQS[i][1]
        band["enable-band"] = i < 4
        data[f"band{i}"] = band

    data = _add_headroom_and_floats(data, args, ["dry", "wet"])
    data.setdefault("gate-mode", "Modern")
    data.setdefault("dry", -100.0)
    data.setdefault("envelope-boost", "None")
    data.setdefault("stereo-split", False)
    data.setdefault("wet", 0.0)
    return data


# --- Simple Converters (for headroom) ---


def _convert_equalizer(data, args):
    """
    Adds headroom and ensures all band parameters are floats.
    """
    if "left" in data:
        for band in data["left"].values():
            _ensure_floats(band, ["frequency", "gain", "q", "width"])
    if "right" in data:
        for band in data["right"].values():
            _ensure_floats(band, ["frequency", "gain", "q", "width"])

    data = _add_headroom_and_floats(data, args, ["balance"])
    data.setdefault("balance", 0.0)
    return data


def _convert_bass_enhancer(data, args):
    float_keys = ["amount", "blend", "floor", "harmonics", "scope"]
    return _add_headroom_and_floats(data, args, float_keys)


def _convert_exciter(data, args):
    float_keys = ["amount", "blend", "ceil", "harmonics", "scope"]
    return _add_headroom_and_floats(data, args, float_keys)


def _convert_reverb(data, args):
    float_keys = [
        "amount",
        "bass-cut",
        "decay-time",
        "diffusion",
        "dry",
        "hf-damp",
        "predelay",
        "treble-cut",
    ]
    return _add_headroom_and_floats(data, args, float_keys)


def _convert_stereo_tools(data, args):
    float_keys = [
        "balance-in",
        "balance-out",
        "delay",
        "middle-level",
        "middle-panorama",
        "sc-level",
        "side-balance",
        "side-level",
        "stereo-base",
        "stereo-phase",
    ]
    return _add_headroom_and_floats(data, args, float_keys)


def _convert_crossfeed(data, args):
    float_keys = ["feed"]
    return _add_headroom_and_floats(data, args, float_keys)


def _convert_deesser(data, args):
    float_keys = [
        "f1-freq",
        "f1-level",
        "f2-freq",
        "f2-level",
        "f2-q",
        "makeup",
        "ratio",
        "threshold",
    ]
    return _add_headroom_and_floats(data, args, float_keys)


def _convert_delay(data, args):
    float_keys = ["dry-l", "dry-r", "time-l", "time-r", "wet-l", "wet-r"]
    return _add_headroom_and_floats(data, args, float_keys)


# --- Mappings ---

# Map old plugin names to their new names
PLUGIN_NAME_MAP = {"limiter": "maximizer"}

# Map new plugin names to their special conversion functions
PARAM_CONVERTERS = {
    # Special structural converters
    "autogain": _convert_autogain,
    "maximizer": _convert_maximizer,  # Handles old 'limiter' and old 'maximizer'
    "loudness": _convert_loudness,
    "compressor": _convert_compressor,
    "multiband_compressor": _convert_multiband_compressor,  # Rebuilds
    "filter": _convert_filter,
    "gate": _convert_gate,
    "multiband_gate": _convert_multiband_gate,  # Rebuilds
    "convolver": _convert_convolver,
    "crystalizer": _convert_crystalizer,
    "pitch": _convert_pitch,
    "rnnoise": _convert_rnnoise,
    # Headroom-adding converters
    "equalizer": _convert_equalizer,
    "bass_enhancer": _convert_bass_enhancer,
    "exciter": _convert_exciter,
    "reverb": _convert_reverb,
    "stereo_tools": _convert_stereo_tools,
    "crossfeed": _convert_crossfeed,
    "deesser": _convert_deesser,
    "delay": _convert_delay,
}


# Helper function for --selected
def _prompt_for_plugins(plugin_list):
    """
    Shows an interactive menu for the user to select plugins.
    Returns a set of plugins to convert.
    """
    print("---  interactive Plugin Selection ---")
    print("The following plugins were found in the preset:")
    for i, name in enumerate(plugin_list):
        print(f"  [{i + 1}] {name}")
    print("\nPlease enter the numbers of the plugins you wish to convert.")
    print("Example: 1, 3, 4\n")

    selected_plugins = set()
    while True:
        try:
            choice = input("Plugins to convert (or 'a' for all, 'q' to quit): ")
            choice_low = choice.lower()

            if not choice:
                continue
            if choice_low == "q":
                return None  # Signal to quit
            if choice_low == "a":
                return set(plugin_list)  # Convert all

            indices = [int(i.strip()) for i in choice.split(",")]

            valid_indices = set()
            invalid_found = False
            for i in indices:
                if 1 <= i <= len(plugin_list):
                    valid_indices.add(i - 1)
                else:
                    print(f" Invalid number: {i}")
                    invalid_found = True

            if invalid_found:
                continue

            selected_plugins = {plugin_list[i] for i in valid_indices}
            print("\nSelected to convert:")
            for name in selected_plugins:
                print(f"  - {name}")
            print("---")
            return selected_plugins

        except ValueError:
            print(
                f" Invalid input. Please enter numbers separated by commas (e.g., 1, 3)."
            )
        except Exception as e:
            print(f" An error occurred: {e}")


# --- Main Conversion Function ---


def convert_pulseeffects_to_easyeffects(pulse_data, args):
    """
    Main conversion function.
    Converts a PulseEffects preset dict to an EasyEffects preset dict.
    Applies filtering and headroom based on 'args'.
    """
    ee_data = {"output": {"blocklist": [], "plugins_order": []}}

    pe_output = pulse_data.get("output", {})
    if not pe_output:
        print(" No 'output' section found in source file.")
        return None

    all_plugins = pe_output.get("plugins_order", [])
    plugins_to_process = set(all_plugins)

    # Handle --selected
    if args.selected:
        selected = _prompt_for_plugins(all_plugins)
        if selected is None:  # User quit
            print("Operation cancelled.")
            return "CANCELLED"
        plugins_to_process = selected

    print(f"\nProcessing preset...")

    for plugin_name in all_plugins:
        pe_plugin_data = pe_output.get(plugin_name)

        # Get the new plugin name (e.g., "limiter" -> "maximizer")
        final_plugin_name = PLUGIN_NAME_MAP.get(plugin_name, plugin_name)

        # --- Filtering Logic ---
        if plugin_name not in plugins_to_process:  # From --selected
            print(f"        Skipping '{plugin_name}' (not selected).")
            continue
        if args.eq_only and final_plugin_name != "equalizer":
            print(f"        Skipping '{plugin_name}' (--eq-only).")
            continue
        if args.no_eq and final_plugin_name == "equalizer":
            print(f"        Skipping 'equalizer' (--no-eq).")
            continue
        # --- End Filtering Logic ---

        if not pe_plugin_data:
            print(f"        Missing plugin data for '{plugin_name}', skipping.")
            continue

        # Convert all string values ("true", "1.0") to native types
        ee_plugin_data = convert_value(copy.deepcopy(pe_plugin_data))

        # Handle "state" (old) -> "bypass" (new)
        state = ee_plugin_data.pop("state", True)
        ee_plugin_data["bypass"] = not state

        # Run special parameter converters if one exists
        if final_plugin_name in PARAM_CONVERTERS:
            ee_plugin_data = PARAM_CONVERTERS[final_plugin_name](ee_plugin_data, args)

        # For plugins without converters, still ensure floats and default gains
        elif final_plugin_name not in [
            "level_meter",
            "speex",
            "echo_canceller",
            "deepfilternet",
        ]:
            ee_plugin_data = _add_headroom_and_floats(ee_plugin_data, args)

        # --- NEW: Centralized Gain Forcing Logic ---
        # This block now handles ALL volume modes and replaces the old headroom logic.

        FORCE_SET_DB_MAP = {
            "headroom_0": 0.0,
            "headroom_3": -3.0,
            "headroom_6": -6.0,
            "reset_9": -9.0,
        }

        # Check if the current volume mode is one we need to force-set
        if args.volume_mode in FORCE_SET_DB_MAP:
            target_db = FORCE_SET_DB_MAP[args.volume_mode]
            if args.volume_mode == "reset_9":
                print(
                    f"        Resetting all gain levels in '{final_plugin_name}' to -9.0dB."
                )
            else:
                print(
                    f"        Forcing all gain levels in '{final_plugin_name}' to {target_db}dB."
                )

            # --- FIX: Preserve EQ band gains during reset ---
            eq_bands_to_restore = None
            if final_plugin_name == "equalizer":
                # Save a deep copy of the 'left' and 'right' band containers
                # We need deepcopy because _recursive_reset_gains modifies in-place
                eq_bands_to_restore = (
                    copy.deepcopy(ee_plugin_data.get("left")),
                    copy.deepcopy(ee_plugin_data.get("right")),
                )
            # --- End FIX ---

            # Run the reset, using the dynamically-fetched target_db
            ee_plugin_data = _recursive_reset_gains(ee_plugin_data, target_db)

            # --- FIX: Restore EQ band gains ---
            if eq_bands_to_restore:
                print("        Restoring EQ band settings (not resetting band gains).")
                # Now, restore the saved bands, overwriting the reset ones.
                if eq_bands_to_restore[0]:
                    ee_plugin_data["left"] = eq_bands_to_restore[0]
                if eq_bands_to_restore[1]:
                    ee_plugin_data["right"] = eq_bands_to_restore[1]
            # --- End FIX ---
        # --- END: Centralized Gain Forcing Logic ---

        # Add the required '#0' index
        final_name_indexed = f"{final_plugin_name}#0"

        # Assign the plugin data dict to the new key
        ee_data["output"][final_name_indexed] = ee_plugin_data
        ee_data["output"]["plugins_order"].append(final_name_indexed)
        print(f"       Converted {plugin_name} -> {final_name_indexed}")

    # Handle case where filtering resulted in an empty preset
    if not ee_data["output"]["plugins_order"]:
        print("\n No plugins were converted based on your filter selection.")
        return None

    return ee_data


def main():
    """
    Main entry point. Parses command-line arguments and runs conversion.
    """
    parser = argparse.ArgumentParser(
        description="""Convert PulseEffects (PE) legacy presets to EasyEffects (EE) v7+ format.
This script correctly handles gain staging, type conversion, and incompatible
plugins (like multiband_compressor) by rebuilding them.

Find the latest version at:
https://github.com/Lukas-Alexander/pulse-effects-2-easy-effects-converter
""",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "input_files",
        metavar="input.json",
        type=str,
        nargs="*",  # MODIFIED: Changed to '*' to allow no args
        help="One or more PE preset .json file(s) to convert.",
    )

    # --- Volume/Headroom Group ---
    volume_group = parser.add_mutually_exclusive_group()
    volume_group.add_argument(
        "--volume-0db",
        dest="volume_mode",
        action="store_const",
        const="headroom_0",
        help="Force ALL gain/level sliders to 0.0dB (neutral volume).",
    )
    volume_group.add_argument(
        "--volume-3db",
        dest="volume_mode",
        action="store_const",
        const="headroom_3",
        help="Force ALL gain/level sliders to -3.0dB (default).",
    )
    volume_group.add_argument(
        "--volume-6db",
        dest="volume_mode",
        action="store_const",
        const="headroom_6",
        help="Force ALL gain/level sliders to -6.0dB (conservative).",
    )
    # NEW: Added --volume-reset
    volume_group.add_argument(
        "--volume-reset",
        dest="volume_mode",
        action="store_const",
        const="reset_9",
        help="""Force ALL gain/level sliders to -9.0dB (safe mode).
This is the safest option for complex presets.
You WILL need to manually adjust volumes after loading.""",
    )

    # --- Plugin Filtering Group ---
    filter_group = parser.add_mutually_exclusive_group()
    filter_group.add_argument(
        "--eq-only",
        action="store_true",
        help='Only convert the "equalizer" plugin and skip all others.',
    )
    filter_group.add_argument(
        "--no-eq", action="store_true", help='Convert all plugins *except* "equalizer".'
    )
    filter_group.add_argument(
        "--selected",
        action="store_true",
        help="Show an interactive menu to select which plugins to convert.",
    )

    parser.set_defaults(volume_mode="headroom_3")  # Default to -3.0dB if no flag is set

    args = parser.parse_args()

    # NEW: Handle no arguments
    if not args.input_files:
        parser.print_help(sys.stderr)
        sys.exit(1)

    for input_file in args.input_files:
        if not input_file.endswith(".json"):
            print(f"Skipping non-JSON file: {input_file}")
            continue

        print(f"--- Converting: {input_file} ---")
        try:
            with open(input_file, "r", encoding="utf-8") as f:
                pulse_data = json.load(f)

            converted_data = convert_pulseeffects_to_easyeffects(pulse_data, args)

            if converted_data is None:  # Skipped due to filters
                print(f"        No preset file written for {input_file}.\n")
                continue
            if converted_data == "CANCELLED":  # User quit interactive prompt
                break

            # Create a safe output filename
            base_name = os.path.splitext(input_file)[0]
            if base_name.endswith("_ee"):
                base_name = base_name[:-3]
            output_file = f"{base_name}_ee.json"

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(converted_data, f, indent=4)

            print(f"        Converted preset saved as: {output_file}\n")

        except json.JSONDecodeError:
            print(f" Error: Failed to decode JSON from {input_file}. Is it valid?")
        except Exception as e:
            print(f" An unexpected error occurred for {input_file}: {e}")
            import traceback

            traceback.print_exc()

    print("Done.")

    # NEW: Add final message for all volume-forcing modes
    if args.volume_mode in ["headroom_0", "headroom_3", "headroom_6", "reset_9"]:
        FORCE_SET_DB_MAP = {
            "headroom_0": "0.0dB",
            "headroom_3": "-3.0dB",
            "headroom_6": "-6.0dB",
            "reset_9": "-9.0dB",
        }
        db_val = FORCE_SET_DB_MAP[args.volume_mode]
        print("\n---   IMPORTANT ---")
        print(
            f"You used a volume-forcing mode. All gain levels have been set to {db_val}."
        )

        if args.volume_mode == "reset_9":
            print("You will need to manually adjust the plugin volumes in EasyEffects.")
        elif args.volume_mode == "headroom_0":
            print("Your preset should have a neutral volume level.")
        else:
            print("This preset has built-in headroom.")


if __name__ == "__main__":
    main()
