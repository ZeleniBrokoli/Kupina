import csv
from pathlib import Path


DATASET_FOLDER = Path("dataset/ml-1m")

FILES = [
    (
        "users.dat",
        "users.csv",
        ["userId", "gender", "age", "occupation", "zipCode"],
    ),
    (
        "movies.dat",
        "movies.csv",
        ["movieId", "title", "genres"],
    ),
    (
        "ratings.dat",
        "ratings.csv",
        ["userId", "movieId", "rating", "timestamp"],
    ),
]


def convert_file(
    input_path: Path,
    output_path: Path,
    headers: list[str],
) -> None:
    if not input_path.exists():
        raise FileNotFoundError(
            f"Fajl nije pronađen: {input_path}"
        )

    with input_path.open(
        "r",
        encoding="latin-1",
    ) as input_file, output_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as output_file:

        writer = csv.writer(output_file)
        writer.writerow(headers)

        for line in input_file:
            values = line.strip().split("::")
            writer.writerow(values)


def main() -> None:
    for input_name, output_name, headers in FILES:
        input_path = DATASET_FOLDER / input_name
        output_path = DATASET_FOLDER / output_name

        print(f"Konverzija: {input_name} -> {output_name}")

        convert_file(
            input_path=input_path,
            output_path=output_path,
            headers=headers,
        )

    print("Konverzija je uspešno završena.")


if __name__ == "__main__":
    main()