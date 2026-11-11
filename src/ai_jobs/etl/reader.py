import csv
from collections.abc import Iterator
from pathlib import Path


def read_csv(source: Path) -> Iterator[tuple[int, dict[str, str]]]:
    """Read CSV rows and return each row with its source line number."""
    if not source.exists():
        raise FileNotFoundError(f"CSV file not found: {source}")

    if not source.is_file():
        raise ValueError(f"CSV source is not a file: {source}")

    try:
        with source.open(
            mode="r",
            encoding="utf-8-sig",
            newline="",
        ) as csv_file:
            reader = csv.DictReader(csv_file)

            if not reader.fieldnames:
                raise ValueError("CSV file has no header.")

            for row_number, row in enumerate(reader, start=2):
                if None in row:
                    raise ValueError(
                        f"CSV row {row_number} contains more values than the header."
                    )

                yield row_number, row

    except csv.Error as error:
        raise ValueError(f"Failed to parse CSV: {error}") from error
