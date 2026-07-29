import csv
import json
import sys

def load_csv_rows(filepath):
    # encoding cascade for Windows vs Linux Jenzabar dumps
    for enc in ['utf-8-sig', 'utf-8', 'cp1252', 'latin1']:
        try:
            with open(filepath, 'r', encoding=enc, newline='') as f:
                reader = csv.DictReader(f)
                # normalize header keys to uppercase to prevent case mismatches
                return [{(k.upper() if k else k): v for k, v in row.items()} for row in reader]
        except (UnicodeDecodeError, UnicodeError):
            continue
    raise ValueError(f"unable to decode {filepath}")

def generate_json(csv_path, json_path):
    rows = load_csv_rows(csv_path)
    out_data = {"c": {}}

    for row in rows:
        crs_cde_raw = row.get("CRS_CDE") or ""
        if not crs_cde_raw.strip():
            continue

        dept_code = crs_cde_raw.strip().split()[0]
        crs_code_concat = "".join(crs_cde_raw.strip().lower().split())
        crs_code = repr(" ".join(crs_cde_raw.strip().split()))

        crs_title_raw = (row.get("CRS_TITLE") or "").strip().replace("'", "")
        crs_code_with_title = repr(' '.join(crs_cde_raw.strip().split()) + " " + crs_title_raw)

        # mirror pandas behavior for missing/empty catalog text
        cat_text = row.get("CATALOG_TEXT")
        if cat_text is None or cat_text == "":
            crs_desc = "nan"
        else:
            crs_desc = (
                str(cat_text)
                .strip()
                .replace("  ", " ")
                .replace("\r\n", " ")
                .replace("\\r\\n", " ")
            )

        out_data["c"][crs_code_concat] = {
            "short": crs_code,
            "long": crs_code_with_title,
            "desc": crs_desc,
            "namelink": f"[{crs_code[1:-1]}](departmental_programs/{dept_code}_courses.qmd#courses-in-SOMETHING)",
            "namelinklong": f"[{crs_code_with_title[1:-1]}](departmental_programs/{dept_code}_courses.qmd#courses-in-SOMETHING)"
        }

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(out_data, f, indent=2)

if __name__ == "__main__":
    generate_json("catalog_from_jenzabar.csv", "courses.json")