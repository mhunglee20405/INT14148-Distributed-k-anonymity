import pandas as pd

def calculate_information_loss(original_df: pd.DataFrame, anonymized_df: pd.DataFrame, output_file=None) -> dict:
    qi_columns = ["Age", "Gender", "ZipCode"]

    total_cells = len(original_df) * len(qi_columns)
    changed_cells = 0

    original_qi = original_df[qi_columns].astype(str).reset_index(drop=True)
    anonymized_qi = anonymized_df[qi_columns].astype(str).reset_index(drop=True)

    for col in qi_columns:
        changed_cells += (original_qi[col] != anonymized_qi[col]).sum()

    loss_ratio = changed_cells / total_cells if total_cells > 0 else 0

    result = {
        "total_qi_cells": int(total_cells),
        "changed_qi_cells": int(changed_cells),
        "information_loss_ratio": round(loss_ratio, 4)
    }
    
    if output_file:
        with open(output_file, "w") as f:
            for key, value in result.items():
                f.write(f"{key}:{value}\n")

    return result