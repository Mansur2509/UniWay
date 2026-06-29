"""Rule-based importer for the university XLSX dataset.

The parsing/normalization logic lives here (not in the management command) so it
can be unit-tested directly against in-memory row dicts without touching a file.

Policy (see docs/DECISIONS.md): never invent data. Anything that cannot be
parsed confidently is preserved as raw text and the row is flagged in the import
report. Questionable values (e.g. identical SAT 25/50/75 placeholders) are never
stored as verified statistics.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.utils.text import slugify

from .models import (
    University,
    UniversityDataSource,
    UniversityFieldVerification,
    UniversityProgram,
    UniversityScholarship,
)

EXPECTED_HEADERS = [
    "Name",
    "Country",
    "City",
    "Official Website",
    "Admissions URL",
    "Majors",
    "Deadlines",
    "SAT 25th",
    "SAT 50th",
    "SAT 75th",
    "IELTS Minimum",
    "IELTS Competitive",
    "Average GPA",
    "Acceptance Rate",
    "Tuition",
    "Scholarships",
    "AP Recommendations by Major",
    "Application Requirements",
    "Essays",
    "Financial Aid",
    "Source URLs",
    "Last Verified Date",
]

DEFAULT_SHEET_NAME = "Database"

VERIFICATION_CHOICES = {"verified", "partial", "estimated"}

# Excel stores dates as a serial day count from 1899-12-30 (the well-known Lotus
# 1900 leap-year quirk offset).
_EXCEL_EPOCH = date(1899, 12, 30)

_URL_RE = re.compile(r"https?://[^\s,;]+", re.IGNORECASE)
_DEADLINE_DATE_RE = re.compile(r"([A-Za-z]{3,9})\.?\s+(\d{1,2}),?\s+(\d{4})")
_WORD_LIMIT_RE = re.compile(r"([\d,]{2,6})\s*(?:words|characters)", re.IGNORECASE)

_CURRENCY_BY_COUNTRY = {
    "usa": "USD",
    "united states": "USD",
    "uk": "GBP",
    "united kingdom": "GBP",
    "england": "GBP",
    "scotland": "GBP",
    "italy": "EUR",
    "france": "EUR",
    "germany": "EUR",
    "netherlands": "EUR",
    "spain": "EUR",
    "ireland": "EUR",
    "singapore": "SGD",
    "japan": "JPY",
    "china": "CNY",
    "hong kong": "HKD",
    "canada": "CAD",
    "switzerland": "CHF",
    "australia": "AUD",
    "south korea": "KRW",
}

_SCHOLARSHIP_TYPES = [
    ("full ride", "Full-ride scholarship"),
    ("full tuition", "Full-tuition scholarship"),
    ("need-based", "Need-based aid"),
    ("need based", "Need-based aid"),
    ("merit", "Merit scholarship"),
    ("partial", "Partial scholarship"),
    ("international", "International-student aid"),
    ("external", "External scholarship"),
    ("government", "Government/national scholarship"),
    ("national scholarship", "Government/national scholarship"),
]


class UniversityWorkbookError(ValueError):
    """Raised when the XLSX workbook cannot be safely parsed for import."""


def load_xlsx_rows(path: str | Path, *, sheet_name: str = DEFAULT_SHEET_NAME) -> list[dict]:
    """Read the expected university workbook into importer row dictionaries."""
    try:
        from openpyxl import load_workbook
    except ImportError as exc:  # pragma: no cover - dependency guard
        raise UniversityWorkbookError(
            "openpyxl is required to read university XLSX workbooks."
        ) from exc

    workbook_path = Path(path)
    if not workbook_path.exists():
        raise UniversityWorkbookError(f"Workbook not found: {workbook_path}")

    try:
        workbook = load_workbook(workbook_path, read_only=True, data_only=True)
    except Exception as exc:
        raise UniversityWorkbookError("The uploaded file could not be read as an XLSX workbook.") from exc

    try:
        if sheet_name not in workbook.sheetnames:
            raise UniversityWorkbookError(
                f"Sheet {sheet_name!r} not found. Available: {workbook.sheetnames}"
            )
        worksheet = workbook[sheet_name]

        all_rows = list(worksheet.iter_rows(values_only=True))
        if not all_rows:
            raise UniversityWorkbookError("The worksheet is empty.")

        header = [(c or "").strip() if isinstance(c, str) else c for c in all_rows[0]]
        header = [h for h in header if h is not None]
        missing = [h for h in EXPECTED_HEADERS if h not in header]
        if missing:
            raise UniversityWorkbookError(
                "Workbook headers do not match the expected dataset. "
                f"Missing columns: {missing}"
            )

        index_by_header = {h: i for i, h in enumerate(all_rows[0]) if isinstance(h, str)}
        row_dicts: list[dict] = []
        for raw in all_rows[1:]:
            if not raw or all(cell in (None, "") for cell in raw):
                continue
            row_dicts.append(
                {h: (raw[i] if i < len(raw) else None) for h, i in index_by_header.items()}
            )
        return row_dicts
    finally:
        workbook.close()


def clean(value) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def strip_parenthetical(name: str) -> str:
    """Drop a trailing "(...)" so "MIT (MIT)" and a curated "MIT" share a slug."""
    return re.sub(r"\s*\([^)]*\)\s*$", "", name).strip()


def make_slug(name: str) -> str:
    base = strip_parenthetical(name) or name
    return slugify(base)[:260]


def parse_decimal(value) -> Decimal | None:
    s = clean(value).replace(",", "")
    if not s:
        return None
    match = re.search(r"-?\d+(?:\.\d+)?", s)
    if not match:
        return None
    try:
        return Decimal(match.group(0))
    except InvalidOperation:
        return None


def parse_int(value) -> int | None:
    parsed = parse_decimal(value)
    return int(parsed) if parsed is not None else None


def parse_acceptance_rate(value) -> tuple[Decimal | None, str | None]:
    """Return (percent number rounded to 2dp, warning).

    Accepts 0.038 (fraction), "28.0%", "0.28", or 28.0 and always returns a
    percentage number consistent with the existing catalog (e.g. MIT 4.60).
    """
    s = clean(value)
    if not s:
        return None, None
    number = parse_decimal(s)
    if number is None:
        return None, f"unparseable acceptance rate: {s!r}"
    if "%" in s:
        percent = number
    elif number <= 1:
        percent = number * 100
    else:
        percent = number
    percent = percent.quantize(Decimal("0.01"))
    if percent < 0 or percent > 100:
        return None, f"acceptance rate out of range: {s!r}"
    return percent, None


def guess_currency(country: str, raw: str) -> str:
    if "£" in raw:
        return "GBP"
    if "€" in raw:
        return "EUR"
    if "¥" in raw:
        return "JPY"
    lowered = (country or "").lower()
    if "$" in raw and "singapore" in lowered:
        return "SGD"
    if "$" in raw:
        return "USD"
    for key, code in _CURRENCY_BY_COUNTRY.items():
        if key in lowered:
            return code
    return "USD"


def parse_tuition(value, country: str) -> tuple[Decimal | None, str, str, str | None]:
    """Return (amount, currency, raw_text, warning)."""
    s = clean(value)
    if not s:
        return None, "USD", "", None
    currency = guess_currency(country, s)
    number = parse_decimal(s)
    if number is None:
        return None, currency, s, f"unparseable tuition, kept raw: {s!r}"
    return number.quantize(Decimal("0.01")), currency, s, None


def parse_date(value) -> tuple[date | None, str | None]:
    if value is None:
        return None, None
    if isinstance(value, datetime):
        return value.date(), None
    if isinstance(value, date):
        return value, None
    s = clean(value)
    if not s:
        return None, None
    if re.fullmatch(r"\d{4,6}(?:\.0)?", s):
        try:
            serial = int(float(s))
        except ValueError:
            serial = None
        if serial is not None and 20000 < serial < 60000:
            return _EXCEL_EPOCH + timedelta(days=serial), None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%b %d, %Y", "%B %d, %Y", "%d %b %Y", "%d %B %Y"):
        try:
            return datetime.strptime(s, fmt).date(), None
        except ValueError:
            continue
    return None, f"unsupported date format: {s!r}"


def detect_sat_placeholder(p25: int | None, p50: int | None, p75: int | None) -> bool:
    """Real SAT 25/50/75 percentiles are never identical; equal values across at
    least two percentiles signal placeholder data (e.g. the 550/550/550 rows)."""
    values = [v for v in (p25, p50, p75) if v is not None]
    return len(values) >= 2 and len(set(values)) == 1


def parse_majors(value) -> list[str]:
    s = clean(value)
    if not s:
        return []
    parts = re.split(r"[;,]", s)
    seen: list[str] = []
    for part in parts:
        name = part.strip()
        if name and name.lower() not in {p.lower() for p in seen}:
            seen.append(name[:240])
    return seen


def parse_sources(value) -> list[str]:
    s = clean(value)
    if not s:
        return []
    urls: list[str] = []
    for match in _URL_RE.findall(s):
        url = match.rstrip(").,;")
        if url not in urls:
            urls.append(url)
    return urls


def parse_deadlines(value) -> list[tuple[str, date | None, str]]:
    s = clean(value)
    if not s:
        return []
    parsed: list[tuple[str, date | None, str]] = []
    for line in re.split(r"[\r\n]+", s):
        line = line.strip()
        if not line:
            continue
        deadline: date | None = None
        match = _DEADLINE_DATE_RE.search(line)
        if match:
            month, day, year = match.group(1), match.group(2), match.group(3)
            for fmt in ("%b %d %Y", "%B %d %Y"):
                try:
                    deadline = datetime.strptime(
                        f"{month[:9]} {day} {year}", fmt
                    ).date()
                    break
                except ValueError:
                    continue
            if deadline is None:
                try:
                    deadline = datetime.strptime(
                        f"{month[:3]} {day} {year}", "%b %d %Y"
                    ).date()
                except ValueError:
                    deadline = None
        label = line.split(":", 1)[0].strip() if ":" in line else line
        parsed.append((label, deadline, line))
    return parsed


def choose_application_deadline(value) -> tuple[date | None, int]:
    parsed = parse_deadlines(value)
    dated = [(label, deadline) for (label, deadline, _raw) in parsed if deadline]
    count = len(dated)
    if not dated:
        return None, count
    for key in ("regular decision", "regular", "application deadline", "ucas", "rd"):
        for label, deadline in dated:
            if key in label.lower():
                return deadline, count
    return max(deadline for _label, deadline in dated), count


def count_word_limits(value) -> int:
    return len(_WORD_LIMIT_RE.findall(clean(value)))


def detect_scholarship_types(value) -> list[str]:
    lowered = clean(value).lower()
    if not lowered:
        return []
    labels: list[str] = []
    for keyword, label in _SCHOLARSHIP_TYPES:
        if keyword in lowered and label not in labels:
            labels.append(label)
    return labels


@dataclass
class RowResult:
    row_number: int
    name: str
    slug: str
    status: str = "skipped"  # created | updated | skipped
    duplicate_matched: bool = False
    parsed_field_count: int = 0
    source_url_count: int = 0
    last_verified_date: str | None = None
    warnings: list[str] = field(default_factory=list)
    questionable_fields: list[str] = field(default_factory=list)


@dataclass
class ImportReport:
    created: int = 0
    updated: int = 0
    skipped: int = 0
    placeholder_sat: int = 0
    parsed_deadlines: int = 0
    parsed_essays: int = 0
    source_urls: int = 0
    fields_verified: int = 0
    rows: list[RowResult] = field(default_factory=list)

    @property
    def warnings_count(self) -> int:
        return sum(len(row.warnings) for row in self.rows)

    def add(self, row: RowResult) -> None:
        self.rows.append(row)
        if row.status == "created":
            self.created += 1
        elif row.status == "updated":
            self.updated += 1
        else:
            self.skipped += 1

    def as_dict(self) -> dict:
        return {
            "summary": {
                "created": self.created,
                "updated": self.updated,
                "skipped": self.skipped,
                "warnings": self.warnings_count,
                "placeholder_sat": self.placeholder_sat,
                "parsed_deadlines": self.parsed_deadlines,
                "parsed_essays": self.parsed_essays,
                "source_urls": self.source_urls,
                "fields_verified": self.fields_verified,
            },
            "rows": [
                {
                    "row_number": row.row_number,
                    "name": row.name,
                    "slug": row.slug,
                    "status": row.status,
                    "duplicate_matched": row.duplicate_matched,
                    "parsed_field_count": row.parsed_field_count,
                    "questionable_fields": row.questionable_fields,
                    "source_url_count": row.source_url_count,
                    "last_verified_date": row.last_verified_date,
                    "warnings": row.warnings,
                }
                for row in self.rows
            ],
        }


def _http(url: str) -> str:
    url = (url or "").strip()
    return url if url.lower().startswith(("http://", "https://")) else ""


def import_rows(
    rows: list[dict],
    *,
    replace_existing: bool = False,
    include_questionable: bool = False,
    source_label: str = "Universities Data XLSX",
    default_verification: str = "partial",
) -> ImportReport:
    if default_verification not in VERIFICATION_CHOICES:
        default_verification = "partial"
    report = ImportReport()

    for index, raw_row in enumerate(rows, start=2):  # row 1 is the header
        name = clean(raw_row.get("Name"))
        if not name:
            continue

        slug = make_slug(name)
        result = RowResult(row_number=index, name=name, slug=slug)

        country = clean(raw_row.get("Country"))
        official = _http(raw_row.get("Official Website")) or _http(raw_row.get("Admissions URL"))
        if not official:
            result.warnings.append("missing official website / admissions URL")
            report.add(result)
            continue

        sources = parse_sources(raw_row.get("Source URLs"))
        result.source_url_count = len(sources)
        report.source_urls += len(sources)
        primary_source = _http(sources[0]) if sources else ""
        verified_date, date_warning = parse_date(raw_row.get("Last Verified Date"))
        if date_warning:
            result.warnings.append(date_warning)
        result.last_verified_date = verified_date.isoformat() if verified_date else None
        if not sources:
            result.warnings.append("missing source URL")

        status = default_verification if (primary_source and verified_date) else None

        acceptance, acceptance_warning = parse_acceptance_rate(raw_row.get("Acceptance Rate"))
        if acceptance_warning:
            result.warnings.append(acceptance_warning)

        sat25 = parse_int(raw_row.get("SAT 25th"))
        sat50 = parse_int(raw_row.get("SAT 50th"))
        sat75 = parse_int(raw_row.get("SAT 75th"))
        placeholder = detect_sat_placeholder(sat25, sat50, sat75)
        sat_note = ""
        if placeholder:
            report.placeholder_sat += 1
            result.warnings.append("possible placeholder SAT values")
            result.questionable_fields.append("sat")
            sat_note = (
                "Possible placeholder SAT values "
                f"({sat25}/{sat50}/{sat75}); not stored as verified statistics."
            )
            if not include_questionable:
                sat25 = sat50 = sat75 = None

        gpa = parse_decimal(raw_row.get("Average GPA"))
        raw_gpa = clean(raw_row.get("Average GPA"))
        gpa_note = ""
        if gpa is None and raw_gpa:
            gpa_note = f"GPA (as provided): {raw_gpa}"
            result.warnings.append("GPA stored as text note")

        ielts_min = parse_decimal(raw_row.get("IELTS Minimum"))
        ielts_comp = parse_decimal(raw_row.get("IELTS Competitive"))

        tuition, currency, tuition_raw, tuition_warning = parse_tuition(
            raw_row.get("Tuition"), country
        )
        if tuition_warning:
            result.warnings.append(tuition_warning)

        app_deadline, deadline_count = choose_application_deadline(raw_row.get("Deadlines"))
        report.parsed_deadlines += deadline_count
        deadlines_text = clean(raw_row.get("Deadlines"))
        if deadlines_text and deadline_count == 0:
            result.warnings.append("unparseable deadline (kept raw text)")

        essays_text = clean(raw_row.get("Essays"))
        if count_word_limits(essays_text):
            report.parsed_essays += 1

        majors = parse_majors(raw_row.get("Majors"))
        if not majors:
            result.warnings.append("empty majors")

        scholarships_text = clean(raw_row.get("Scholarships"))
        financial_aid_notes = clean(raw_row.get("Financial Aid"))
        application_requirements = clean(raw_row.get("Application Requirements"))
        ap_recommendations = clean(raw_row.get("AP Recommendations by Major"))

        data_quality_lines: list[str] = []
        if sat_note:
            data_quality_lines.append(sat_note)
        if gpa_note:
            data_quality_lines.append(gpa_note)
        if tuition is None and tuition_raw:
            data_quality_lines.append(f"Tuition (as provided): {tuition_raw}")
        elif (
            tuition is not None
            and currency == "USD"
            and "$" in tuition_raw
            and any(key in country.lower() for key in _CURRENCY_BY_COUNTRY if _CURRENCY_BY_COUNTRY[key] != "USD")
        ):
            # The source wrote a "$" figure for a non-US institution; keep the exact
            # source string visible rather than silently converting the currency.
            data_quality_lines.append(
                f"Tuition shown as {tuition_raw} in the source (a $ figure on a "
                "non-US institution; treat the currency as the source's USD-equivalent)."
            )
        if not sources:
            data_quality_lines.append(
                "No source URL provided in the dataset; treat all figures as unverified."
            )
        data_quality_notes = "\n".join(data_quality_lines)

        existing = University.objects.filter(slug=slug).first()
        created = existing is None
        university = existing or University(
            slug=slug,
            name=name,
            official_website=official,
            is_published=True,
            is_demo=False,
        )
        result.duplicate_matched = not created

        def assign(attr: str, value, *, _u=university, _created=created, _replace=replace_existing) -> None:
            """Fill a field. New rows and --replace-existing overwrite; otherwise
            only fill values that are currently empty so curated data is kept.
            (Loop variables are bound via defaults so this stays correct per row.)"""
            if value in (None, ""):
                return
            if _created or _replace or getattr(_u, attr) in (None, ""):
                setattr(_u, attr, value)

        if created:
            university.name = name
            university.official_website = official
            university.is_published = True
            university.is_demo = False
        assign("country", country)
        assign("city", clean(raw_row.get("City")))
        admissions = _http(raw_row.get("Admissions URL"))
        if admissions:
            assign("admissions_url", admissions)
        assign("acceptance_rate", acceptance)
        assign("sat_p25", sat25)
        assign("sat_average", sat50)
        assign("sat_p75", sat75)
        assign("gpa_average", gpa)
        assign("ielts_minimum", ielts_min)
        assign("ielts_competitive", ielts_comp)
        # Currency carries a model default of "USD", so it is never "blank" and the
        # fill-only-blanks rule would never correct it. Tie it to the amount: set
        # the currency whenever we actually populate the tuition amount.
        had_tuition = university.tuition_amount is not None
        assign("tuition_amount", tuition)
        if tuition is not None and (created or replace_existing or not had_tuition):
            university.tuition_currency = currency
        assign("application_deadline", app_deadline)
        assign("essay_requirements", essays_text)
        assign("application_requirements", application_requirements)
        assign("ap_recommendations", ap_recommendations)
        assign("deadlines_text", deadlines_text)
        assign("financial_aid_notes", financial_aid_notes)
        assign("scholarships_text", scholarships_text)
        assign("data_quality_notes", data_quality_notes)
        if scholarships_text or financial_aid_notes:
            if created or replace_existing or university.scholarship_available is None:
                university.scholarship_available = True

        university.save()

        # --- idempotent related records ---
        for major in majors:
            UniversityProgram.objects.get_or_create(university=university, name=major)

        for url in sources:
            normalized = _http(url)
            if not normalized:
                continue
            UniversityDataSource.objects.get_or_create(
                university=university,
                source_url=normalized,
                defaults={
                    "source_title": f"{source_label}: {name}",
                    "is_official": True,
                    "published_at": verified_date,
                },
            )

        scholarship_url = primary_source or university.financial_aid_url or official
        for label in detect_scholarship_types(scholarships_text):
            UniversityScholarship.objects.get_or_create(
                university=university,
                name=label,
                defaults={
                    "summary": scholarships_text[:2000],
                    "official_url": scholarship_url,
                },
            )

        # --- per-field verification (only where a source + date exist) ---
        verifiable = {
            "acceptance_rate": acceptance,
            "sat_p25": sat25,
            "sat_average": sat50,
            "sat_p75": sat75,
            "gpa_average": gpa,
            "ielts_minimum": ielts_min,
            "ielts_competitive": ielts_comp,
            "tuition_amount": tuition,
            "application_deadline": app_deadline,
            "essay_requirements": essays_text or None,
            "scholarship_available": university.scholarship_available,
        }
        if primary_source and verified_date:
            for field_name, value in verifiable.items():
                if value in (None, ""):
                    continue
                field_status = status
                note = ""
                if field_name.startswith("sat") and placeholder:
                    field_status = "estimated"
                    note = "Identical SAT percentiles in the source; treat as estimated."
                defaults = {
                    "status": field_status,
                    "source_url": primary_source,
                    "last_verified_date": verified_date,
                    "note": note,
                }
                if replace_existing:
                    UniversityFieldVerification.objects.update_or_create(
                        university=university, field_name=field_name, defaults=defaults
                    )
                else:
                    # Preserve a curated/manually-verified row if one already exists;
                    # only add verification for fields that had none.
                    UniversityFieldVerification.objects.get_or_create(
                        university=university, field_name=field_name, defaults=defaults
                    )
                report.fields_verified += 1

        result.parsed_field_count = sum(
            1
            for value in (
                acceptance,
                sat25,
                sat50,
                sat75,
                gpa,
                ielts_min,
                ielts_comp,
                tuition,
                app_deadline,
                essays_text or None,
                scholarships_text or None,
                financial_aid_notes or None,
                application_requirements or None,
                ap_recommendations or None,
            )
            if value not in (None, "")
        )
        result.status = "created" if created else "updated"
        report.add(result)

    return report
