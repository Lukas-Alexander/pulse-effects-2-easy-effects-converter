#!/usr/bin/env python3
import json
import sys
import os
import copy

# --- Project Information ---
#
# Project: PulseEffects to EasyEffects Preset Converter
# Author: Lukas Alexander Pruski
# License: MIT License
# GitHub Repository: https://github.com/[your-username]/pulseeffects-to-easyeffects-converter
# Copyright (c) 2025 Lukas Pruski. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

### Changelog ###


### Changelog ###

# Version 0.1:       Initial release. Functionality is, frankly, a bit underwhelming: it only
#                    renames the tags—though not error-free.
# Version 0.1[a-f]:  Various tweaks and adjustments.
# Version 0.2:       Added Equalizer interpretation and fixed some tags, but alas, introduced
#                    new bugs.
# Version 0.2[a-d]:  Bug fixes.
# Version 0.3:       A nightmare. Spent hours trying to figure out the syntax and topology
#                    of the new format. Modules weren't ported to Easy Effects... but I pushed through!
#                    Still, encountered issues with invalid parameters for compressors.
# Version 0.4:       More bugs discovered (sigh). The existential question: to continue, or
#                    not to continue? Resolved the parameters issue, but somehow the equalization
#                    processing broke.
# Version 0.4a:      Cleaned up existing code and added missing comments.
# Version 0.4b:      Incorporated script user feedback regarding processing.
# Version 0.5:       Realised I'd been working with an old version of Easy Effects: oops! It's
#                    clear there have been updates. Fixed some grammar and spelling in comments.
# Version 0.5a:      Added licensing information.
# Version 0.5b:      Revamped the user interface. Emojis, smileys, and icons seem to be
#                    the way forward, so I added them to the user feedback section.
# Version 0.5c:      Tested on 120 settings; 60% success rate, though not all settings could
#                    be tested. Used extensive debugging logs to analyze and reprocess.
# Version 0.5d:      Is there hope left? Honestly, I don't know anymore... What am I doing
#                    wrong? The "fixes" seem to have introduced even more bugs. *Cue existential crisis*.
# Version 0.5e:      Nearing the end of my rope—help! This project is draining me. As great
#                    as the app is, Easy Effects' documentation is lacking in key areas. It's all been
#                    trial and error. :-(
# Version 0.5f:      EUREKA! It works! When specifying an explicit preset name, the file
#                    is processed correctly. It’s working, so I decided to include all modules but disable
#                    the inactive ones.
# Version 0.5g:      Major bug found: batch processing now deletes every original pulse
#                    effects file.
#
#                    --- We decided to share with Github :-) ---
#
# Version 0.6:       Fixed the bugs, cleaned up the code, and—wait for it—finally used proper
#                    indentation. Improved spelling, and tested across Mint, OpenSUSE, Ubuntu, Fedora, and
#                    macOS. It works on all Linux versions, but for some reason, it failed on my macOS (10.15)
#                    install. Not sure if it's my personal machine or if there's a deeper issue. Any macOS
#                    wizards out there want to help make this bulletproof? And ... Last but not least: posted
#                    it on Github.
#
# Version 0.6:       Documentation! Oh, joy. Look, it's not some 900-page SAP monstrosity
#                    or the Autocad manual that could double as a doorstop. But hey, as an Enterprise
#                    Security Architect, I *had* to practice what I preach: document your solution.
#                    It's like flossing your teeth—nobody wants to do it, but deep down, you know
#                    it's probably for the best. 😏

### Current State of Development
# - Script to be presented here: Either October 29th, or 30th, 2025
