import pandas as pd
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"

RAW_FILES = [
    DATA_DIR / "site_a.csv",
    DATA_DIR / "site_b.csv"
]

ANONYMIZED_FILE = OUTPUT_DIR / "anonymized_result.csv"


def load_raw_data():
    """
    Load raw data from both distributed sites.
    This simulates what would happen if an attacker could access raw data.
    """
    dataframes = []

    for file_path in RAW_FILES:
        df = pd.read_csv(file_path)
        dataframes.append(df)

    return pd.concat(dataframes, ignore_index=True)


def attack_raw_data(age: int, gender: str, zipcode: str):
   
    raw_df = load_raw_data()

    matched = raw_df[
        (raw_df["Age"] == age) &
        (raw_df["Gender"] == gender) &
        (raw_df["ZipCode"].astype(str) == str(zipcode))
    ]

    print("\n[Attack 1] Re-identification attack on RAW data")
    print(f"Attacker knows: Age={age}, Gender={gender}, ZipCode={zipcode}")

    if len(matched) == 1:
        print("Result: LEAK FOUND")
        print("A unique patient was identified:")
        print(matched.to_string(index=False))
    elif len(matched) > 1:
        print("Result: Multiple patients matched.")
        print(matched.to_string(index=False))
    else:
        print("Result: No patient matched.")


def attack_anonymized_data(age_range: str, gender: str, zipcode_generalized: str):
    
    print("\n[Attack 2] Re-identification attack on ANONYMIZED data")

    if not ANONYMIZED_FILE.exists():
        print("Anonymized file not found.")
        print("Please run: python coordinator/coordinator.py first.")
        return

    anon_df = pd.read_csv(ANONYMIZED_FILE)

    matched = anon_df[
        (anon_df["Age"].astype(str) == age_range) &
        (anon_df["Gender"] == gender) &
        (anon_df["ZipCode"].astype(str) == zipcode_generalized)
    ]

    print(
        f"Attacker knows generalized group: "
        f"Age={age_range}, Gender={gender}, ZipCode={zipcode_generalized}"
    )

    if len(matched) >= 5:
        print("Result: ATTACK BLOCKED BY k-ANONYMITY")
        print(f"Matched equivalence class size: {len(matched)}")
        print("Possible diseases in this group:")
        print(sorted(matched["Disease"].unique()))
    elif 0 < len(matched) < 5:
        print("Result: PRIVACY RISK")
        print(f"Group size is only {len(matched)}")
        print(matched.to_string(index=False))
    else:
        print("Result: No matching anonymized group.")


def check_output_leaks():
    """
    Check whether anonymized output still contains obvious leaks.
    """
    print("\n[Attack 3] Output leak check")

    if not ANONYMIZED_FILE.exists():
        print("Anonymized file not found.")
        print("Please run: python coordinator/coordinator.py first.")
        return

    anon_df = pd.read_csv(ANONYMIZED_FILE)

    forbidden_columns = ["PatientID", "Name"]
    leaked_columns = [col for col in forbidden_columns if col in anon_df.columns]

    if leaked_columns:
        print("Result: LEAK FOUND")
        print("Forbidden columns found:", leaked_columns)
    else:
        print("Direct identifiers check: PASS")
        print("PatientID and Name are not found in anonymized output.")

    exact_age_count = anon_df["Age"].astype(str).str.fullmatch(r"\d+").sum()
    exact_zip_count = anon_df["ZipCode"].astype(str).str.fullmatch(r"\d{5}").sum()

    if exact_age_count > 0 or exact_zip_count > 0:
        print("Raw quasi-identifier check: WARNING")
        print(f"Exact Age values found: {exact_age_count}")
        print(f"Exact ZipCode values found: {exact_zip_count}")
    else:
        print("Raw quasi-identifier check: PASS")
        print("Exact Age and exact ZipCode are not found.")


def main():
    print("=" * 75)
    print("Hacker Mode: Privacy Attack Simulation")
    print("=" * 75)

    # Attack on one exact patient in raw data
    attack_raw_data(age=25, gender="Male", zipcode="70001")

    # Attack on the corresponding anonymized equivalence class
    attack_anonymized_data(
        age_range="20-29",
        gender="Male",
        zipcode_generalized="700**"
    )

    # Check whether published output still leaks direct identifiers
    check_output_leaks()

    print("=" * 75)


if __name__ == "__main__":
    main()