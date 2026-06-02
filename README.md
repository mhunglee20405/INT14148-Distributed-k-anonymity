<<<<<<< HEAD
# INT14148-Distributed-k-anonymity
=======
# Distributed k-Anonymity for Patient Records

## Overview

This project simulates a distributed privacy-preserving patient data publishing system using k-anonymity.

The system has two distributed sites:

- Node A stores `data/site_a.csv`
- Node B stores `data/site_b.csv`
- Coordinator collects records from both nodes and checks global k-anonymity before publishing anonymized data.

Default value:

```text
k = 5
```

````

## 2. Dataset

The dataset contains patient records distributed across two sites.

Schema:

| Attribute | Role |
|---|---|
| PatientID | Direct Identifier |
| Name | Direct Identifier |
| Age | Quasi-Identifier |
| Gender | Quasi-Identifier |
| ZipCode | Quasi-Identifier |
| Disease | Sensitive Attribute |

Direct identifiers `PatientID` and `Name` are removed before publishing.

Quasi-identifiers `Age`, `Gender`, and `ZipCode` are used to form equivalence classes.

`Disease` is preserved for medical analysis.

## 3. Architecture

```text
Node A  ----\
             ---> Coordinator ---> output/anonymized_result.csv
Node B  ----/

Attacker Script ---> Privacy attack simulation
````

## 4. Installation

```bash
pip install -r requirements.txt
```

## 5. Run the System

Open three terminals.

Terminal 1:

```bash
python nodes/node_a.py
```

Terminal 2:

```bash
python nodes/node_b.py
```

Terminal 3:

```bash
python coordinator/coordinator.py
```

Expected result:

```text
Node A: OK - 20 records received
Node B: OK - 20 records received
Total distributed records collected: 40
Result: PASS
```

Generated files:

```text
output/anonymized_result.csv
output/equivalence_classes.csv
output/metrics.csv
```

## 6. Hacker Mode

Run:

```bash
python attacker/hacker_mode.py
```

Expected result:

```text
[Attack 1] RAW data: LEAK FOUND
[Attack 2] ANONYMIZED data: ATTACK BLOCKED BY k-ANONYMITY
[Attack 3] Output leak check: PASS
```

## 7. Failure Scenario: Kill Node B

Stop Node B by pressing:

```text
Ctrl + C
```

Then run the coordinator again:

```bash
python coordinator/coordinator.py
```

Expected result:

```text
Node B: FAILED
Cannot guarantee global k-anonymity on incomplete distributed data.
Anonymized output is BLOCKED.
```

## 8. Threat Model

The attacker may know quasi-identifiers of a target patient, such as age, gender, and zipcode.

The attacker tries to re-identify the patient or infer the patient's disease from the published dataset.

The system protects against this by:

- removing direct identifiers,
- generalizing quasi-identifiers,
- enforcing k-anonymity globally across distributed sites,
- blocking publication when a node is unavailable.

## 9. Limitations

This project focuses on k-anonymity only.

It does not fully protect against:

- homogeneity attacks,
- background knowledge attacks,
- direct compromise of raw node data.

Future work can extend the system with l-diversity or t-closeness.
>>>>>>> be6d4fb (Initial commit - distributed k-anonymity project)
