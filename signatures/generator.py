
import json
import re
from pathlib import Path
from html import escape

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "individual signatures"

# Read the shared configuration and master template.
data = json.loads((ROOT / "teamInfo.json").read_text(encoding="utf-8"))
template = (ROOT / "template.html").read_text(encoding="utf-8")

OUTPUT.mkdir(exist_ok=True)

def safe_filename(value):
    """Allow only simple filenames for generated files."""
    if not re.fullmatch(r"[a-z0-9_-]+", value):
        raise ValueError(f"Invalid member id: {value!r}")
    return value + ".html"

def render_signature(member):
    values = {
        "NAME": member["name"],
        "POSITION": member["role"],
        "EMAIL": member["email"],
        "TEAM_NAME": data["team_name"],
        "AFFILIATION": data["affiliation"],
        "WEBSITE": data["website"],
        "DEPARTMENT": data["deparment"],
        "LOGO_URL": data["logo_url"],
    }

    # Escape personal text and URLs before inserting them into HTML.
    # Attribute values are escaped too, including quotation marks.
    rendered = template
    for key, value in values.items():
        rendered = rendered.replace(
            "{{" + key + "}}",
            escape(str(value), quote=True)
        )

    # Catch misspelled or forgotten template placeholders.
    if re.search(r"\{\{[^}]+\}\}", rendered):
        raise ValueError("Unresolved placeholder in template.html")

    return rendered

seen_ids = set()

for member in data["members"]:
    member_id = member["id"]

    if member_id in seen_ids:
        raise ValueError(f"Duplicate member id: {member_id}")
    seen_ids.add(member_id)

    filename = safe_filename(member_id)
    output_file = OUTPUT / filename
    output_file.write_text(
        render_signature(member),
        encoding="utf-8"
    )
    print(f"Generated: {output_file.relative_to(ROOT)}")

print(f"\nDone — generated {len(seen_ids)} signatures.")
