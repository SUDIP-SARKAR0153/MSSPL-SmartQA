import json
from datetime import datetime

from ai_engine import ask_ai


# ============================================================
# NORMALIZATION HELPERS
# ============================================================

def normalize_test_case_type(value):
    if str(value).strip().lower() == "positive":
        return "Positive"

    return "Negative"


def normalize_priority(value):
    value = str(value).strip().lower()

    if value == "critical":
        return "Critical"

    if value == "high":
        return "High"

    if value == "low":
        return "Low"

    return "Medium"


def normalize_coverage_level(value):
    value = str(value).strip().lower()

    if value == "core":
        return "Core"

    if value == "important":
        return "Important"

    if value == "extended":
        return "Extended"

    return "Edge"


def normalize_complexity(value):
    value = str(value).strip().lower()

    if value == "low":
        return "Low"

    if value == "high":
        return "High"

    return "Medium"


def normalize_coverage_score(value):
    try:
        score = int(value)
        return max(0, min(score, 100))
    except (ValueError, TypeError):
        return 0


# ============================================================
# TEST DATA CLEANING
# ============================================================

def clean_test_data(test_data):
    """
    Convert AI test data into a readable string
    matching the company's test case format.
    """

    if isinstance(test_data, dict):

        parts = []

        for key, value in test_data.items():

            readable_key = (
                str(key)
                .replace("_", " ")
                .title()
            )

            parts.append(
                f"{readable_key}: {value}"
            )

        return "; ".join(parts)

    if isinstance(test_data, list):

        return "; ".join(
            str(item)
            for item in test_data
        )

    if test_data is None:

        return "Required test data"

    return str(test_data)


# ============================================================
# BASIC QUALITY VALIDATION
# ============================================================

def is_valid_test_case(test_case):
    """
    Reject obviously malformed or incomplete AI test cases.
    """

    if not isinstance(test_case, dict):
        return False

    required_fields = [
        "test_case",
        "test_data",
        "expected_result"
    ]

    for field in required_fields:

        value = test_case.get(field)

        if value is None:
            return False

        if str(value).strip() == "":
            return False

    return True


# ============================================================
# DUPLICATE DETECTION
# ============================================================

def is_duplicate_case(existing_cases, new_case):
    """
    Prevent duplicate or almost identical test scenarios.
    """

    new_text = (
        str(new_case.get("test_case", ""))
        .strip()
        .lower()
    )

    for existing in existing_cases:

        existing_text = (
            str(existing.get("test_case", ""))
            .strip()
            .lower()
        )

        if new_text == existing_text:
            return True

    return False


# ============================================================
# MAIN AI ANALYSIS
# ============================================================

def analyze_requirement_with_ai(
    requirement: str,
    coverage_mode: str = "standard"
):

    prompt = f"""
You are MSSPL SmartQA.

You are an AI-powered assistant designed specifically
for professional Manual Software Testers.

Your task is to deeply understand the provided software
requirement and identify the COMPLETE set of meaningful
manual testing scenarios supported by that requirement.

============================================================
SOFTWARE REQUIREMENT
============================================================

{requirement}

============================================================
PRIMARY OBJECTIVE
============================================================

First understand the complete requirement.

Then identify ALL meaningful test scenarios supported
by the requirement.

There is NO TEST CASE COUNT LIMIT during this analysis.

Do NOT optimize for a fixed number of test cases.

Do NOT generate artificial scenarios just to increase
the number of test cases.

The complete scenario pool will later be filtered by
MSSPL SmartQA into:

Quick
Standard
Comprehensive

Therefore, IGNORE coverage_mode while creating the
complete scenario pool.

Current coverage_mode received from the application:

{coverage_mode}

This value must NOT restrict the AI analysis.

============================================================
MOST IMPORTANT RULE: REQUIREMENT IS THE SOURCE OF TRUTH
============================================================

You MUST stay grounded in the provided requirement.

Only generate a test scenario when the behavior is:

1. Explicitly stated in the requirement, OR
2. A direct and unavoidable consequence of the stated
   functionality.

Do NOT invent business rules.

Do NOT invent validation rules.

Do NOT invent technical specifications.

Do NOT invent exact limits.

Do NOT invent workflows.

Do NOT invent security policies.

Do NOT invent timeout values.

Do NOT invent retry counts.

Do NOT invent permissions.

Do NOT invent database behavior.

Do NOT invent UI behavior unless it is stated.

============================================================
EXAMPLES OF INFORMATION THAT MUST NOT BE INVENTED
============================================================

If the requirement says:

"User logs in with email and password."

Do NOT automatically create scenarios such as:

- password must contain 8 characters
- password must contain a number
- password must contain a special character
- email must have a specific maximum length
- login timeout after 30 seconds
- account locked after 3 attempts
- CAPTCHA appears
- password expires
- remember-me functionality

unless the requirement explicitly mentions them.

Instead, missing rules should be reported under:

"missing_information"

============================================================
MEANINGFUL NEGATIVE TESTING
============================================================

Negative scenarios are important, but they must remain
connected to the stated functionality.

For example:

Requirement:
"Email address must be unique."

Meaningful negative scenario:

"Attempt registration using an email address that already
exists."

That is valid because uniqueness is explicitly required.

But:

"Attempt registration with an email longer than 50 characters"

is NOT valid unless a 50-character limit is specified.

============================================================
FUNCTIONAL FLOW COVERAGE
============================================================

Read the ENTIRE requirement.

If multiple flows are described, cover all of them.

For example:

"Customer creates an account and then logs in using the
registered credentials."

The scenario pool should cover BOTH:

Registration
AND
Login

Do not focus only on registration.

============================================================
DUPLICATE SCENARIOS
============================================================

Do not create duplicate or nearly identical scenarios.

Each test case must provide meaningful additional coverage.

============================================================
TEST CASE CLASSIFICATION
============================================================

Every test case must contain:

priority

and

coverage_level

Priority values:

Critical
High
Medium
Low

Coverage level values:

Core
Important
Extended
Edge

============================================================
PRIORITY GUIDELINES
============================================================

Critical:
A fundamental required business flow.

High:
Important negative, validation, business-rule,
or alternate-flow scenarios.

Medium:
Additional meaningful functional coverage.

Low:
Less common but still meaningful edge scenarios.

Do not classify everything as Critical.

============================================================
COVERAGE LEVEL GUIDELINES
============================================================

Core:
Essential functionality explicitly required.

Important:
Important negative, validation, business-rule,
or alternate scenarios.

Extended:
Additional meaningful scenarios that improve coverage.

Edge:
Less common but valid scenarios supported by the requirement.

============================================================
COMPANY TEST CASE FORMAT
============================================================

MSSPL uses this test case format:

Date
Test Case ID
Module
Test Case Type
Test Case
Test Data
Expected Result

Priority and Coverage Level are INTERNAL SmartQA
metadata.

They are NOT company-facing columns.

The Python application will generate the Date.

Therefore:

DO NOT generate the date yourself.

============================================================
TEST DATA RULES
============================================================

Test data must match the actual test scenario.

For example:

Scenario:
"Attempt login with incorrect password."

Correct:

Email: registered@example.com
Password: IncorrectPassword

Do not provide test data that contradicts the scenario.

============================================================
EXPECTED RESULT RULES
============================================================

Expected results must be based on the requirement.

Do not claim unsupported UI behavior.

For example, if the requirement only says:

"User can log in successfully."

Use:

"User should be logged in successfully."

Do not invent:

"User should be redirected to dashboard."

unless the requirement explicitly says so.

============================================================
COVERAGE SCORE
============================================================

coverage_score represents estimated requirement coverage
provided by the generated scenario pool.

It is NOT software quality.

Use an integer between 0 and 100.

Do not automatically return 100.

============================================================
MISSING INFORMATION
============================================================

List genuinely missing or unclear requirements.

Examples:

- Password complexity rules are not specified.
- Login failure behavior is not specified.
- Email format validation rules are not specified.

Do not convert missing information into invented test cases.

============================================================
COVERAGE GAPS
============================================================

Identify meaningful areas that cannot be fully tested because
the requirement does not provide enough information.

============================================================
OUTPUT FORMAT
============================================================

Return ONLY valid JSON.

Return exactly:

{{
    "module": "Relevant module",
    "actor": "Primary actor",
    "complexity": "Low / Medium / High",
    "coverage_score": 0,
    "scenario_count": 0,

    "functional_requirements": [
        "Requirement explicitly identified from the story"
    ],

    "qa_risks": [
        "Important QA risk supported by the requirement"
    ],

    "missing_information": [
        "Missing or unclear information"
    ],

    "coverage_gaps": [
        "Potential remaining coverage gap"
    ],

    "test_cases": [
        {{
            "test_case_id": "TC_001",
            "module": "Module name",
            "test_case_type": "Positive",
            "test_case": "Manual test scenario",
            "test_data": "Required test data",
            "expected_result": "Specific expected result",
            "priority": "Critical",
            "coverage_level": "Core"
        }}
    ]
}}

============================================================
FINAL SELF-CHECK BEFORE RETURNING JSON
============================================================

Before producing the final JSON:

1. Did I cover every explicit functional flow?

2. Did I avoid inventing unsupported validation rules?

3. Did I avoid inventing exact limits?

4. Did I avoid duplicate scenarios?

5. Does every test case have appropriate test data?

6. Does every expected result come from the requirement?

7. Does every test case have priority?

8. Does every test case have coverage_level?

9. Did I consider meaningful positive and negative scenarios?

10. Did I avoid creating artificial scenarios?

Return ONLY JSON.
"""

    response = ask_ai(prompt)

    # ========================================================
    # PARSE AI RESPONSE
    # ========================================================

    try:

        result = json.loads(response)

    except json.JSONDecodeError:

        return {
            "module": "AI Analysis",
            "actor": "User",
            "complexity": "Medium",
            "coverage_score": 0,
            "scenario_count": 0,
            "functional_requirements": [],
            "qa_risks": [],
            "missing_information": [
                "AI returned an unexpected response format."
            ],
            "coverage_gaps": [
                "Coverage could not be calculated."
            ],
            "test_cases": [],
            "raw_ai_response": response
        }

    # ========================================================
    # SAFE DEFAULTS
    # ========================================================

    result.setdefault(
        "module",
        "Unknown"
    )

    result.setdefault(
        "actor",
        "User"
    )

    result.setdefault(
        "complexity",
        "Medium"
    )

    result.setdefault(
        "coverage_score",
        0
    )

    result.setdefault(
        "scenario_count",
        0
    )

    result.setdefault(
        "functional_requirements",
        []
    )

    result.setdefault(
        "qa_risks",
        []
    )

    result.setdefault(
        "missing_information",
        []
    )

    result.setdefault(
        "coverage_gaps",
        []
    )

    result.setdefault(
        "test_cases",
        []
    )

    # ========================================================
    # NORMALIZE ANALYSIS
    # ========================================================

    result["complexity"] = normalize_complexity(
        result.get("complexity")
    )

    result["coverage_score"] = normalize_coverage_score(
        result.get("coverage_score")
    )

    # ========================================================
    # TEST CASE PROCESSING
    # ========================================================

    ai_test_cases = result.get(
        "test_cases",
        []
    )

    if not isinstance(ai_test_cases, list):
        ai_test_cases = []

    normalized_cases = []

    today = datetime.now().strftime(
        "%d-%m-%Y"
    )

    for test_case in ai_test_cases:

        if not is_valid_test_case(test_case):
            continue

        # Prevent duplicates
        if is_duplicate_case(
            normalized_cases,
            test_case
        ):
            continue

        normalized_case = {}

        # ----------------------------------------------------
        # COMPANY-FACING FIELDS
        # ----------------------------------------------------

        # Date is ALWAYS generated by Python.
        normalized_case["date"] = today

        normalized_case["test_case_id"] = (
            f"TC_{len(normalized_cases) + 1:03d}"
        )

        normalized_case["module"] = test_case.get(
            "module",
            result.get(
                "module",
                "Unknown"
            )
        )

        normalized_case["test_case_type"] = (
            normalize_test_case_type(
                test_case.get(
                    "test_case_type"
                )
            )
        )

        normalized_case["test_case"] = str(
            test_case.get(
                "test_case"
            )
        ).strip()

        normalized_case["test_data"] = (
            clean_test_data(
                test_case.get(
                    "test_data"
                )
            )
        )

        normalized_case["expected_result"] = str(
            test_case.get(
                "expected_result"
            )
        ).strip()

        # ----------------------------------------------------
        # INTERNAL SMARTQA METADATA
        # ----------------------------------------------------

        normalized_case["priority"] = (
            normalize_priority(
                test_case.get(
                    "priority"
                )
            )
        )

        normalized_case["coverage_level"] = (
            normalize_coverage_level(
                test_case.get(
                    "coverage_level"
                )
            )
        )

        normalized_cases.append(
            normalized_case
        )

    # ========================================================
    # FINAL RESULT
    # ========================================================

    result["test_cases"] = normalized_cases

    result["scenario_count"] = (
        len(normalized_cases)
    )

    return result