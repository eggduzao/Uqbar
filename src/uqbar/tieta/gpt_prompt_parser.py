# SPDX-License-Identifier: MIT
# uqbar/acta/gpt_prompt_parser.py
"""
Tieta | GPT Prompt Parser
=========================

Overview
--------
Placeholder.

Metadata
--------
- Project: Tieta
- License: MIT
"""

# -------------------------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------------------------
from __future__ import annotations

from pathlib import Path

# -------------------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------------------
def _get_prompt_string(
    input_path: Path,
) -> str:

    fname = input_path.name
    prompt_string: str = (
        f"1. Goal: Read the text file attached ({fname}) and look - smartly - "
        f"for any sign of `INTERESTING CONTENT` (defined below).\n"
        f"\n"
        f"2. Return the interesting contents - if any - as a list of Major Topic "
        f"| Subtopic. For example:\n"
        f"  - Python | Type Hint\n"
        f"  - Sublime App | Custom Themes\n"
        f"  - Pharmacology | Medicament Terminology\n"
        f"\n"
        f"A. **Definition of `INTERESTING CONTENT`:**\n"
        f"  - Each file corresponds to a long chain of logged conversations with you"
        f".\n"
        f"  - `INTERESTING CONTENT` can be small or large chunks of our conversation "
        f"in which you explicitly TAUGHT something to me (knowledge is being trans "
        f"mitted.\n"
        f"\n"
        f"B. **Range of Topics:** UNLIMITED. But special focus shall be placed in "
        f"content from the following **BROAD** areas of knowledge:\n"
        f"  - Computer Science: Data Science, Machine Learning, etc.\n"
        f"  - Computer Software: MAC/Linux/OS, Apps, Technologies, Tech Misc., etc"
        f".\n"
        f"  - Programming: Python, R, C/C++, Project Structures, Engineering, etc.\n"
        f"  - Biology: Molecular & Cellular Biology, Wet Lab, Bioinformatics, etc.\n"
        f"  - Medicine: Pathology, Physiology, Pharmacology, Immunology, etc.\n"
        f"  - Omics: Genomics, Epigenomics, Transcriptomics, Proteomics, etc.\n"
        f"  - Bioinformatics: Tools and Methods, Didactics, Materials, DBs & APIs, "
        f"etc.\n"
        f"  - Books and Learning: Pay attention if a book is 'lonely' mentioned, etc"
        f".\n"
        f"  - Industry: CV-optimization, Industry Mentality, Job Search, etc.\n"
        f"  - Arts: Writing, Painting, Music, Acting, Education, etc.\n"
        f"\n"
        f"C. **Summary of `INTERESTING CONTENT`:** All that 'looks like you are "
        f"teaching me' OR 'all that' feels like I am learning'.\n"
        f"\n"
        f"D. **TRIMMING RULES:**\n"
        f"  - Do NOT invent, infer, generalize, or name meta-concepts, pedagogical "
        f"patterns, frameworks, or systems. If a concept name does not explicitly "
        f"appear in the text as a taught idea, it must NOT appear in the output.\n"
        f"  - Only list topics that would still make sense if removed from my "
        f"personal workflow, naming conventions, blog structure, or project "
        f"organization.\n"
        f"  - A topic qualifies ONLY if I explicitly explained, defined, contrasted, "
        f"or corrected something (e.g. “X vs Y”, “why not Z”, “how A works”). "
        f"Mentions, planning, naming, or stylistic discussion do NOT qualify.\n"
        f"teaching"
        f"  - A typical return ranges from 0 to 15 topics. Return at most 20 "
        f"items. Prefer omission over inclusion. If unsure, discard.\n"
        f"  - Each listed topic must correspond to a moment where a reader could "
        f"point to a paragraph and say: ‘here I learned something concrete.’"
    )

    return prompt_string

        

        

        

         




# --------------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------------
def create_multiprompt_list(
    input_path_list: list[Path] | None,
) -> list[str]:
    """
    Create Trends Prompt for Chat GPT or OpenRouter models.
    """

    # Check file
    out: list[str] = []

    if not input_path_list:
        raise FileNotFoundError(
            "Could not find required input path list."
            f"Found instead: {input_path_list}"
        )

    for input_path in input_path_list:

        if not input_path:
            raise FileNotFoundError(f"Could not find input path {input_path}")

        if not isinstance(input_path, Path):
            raise ValueError(f"File {input_path} is not a Path object")

        file_list = [
            file_path for file_path in input_path.iterdir() if file_path.is_file()
        ]

        for file_path in file_list:

            if not file_path:
                continue

            prompt_string: str = _get_prompt_string(input_path=file_path)

            if prompt_string:
                out.append(prompt_string)

    return out


# --------------------------------------------------------------------------------------
# Exports 061260
# --------------------------------------------------------------------------------------
__all__: list[str] = [
    "create_multiprompt_list",
]
