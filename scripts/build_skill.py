#!/usr/bin/env python3
"""Build allowlisted portable-skill and Claude-plugin ZIPs with the stdlib."""
from hashlib import sha256
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parent.parent
SKILL_ENTRIES = (
    ("skills/feuerwehr-pruefung/SKILL.md", "feuerwehr-pruefung/SKILL.md"),
    ("skills/feuerwehr-pruefung/references/tool-contracts.md", "feuerwehr-pruefung/references/tool-contracts.md"),
    ("LICENSE", "feuerwehr-pruefung/LICENSE"),
)
PLUGIN_ENTRIES = (
    (".claude-plugin/plugin.json", "feuerwehr-pruefung/.claude-plugin/plugin.json"),
    ("skills/feuerwehr-pruefung/SKILL.md", "feuerwehr-pruefung/skills/feuerwehr-pruefung/SKILL.md"),
    ("skills/feuerwehr-pruefung/references/tool-contracts.md", "feuerwehr-pruefung/skills/feuerwehr-pruefung/references/tool-contracts.md"),
    ("LICENSE", "feuerwehr-pruefung/LICENSE"),
)
PACKAGES = (
    ("feuerwehr-pruefung-skill.zip", SKILL_ENTRIES),
    ("feuerwehr-pruefung-claude-plugin.zip", PLUGIN_ENTRIES),
)


def payloads_for(entries):
    payloads = []
    for source, target in entries:
        path = ROOT / source
        if any(parent.is_symlink() for parent in (path, *path.parents) if parent != ROOT.parent):
            raise ValueError("Symlinked source paths are not supported")
        if not path.resolve().is_relative_to(ROOT):
            raise ValueError("Source escapes the repository")
        payloads.append((target, path.read_bytes().replace(b"\r\n", b"\n")))
    return payloads


def build():
    # Validate all inputs and destinations before writing either package.
    packages = [(name, payloads_for(entries)) for name, entries in PACKAGES]
    destination = ROOT / "dist"
    sums = destination / "SHA256SUMS"
    if any(path.is_symlink() for path in (destination, sums, *(destination / name for name, _ in packages))):
        raise ValueError("Symlinked artifact paths are not supported")
    destination.mkdir(exist_ok=True)
    digests = []
    for name, payloads in packages:
        archive = destination / name
        with ZipFile(archive, "w", compression=ZIP_DEFLATED, compresslevel=9) as bundle:
            for target, content in sorted(payloads):
                entry = ZipInfo(target, date_time=(2026, 1, 1, 0, 0, 0))
                entry.create_system = 3
                entry.external_attr = 0o100644 << 16
                entry.compress_type = ZIP_DEFLATED
                bundle.writestr(entry, content, compress_type=ZIP_DEFLATED, compresslevel=9)
        digest = sha256(archive.read_bytes()).hexdigest()
        digests.append(f"{digest}  {name}\n")
        print(f"Built {name}; sha256={digest}")
    sums.write_text("".join(digests), encoding="utf-8")


if __name__ == "__main__":
    build()
