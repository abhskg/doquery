#!/usr/bin/env python
"""
Generate requirements.txt from Poetry's pyproject.toml

This script extracts dependencies from pyproject.toml and writes them to requirements.txt
"""
import re
import sys
from pathlib import Path


def extract_deps_from_pyproject(pyproject_path):
    """Extract dependencies from pyproject.toml"""
    with open(pyproject_path, "r") as f:
        content = f.read()

    # Extract the main dependencies section
    deps_section = re.search(
        r"\[tool\.poetry\.dependencies\](.*?)(?=\[tool|$)", content, re.DOTALL
    )
    if not deps_section:
        print("Could not find dependencies section in pyproject.toml")
        sys.exit(1)

    deps_text = deps_section.group(1)

    # Parse dependencies
    deps = []
    for line in deps_text.strip().split("\n"):
        line = line.strip()
        if not line or line.startswith("#") or line == "python = ":
            continue

        # Match package name and version
        match = re.match(r'([a-zA-Z0-9\-_]+)\s*=\s*["\']([^"\']+)["\']', line)
        if match:
            package, version = match.groups()
            # Handle caret version range (^x.y.z) by removing the caret
            if version.startswith("^"):
                version = version[1:]
            deps.append(f"{package}=={version}")

    return deps


def write_requirements_txt(deps, output_path):
    """Write dependencies to requirements.txt"""
    with open(output_path, "w") as f:
        f.write("\n".join(deps) + "\n")


if __name__ == "__main__":
    script_dir = Path(__file__).parent
    pyproject_path = script_dir / "pyproject.toml"
    requirements_path = script_dir / "requirements.txt"

    print(f"Generating {requirements_path} from {pyproject_path}...")

    deps = extract_deps_from_pyproject(pyproject_path)
    write_requirements_txt(deps, requirements_path)

    print(f"Successfully generated {requirements_path} with {len(deps)} dependencies.")
    print("Generated requirements:")
    for dep in deps:
        print(f"  - {dep}")
