import sys
from pathlib import Path

import pandas as pd
import requests

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from anonymizer import anonymize_dataset, remove_direct_identifiers
from metrics import calculate_information_loss

NODE_ENDPOINTS = {
    "Node A": "http://127.0.0.1:5001/records",
    "Node B": "http://127.0.0.1:5002/records"
}

OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

K = 5


def fetch_node_records(node_name: str, endpoint: str, timeout: int = 3):
    """
    Fetch records from one distributed node.
    """
    try:
        response = requests.get(endpoint, timeout=timeout)
        response.raise_for_status()

        payload = response.json()
        records = payload.get("records", [])

        print(f"{node_name}: OK - {len(records)} records received")
        return records, None

    except requests.exceptions.RequestException as error:
        print(f"{node_name}: FAILED - {error}")
        return None, str(error)


def collect_distributed_records():
   
    all_records = []
    failed_nodes = {}

    print("\nConnecting to distributed nodes...\n")

    for node_name, endpoint in NODE_ENDPOINTS.items():
        records, error = fetch_node_records(node_name, endpoint)

        if error:
            failed_nodes[node_name] = error
        else:
            all_records.extend(records)

    if failed_nodes:
        return {
            "status": "FAIL",
            "records": all_records,
            "failed_nodes": failed_nodes
        }

    return {
        "status": "PASS",
        "records": all_records,
        "failed_nodes": {}
    }


def main():
    print("=" * 75)
    print("Distributed k-Anonymity Coordinator")
    print("=" * 75)

    collection_result = collect_distributed_records()

    if collection_result["status"] == "FAIL":
        print("\nWARNING: One or more distributed nodes are unavailable.")
        print("Failed nodes:", list(collection_result["failed_nodes"].keys()))
        print("\nCannot guarantee global k-anonymity on incomplete distributed data.")
        print("Anonymized output is BLOCKED.")
        print("=" * 75)
        return

    records = collection_result["records"]
    distributed_df = pd.DataFrame(records)

    print(f"\nTotal distributed records collected: {len(distributed_df)}")
    print(f"Checking global k-anonymity with k = {K}...\n")

    anonymization_result = anonymize_dataset(distributed_df, k=K)

    if anonymization_result["status"] == "PASS":
        anonymized_df = anonymization_result["anonymized_df"]
        group_counts = anonymization_result["group_counts"]
        strategy = anonymization_result["strategy"]

        original_without_ids = remove_direct_identifiers(distributed_df)
        metrics = calculate_information_loss(original_without_ids, anonymized_df)

        output_file = OUTPUT_DIR / "anonymized_result.csv"
        group_file = OUTPUT_DIR / "equivalence_classes.csv"
        metrics_file = OUTPUT_DIR / "metrics.csv"

        anonymized_df.to_csv(output_file, index=False)
        group_counts.to_csv(group_file, index=False)
        pd.DataFrame([metrics]).to_csv(metrics_file, index=False)

        print("Result: PASS")
        print("The distributed dataset satisfies k-anonymity.")

        print("\nSelected generalization strategy:")
        print(strategy)

        print("\nEquivalence classes:")
        print(group_counts.to_string(index=False))

        print("\nInformation Loss:")
        print(metrics)

        print("\nOutput files:")
        print(f"- {output_file}")
        print(f"- {group_file}")
        print(f"- {metrics_file}")

    else:
        print("Result: FAIL")
        print("The dataset cannot satisfy k-anonymity with current strategies.")
        print("\nFailing groups:")
        print(anonymization_result["failing_groups"].to_string(index=False))
        print("\nAnonymized output is BLOCKED.")

    print("=" * 75)


if __name__ == "__main__":
    main()