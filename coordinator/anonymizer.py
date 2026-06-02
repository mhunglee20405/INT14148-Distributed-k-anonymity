import pandas as pd


DIRECT_IDENTIFIERS = ["PatientID", "Name"]
QUASI_IDENTIFIERS = ["Age", "Gender", "ZipCode"]
SENSITIVE_ATTRIBUTE = "Disease"


def generalize_age(age: int, level: int) -> str:
    """
    Level 0: exact age, e.g., 25
    Level 1: 10-year range, e.g., 25 -> 20-29
    Level 2: 20-year range, e.g., 25 -> 20-39
    Level 3: suppressed, *
    """
    age = int(age)

    if level == 0:
        return str(age)

    if level == 1:
        lower = (age // 10) * 10
        upper = lower + 9
        return f"{lower}-{upper}"

    if level == 2:
        lower = (age // 20) * 20
        upper = lower + 19
        return f"{lower}-{upper}"

    return "*"


def generalize_zipcode(zipcode: str, level: int) -> str:
    """
    Level 0: exact zipcode, e.g., 70001
    Level 1: 7000*
    Level 2: 700**
    Level 3: 70***
    Level 4: *
    """
    zipcode = str(zipcode)

    if level == 0:
        return zipcode

    if level == 1:
        return zipcode[:4] + "*"

    if level == 2:
        return zipcode[:3] + "**"

    if level == 3:
        return zipcode[:2] + "***"

    return "*"


def generalize_gender(gender: str, level: int) -> str:
    """
    Usually keep gender unchanged.
    Suppress only at high level.
    """
    if level <= 2:
        return gender

    return "*"


def remove_direct_identifiers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove direct identifiers before publishing data.
    """
    cleaned_df = df.copy()

    for col in DIRECT_IDENTIFIERS:
        if col in cleaned_df.columns:
            cleaned_df = cleaned_df.drop(columns=[col])

    return cleaned_df


def apply_generalization(
    df: pd.DataFrame,
    age_level: int,
    zip_level: int,
    gender_level: int
) -> pd.DataFrame:
    """
    Apply generalization to quasi-identifiers.
    """
    generalized_df = df.copy()

    generalized_df["Age"] = generalized_df["Age"].apply(
        lambda x: generalize_age(x, age_level)
    )

    generalized_df["ZipCode"] = generalized_df["ZipCode"].apply(
        lambda x: generalize_zipcode(x, zip_level)
    )

    generalized_df["Gender"] = generalized_df["Gender"].apply(
        lambda x: generalize_gender(x, gender_level)
    )

    return generalized_df


def check_k_anonymity(df: pd.DataFrame, k: int):
    """
    Check whether every equivalence class has at least k records.

    Equivalence class = records having the same:
    Age, Gender, ZipCode.
    """
    group_counts = (
        df.groupby(QUASI_IDENTIFIERS)
        .size()
        .reset_index(name="count")
    )

    failing_groups = group_counts[group_counts["count"] < k]
    is_valid = failing_groups.empty

    return is_valid, group_counts, failing_groups


def anonymize_dataset(df: pd.DataFrame, k: int = 5):
    """
    Try multiple generalization strategies until k-anonymity is satisfied.
    """
    cleaned_df = remove_direct_identifiers(df)

    strategies = [
        {"age_level": 0, "zip_level": 0, "gender_level": 0},
        {"age_level": 1, "zip_level": 1, "gender_level": 0},
        {"age_level": 1, "zip_level": 2, "gender_level": 0},
        {"age_level": 2, "zip_level": 2, "gender_level": 0},
        {"age_level": 2, "zip_level": 3, "gender_level": 0},
        {"age_level": 3, "zip_level": 4, "gender_level": 3},
    ]

    last_group_counts = None
    last_failing_groups = None

    for strategy in strategies:
        candidate_df = apply_generalization(
            cleaned_df,
            age_level=strategy["age_level"],
            zip_level=strategy["zip_level"],
            gender_level=strategy["gender_level"]
        )

        is_valid, group_counts, failing_groups = check_k_anonymity(candidate_df, k)

        last_group_counts = group_counts
        last_failing_groups = failing_groups

        if is_valid:
            return {
                "status": "PASS",
                "anonymized_df": candidate_df,
                "group_counts": group_counts,
                "failing_groups": failing_groups,
                "strategy": strategy
            }

    return {
        "status": "FAIL",
        "anonymized_df": None,
        "group_counts": last_group_counts,
        "failing_groups": last_failing_groups,
        "strategy": None
    }