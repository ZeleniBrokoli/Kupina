import csv
from pathlib import Path

from pymongo import MongoClient


DATASET_FOLDER = Path("dataset/ml-1m")
MONGODB_URI = "mongodb://127.0.0.1:27017"
DATABASE_NAME = "kupina"
BATCH_SIZE = 10_000


def read_users(csv_path: Path):
    with csv_path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            yield {
                "userId": int(row["userId"]),
                "gender": row["gender"],
                "age": int(row["age"]),
                "occupation": int(row["occupation"]),
                "zipCode": row["zipCode"],
            }


def read_movies(csv_path: Path):
    with csv_path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            yield {
                "movieId": int(row["movieId"]),
                "title": row["title"],
                "genres": row["genres"],
            }


def read_ratings(csv_path: Path):
    with csv_path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            yield {
                "userId": int(row["userId"]),
                "movieId": int(row["movieId"]),
                "rating": float(row["rating"]),
                "timestamp": int(row["timestamp"]),
            }


def insert_in_batches(
    collection,
    documents,
    batch_size: int = BATCH_SIZE,
) -> int:
    batch = []
    inserted_count = 0

    for document in documents:
        batch.append(document)

        if len(batch) >= batch_size:
            collection.insert_many(
                batch,
                ordered=False,
            )

            inserted_count += len(batch)
            print(
                f"{collection.name}: "
                f"učitano {inserted_count} dokumenata"
            )

            batch.clear()

    if batch:
        collection.insert_many(
            batch,
            ordered=False,
        )
        inserted_count += len(batch)

    return inserted_count


def check_csv_files() -> None:
    required_files = [
        DATASET_FOLDER / "users.csv",
        DATASET_FOLDER / "movies.csv",
        DATASET_FOLDER / "ratings.csv",
    ]

    missing_files = [
        path
        for path in required_files
        if not path.exists()
    ]

    if missing_files:
        files = "\n".join(
            f"- {path}"
            for path in missing_files
        )

        raise FileNotFoundError(
            "Nedostaju CSV fajlovi:\n"
            f"{files}\n"
            "Prvo pokreni convert_movielens_to_csv.py."
        )


def main() -> None:
    check_csv_files()

    client = MongoClient(MONGODB_URI)
    db = client[DATABASE_NAME]

    client.admin.command("ping")
    print("Povezivanje sa MongoDB bazom je uspešno.")

    # Brišemo samo početne MovieLens kolekcije.
    db.users.drop()
    db.movies.drop()
    db.ratings.drop()

    print("Postojeće MovieLens kolekcije su obrisane.")

    users_count = insert_in_batches(
        db.users,
        read_users(DATASET_FOLDER / "users.csv"),
    )

    movies_count = insert_in_batches(
        db.movies,
        read_movies(DATASET_FOLDER / "movies.csv"),
    )

    ratings_count = insert_in_batches(
        db.ratings,
        read_ratings(DATASET_FOLDER / "ratings.csv"),
    )

    db.users.create_index(
        "userId",
        unique=True,
    )

    db.movies.create_index(
        "movieId",
        unique=True,
    )

    db.ratings.create_index(
        [
            ("userId", 1),
            ("movieId", 1),
        ]
    )

    client.close()

    print("\nImport je uspešno završen.")
    print(f"Korisnici: {users_count}")
    print(f"Filmovi: {movies_count}")
    print(f"Ocene: {ratings_count}")


if __name__ == "__main__":
    main()