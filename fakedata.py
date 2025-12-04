import csv
import os
from faker import Faker

fake = Faker()

# Create directory if not exists
folder_name = "fake_data"
os.makedirs(folder_name, exist_ok=True)

# Number of CSV files to create
num_files = 50

# Number of rows per file
rows_per_file = 50

for i in range(1, num_files + 1):
    filename = os.path.join(folder_name, f"fake_data_{i}.csv")

    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["name", "role", "location", "extra_info"])

        for _ in range(rows_per_file):
            writer.writerow([
                fake.name(),
                fake.job(),
                fake.city(),
                fake.sentence(nb_words=6)
            ])

    print(f"Created -> {filename}")

print(f"\n🎉 Successfully generated {num_files} CSV files inside '{folder_name}' folder.")
