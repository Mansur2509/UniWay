from __future__ import annotations

import stat
import zipfile
from pathlib import PurePosixPath

from rest_framework import serializers

MAX_XLSX_ENTRIES = 5_000
MAX_XLSX_UNCOMPRESSED_BYTES = 100 * 1024 * 1024
REQUIRED_XLSX_MEMBERS = {"[Content_Types].xml", "xl/workbook.xml"}
FORBIDDEN_XLSX_SUFFIXES = ("vbaproject.bin",)


def validate_xlsx_archive(uploaded_file):
    """Validate XLSX ZIP metadata without extracting or parsing workbook rows."""

    try:
        uploaded_file.seek(0)
        if uploaded_file.read(4) != b"PK\x03\x04":
            raise serializers.ValidationError("The file is not a valid .xlsx archive.")
        uploaded_file.seek(0)

        with zipfile.ZipFile(uploaded_file) as archive:
            entries = archive.infolist()
            if not entries or len(entries) > MAX_XLSX_ENTRIES:
                raise serializers.ValidationError("The workbook archive has an unsafe entry count.")

            names = set()
            total_uncompressed = 0
            for entry in entries:
                normalized_name = entry.filename.replace("\\", "/")
                path = PurePosixPath(normalized_name)
                if path.is_absolute() or ".." in path.parts:
                    raise serializers.ValidationError("The workbook archive contains an unsafe path.")
                if entry.flag_bits & 0x1:
                    raise serializers.ValidationError("Encrypted workbook archives are not accepted.")
                file_mode = entry.external_attr >> 16
                if stat.S_ISLNK(file_mode):
                    raise serializers.ValidationError("Workbook archive links are not accepted.")
                if normalized_name.lower().endswith(FORBIDDEN_XLSX_SUFFIXES):
                    raise serializers.ValidationError("Macro-enabled workbook content is not accepted.")

                names.add(normalized_name)
                total_uncompressed += entry.file_size
                if total_uncompressed > MAX_XLSX_UNCOMPRESSED_BYTES:
                    raise serializers.ValidationError(
                        "The workbook expands beyond the safe processing limit."
                    )

            if not REQUIRED_XLSX_MEMBERS.issubset(names):
                raise serializers.ValidationError("The archive is not a valid Excel workbook.")
    except (zipfile.BadZipFile, OSError, ValueError) as error:
        raise serializers.ValidationError("The file is not a valid .xlsx archive.") from error
    finally:
        uploaded_file.seek(0)

    return uploaded_file
