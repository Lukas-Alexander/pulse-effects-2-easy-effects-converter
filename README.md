[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-0.6-blue.svg)](https://github.com/lukas-alexander/pulse-effects-2-easy-effects-converter)
[![Status](https://img.shields.io/badge/status-active-success.svg)](https://github.com/lukas-alexander/pulse-effects-2-easy-effects-converter)

# PulseEffects to EasyEffects Preset Converter

A Python script to convert old, incompatible **PulseEffects** presets into the new JSON format required by **EasyEffects (v6.0+)**. This project was created to help users migrate their preset collections after the PulseEffects format became defunct.

---

## What This Project Does

When EasyEffects was updated from PulseEffects, the preset format changed significantly. This script reads your old PulseEffects `.json` files and converts them into new, compatible `.json` files that EasyEffects can load without crashing or parsing errors.

It goes beyond simple remapping and intelligently fixes deep structural incompatibilities.

## Why This Project?

As a fan of Professor Wallace's "PulseEffects" and its successor "EasyEffects," and with over 100 effects, I thought it would be helpful to write a script to convert the now-defunct PulseEffects presets to the EasyEffects format. While my expertise lies in Enterprise Architecture, Security, and Legislative Topics, programming is more of a hobby for me. 😉

---

## Features

* **Converts Inverted Logic:** Correctly maps old `"state": "true"` to new `"bypass": false`.
* **Handles Renamed Plugins:** Correctly migrates settings from `limiter` to the new `maximizer`.
* **Fixes Out-of-Range Values:** Clamps values that were valid in PulseEffects but are out-of-range in EasyEffects (e.g., `compressor`'s `release-threshold`).
* **Corrects Data Types:** Fixes specific parameter type errors (e.g., ensures `loudness`'s `fft` value is a **string**, not a number).
* **Rebuilds Incompatible Plugins:** Completely rebuilds complex, incompatible plugins (like `multiband_compressor` and `multiband_gate`) with a valid 8-band default structure, preventing crashes while preserving your top-level gains.
* **Maps Renamed Parameters:** Correctly maps dozens of renamed parameters (e.g., `filter` `mode` to `type`/`slope`, `gate` `range` to `reduction`, `rnnoise` `model-path` to `model-name`).

---

## Why This Project Is Useful

If you, like many others, have spent years curating a collection of audio presets in PulseEffects, you may have discovered that they are all **unusable** in EasyEffects.

Without this tool, your only option would be to manually recreate every single preset—a tedious and often impossible task. This script **salvages your work** by automating the complex conversion process, saving you hours of effort and ensuring your audio setup continues to work.

---

## How to Get Started

You can get your old presets converted in just a few steps.

### 1. Prerequisites

* **Python 3** (This script is a single file and has no external dependencies).

### 2. Get the Script

You can either clone this repository:

```bash
git clone https://github.com/lukas-alexander/pulse-effects-2-easy-effects-converter.git
cd pulse-effects-2-easy-effects-converter
````

### 3. Run the Conversion

The script is designed to be run from inside your old PulseEffects preset folder.

Navigate to your old PulseEffects output presets directory (the location may vary):

```bash
cd ~/.config/PulseEffects/output/
```

Run the script on all your `.json` presets. Make sure to provide the full path to where you downloaded the `convert.py` script.

To convert all presets in the folder:

```bash
# Replace /path/to/convert.py with the actual path
python3 /path/to/convert.py *.json
```

To convert a single preset:

```bash
python3 /path/to/convert.py "My Old Preset.json"
```

The script will create new files ending in `_ee.json` (e.g., `My Old Preset_ee.json`) in the same folder.

### 4. Move Your New Presets

Move the newly converted `_ee.json` files to your EasyEffects preset directory:

```bash
mv *_ee.json ~/.config/EasyEffects/output/
```

### 5. Load EasyEffects

That's it! Open EasyEffects, and you should now see all your converted presets in the "Output" preset list, ready to use.

---

## Where to Get Help

If you find a preset that fails to convert or causes EasyEffects to crash, please open a GitHub Issue.

To help us fix the bug, please include:

* The original PulseEffects `.json` file that failed.
* The converted `_ee.json` file that the script produced.
* Any error messages printed in your terminal (either from the script or from EasyEffects when you try to load the preset).

---

## Who Maintains This Project

This project is maintained by Lukas Alexander Pruski (C) 2025.

We enthusiastically welcome contributions! Many plugins in PulseEffects had obscure parameters, and there are likely many we haven't mapped yet.

---

## How to Contribute

1. Fork the repository.
2. Create a new branch (e.g., `git checkout -b feature/add-plugin-converter`).
3. Add your fix (e.g., if you add a converter for the `speex` plugin, create a `_convert_speex` function and add it to the `PARAM_CONVERTERS` dictionary in the script).
4. Commit your changes (`git commit -m 'Add converter for speex plugin'`).
5. Push to your branch (`git push origin feature/add-plugin-converter`).
6. Open a Pull Request.

---

## How to Support This Project

If you'd like to support this project or the author, here are a few ways you can help:

* Share a link to this project on other forums or communities.
* Leave a kind comment or share the script with others.
* If you're a programming guru, contribute to the project by adding improvements or fixing bugs.

---

## Final Remarks

Not all development happens in the cozy confines of GitHub. Sometimes, there might be a sudden jump in version numbers. Like, a really sudden jump. Why? Well, picture this: I was in a cabin, completely off the grid, with only a solar-powered battery keeping my laptop alive. No Wi-Fi. No distractions. Just me, a notebook, and the sweet sounds of nature… which, by the way, don’t offer great documentation. So yeah, a few versions might have gotten lost in the wilderness. It happens! 😄
