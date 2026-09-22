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
    Convert AI test data into a readable string.
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
# BASIC VALIDATION
# ============================================================

def is_valid_test_case(test_case):
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

def normalize_text(value):
    return " ".join(
        str(value)
        .strip()
        .lower()
        .split()
    )


def is_duplicate_case(existing_cases, new_case):
    """
    Prevent duplicate scenarios.
    """

    new_text = normalize_text(
        new_case.get("test_case", "")
    )

    new_module = normalize_text(
        new_case.get("module", "")
    )

    for existing in existing_cases:

        existing_text = normalize_text(
            existing.get("test_case", "")
        )

        existing_module = normalize_text(
            existing.get("module", "")
        )

        if (
            new_text == existing_text
            and new_module == existing_module
        ):
            return True

    return False


# ============================================================
# SAFE JSON PARSING
# ============================================================

def parse_ai_json(response):
    """
    Safely parse JSON returned by Ollama.
    """

    try:
        return json.loads(response)

    except json.JSONDecodeError:

        # Try extracting the first JSON object.
        start = response.find("{")
        end = response.rfind("}")

        if start != -1 and end != -1 and end > start:

            try:
                return json.loads(
                    response[start:end + 1]
                )
            except json.JSONDecodeError:
                pass

    return None


# ============================================================
# STAGE 1
# REQUIREMENT / MODULE DISCOVERY
# ============================================================

def discover_requirement_modules(requirement):
    """
    First AI stage.

    Understand the complete requirement and identify
    all meaningful modules/features before generating
    test cases.
    """

    prompt = f"""
You are MSSPL SmartQA, an AI assistant for professional
manual software testers.

Your FIRST task is NOT to generate test cases.

Your task is to deeply analyze the COMPLETE software
requirement and identify ALL meaningful modules,
features, screens, workflows, or functional areas
described in it.

============================================================
COMPLETE SOFTWARE REQUIREMENT
============================================================

{requirement}

============================================================
IMPORTANT
============================================================

Read the ENTIRE requirement before responding.

Do not stop after finding the first module.

For a large requirement such as an administration portal,
the requirement may contain many areas such as:

- Authentication
- Parent management
- Wallet
- Children
- Meal ordering
- Teachers
- Students
- Schools
- Calendar
- Menu
- Products
- Classes
- Reports
- Navigation
- Session management

These are only examples.

You MUST identify the actual modules present in the
provided requirement.

============================================================
GROUNDING RULE
============================================================

The requirement is the source of truth.

Do NOT invent modules.

Only identify a module when its functionality is
explicitly present in the requirement.

Do NOT invent:

- business rules
- validation rules
- technical specifications
- database behavior
- permissions
- timeout values
- retry counts
- security policies
- UI behavior not mentioned
- exact limits

============================================================
MODULE REQUIREMENTS
============================================================

For every identified module provide:

1. module name
2. concise description
3. actors involved, if explicitly stated or directly
   inferable
4. the exact relevant requirement content needed to
   understand that module
5. important functional areas within that module

Do not generate test cases yet.

============================================================
OUTPUT
============================================================

Return ONLY valid JSON.

Use exactly this structure:

{{
    "modules": [
        {{
            "module": "Module name",
            "description": "What this module does",
            "actor": "Primary actor",
            "requirement_excerpt": "Relevant requirement content",
            "functional_areas": [
                "Functional area 1",
                "Functional area 2"
            ]
        }}
    ],
    "global_missing_information": [
        "Missing or unclear requirement"
    ]
}}

The module list must cover the COMPLETE requirement.

Do not return only the first module.
"""

    response = ask_ai(prompt)

    result = parse_ai_json(response)

    if not isinstance(result, dict):
        return {
            "modules": [],
            "global_missing_information": [
                "AI returned an unexpected module analysis."
            ]
        }

    modules = result.get("modules", [])

    if not isinstance(modules, list):
        modules = []

    cleaned_modules = []

    for module in modules:

        if not isinstance(module, dict):
            continue

        name = str(
            module.get("module", "")
        ).strip()

        if not name:
            continue

        cleaned_modules.append({
            "module": name,
            "description": str(
                module.get("description", "")
            ).strip(),
            "actor": str(
                module.get("actor", "User")
            ).strip(),
            "requirement_excerpt": str(
                module.get("requirement_excerpt", "")
            ).strip(),
            "functional_areas": (
                module.get("functional_areas", [])
                if isinstance(
                    module.get("functional_areas", []),
                    list
                )
                else []
            )
        })

    return {
        "modules": cleaned_modules,
        "global_missing_information": (
            result.get(
                "global_missing_information",
                []
            )
            if isinstance(
                result.get(
                    "global_missing_information",
                    []
                ),
                list
            )
            else []
        )
    }


# ============================================================
# STAGE 2
# MODULE-FOCUSED TEST SCENARIO GENERATION
# ============================================================

def generate_module_test_cases(
    module_batch,
    global_missing_information
):
    """
    Generate test cases for a focused group of modules.

    Multiple modules are processed in one AI call to reduce
    latency while keeping the context focused.
    """

    module_json = json.dumps(
        module_batch,
        ensure_ascii=False,
        indent=2
    )

    prompt = f"""
You are MSSPL SmartQA.

You are an expert manual software testing assistant.

Your task is to generate the COMPLETE set of meaningful
manual test scenarios for the supplied functional modules.

============================================================
MODULES TO ANALYZE
============================================================

{module_json}

============================================================
GLOBAL MISSING INFORMATION
============================================================

{json.dumps(
    global_missing_information,
    ensure_ascii=False,
    indent=2
)}

============================================================
PRIMARY OBJECTIVE
============================================================

Analyze EVERY supplied module.

Do NOT focus on only the first module.

For EACH module, identify all meaningful scenarios
supported by its requirement excerpt.

Generate scenarios for all meaningful functionality
described in the module.

There is NO artificial test-case count limit.

Do NOT create artificial cases simply to increase the
number of scenarios.

============================================================
REQUIREMENT IS THE SOURCE OF TRUTH
============================================================

Only generate a scenario when it is:

1. Explicitly stated in the requirement, OR
2. A direct and unavoidable consequence of the stated
   functionality.

Do NOT invent:

- business rules
- validation rules
- technical specifications
- exact limits
- timeout values
- retry counts
- permissions
- database behavior
- unsupported security rules
- unsupported UI behavior
- unsupported workflows

============================================================
NEGATIVE TESTING
============================================================

Negative testing is required where the requirement
supports it.

Example:

If the requirement says:

"Student cannot be deleted without confirmation."

Valid negative scenario:

"Attempt to delete a student and cancel the confirmation."

But do NOT invent:

"Delete fails after 3 attempts"

unless that behavior is specified.

============================================================
COVERAGE
============================================================

Where supported by the requirement, consider:

- Main functional flow
- Alternate flow
- Negative flow
- Boundary behavior explicitly described
- Search
- Clear
- Sort
- Filter
- Add
- Edit
- Delete
- Confirmation
- Navigation
- State changes
- Empty states
- Required fields
- Existing-data behavior
- Date behavior
- Session behavior
- Role behavior

ONLY include an area when it is actually supported
by the module requirement.

============================================================
IMPORTANT EXAMPLE
============================================================

If a login requirement says:

"Admin logs in using username and password."

Generate:

- successful login
- invalid username/password behavior IF the requirement
  specifies it

Do NOT invent:

- password must contain 8 characters
- password must contain a number
- password must contain a special character
- account locks after 3 attempts
- CAPTCHA
- password expiration
- login timeout

unless specified.

============================================================
TEST CASE FORMAT
============================================================

Every test case must contain:

- module
- test_case_type
- test_case
- test_data
- expected_result
- priority
- coverage_level

Priority:

Critical
High
Medium
Low

Coverage level:

Core
Important
Extended
Edge

Do not classify every scenario as Critical.

============================================================
TEST DATA
============================================================

Test data must match the scenario.

Do not create contradictory test data.

============================================================
EXPECTED RESULT
============================================================

Expected results MUST be supported by the requirement.

Do not invent redirects, messages, UI states, database
changes, or technical behavior unless stated.

============================================================
MISSING INFORMATION
============================================================

If an important rule is missing from the requirement,
report it under missing_information.

Do NOT convert missing information into an invented
test case.

============================================================
OUTPUT
============================================================

Return ONLY valid JSON.

Use this structure:

{{
    "modules": [
        {{
            "module": "Module name",
            "actor": "Primary actor",
            "complexity": "Low / Medium / High",
            "coverage_score": 0,
            "functional_requirements": [
                "Explicit functional requirement"
            ],
            "qa_risks": [
                "Requirement-supported QA risk"
            ],
            "missing_information": [
                "Missing information"
            ],
            "coverage_gaps": [
                "Coverage gap caused by unclear requirement"
            ],
            "test_cases": [
                {{
                    "module": "Module name",
                    "test_case_type": "Positive",
                    "test_case": "Manual test scenario",
                    "test_data": "Required test data",
                    "expected_result": "Expected result",
                    "priority": "Critical",
                    "coverage_level": "Core"
                }}
            ]
        }}
    ]
}}

FINAL CHECK:

1. Did I analyze EVERY supplied module?
2. Did I cover every explicit functional flow?
3. Did I avoid invented rules?
4. Did I include meaningful negative scenarios?
5. Did I avoid duplicates?
6. Does every test case have relevant test data?
7. Is every expected result requirement-based?
8. Did I keep module names accurate?
9. Did I avoid artificial scenarios?
10. Did I report missing information separately?

Return ONLY JSON.
"""

    response = ask_ai(prompt)

    result = parse_ai_json(response)

    if not isinstance(result, dict):
        return {
            "modules": []
        }

    modules = result.get("modules", [])

    if not isinstance(modules, list):
        modules = []

    return {
        "modules": modules
    }


# ============================================================
# MAIN ANALYSIS
# ============================================================

def analyze_requirement_with_ai(
    requirement: str,
    coverage_mode: str = "standard"
):
    """
    Full MSSPL SmartQA analysis pipeline.

    Stage 1:
        Discover all modules.

    Stage 2:
        Generate test scenarios for module batches.

    Stage 3:
        Normalize, deduplicate and combine results.
    """

    if not requirement or not requirement.strip():
        return {
            "module": "Requirement Analysis",
            "actor": "User",
            "complexity": "Low",
            "coverage_score": 0,
            "scenario_count": 0,
            "functional_requirements": [],
            "qa_risks": [],
            "missing_information": [
                "Requirement is empty."
            ],
            "coverage_gaps": [],
            "test_cases": []
        }

    # ========================================================
    # STAGE 1: MODULE DISCOVERY
    # ========================================================

    print("\n==============================================")
    print("MSSPL SmartQA - Module Discovery")
    print("==============================================")

    discovery = discover_requirement_modules(
        requirement
    )

    modules = discovery.get(
        "modules",
        []
    )

    global_missing_information = discovery.get(
        "global_missing_information",
        []
    )

    print(
        f"Modules identified: {len(modules)}"
    )

    for index, module in enumerate(
        modules,
        start=1
    ):
        print(
            f"{index}. {module.get('module')}"
        )

    if not modules:
        return {
            "module": "Requirement Analysis",
            "actor": "User",
            "complexity": "Medium",
            "coverage_score": 0,
            "scenario_count": 0,
            "functional_requirements": [],
            "qa_risks": [],
            "missing_information": [
                "AI could not identify modules from the requirement."
            ],
            "coverage_gaps": [
                "Module discovery failed."
            ],
            "test_cases": []
        }

    # ========================================================
    # STAGE 2: MODULE BATCH GENERATION
    # ========================================================

    all_module_results = []

    # Process several modules per AI request.
    # This reduces latency compared with one request per module.
    batch_size = 4

    total_batches = (
        (len(modules) + batch_size - 1)
        // batch_size
    )

    for batch_index in range(
        0,
        len(modules),
        batch_size
    ):

        batch = modules[
            batch_index:
            batch_index + batch_size
        ]

        current_batch_number = (
            batch_index // batch_size
        ) + 1

        print(
            f"\nAnalyzing module batch "
            f"{current_batch_number}/{total_batches}"
        )

        result = generate_module_test_cases(
            batch,
            global_missing_information
        )

        batch_modules = result.get(
            "modules",
            []
        )

        if isinstance(
            batch_modules,
            list
        ):
            all_module_results.extend(
                batch_modules
            )

    # ========================================================
    # STAGE 3: COMBINE RESULTS
    # ========================================================

    normalized_cases = []

    functional_requirements = []
    qa_risks = []
    missing_information = list(
        global_missing_information
    )
    coverage_gaps = []

    module_names = []
    actors = []
    complexity_values = []
    coverage_scores = []

    today = datetime.now().strftime(
        "%d-%m-%Y"
    )

    # ========================================================
    # COLLECT MODULE METADATA
    # ========================================================

    for module_result in all_module_results:

        if not isinstance(
            module_result,
            dict
        ):
            continue

        module_name = str(
            module_result.get(
                "module",
                ""
            )
        ).strip()

        if module_name:
            module_names.append(
                module_name
            )

        actor = str(
            module_result.get(
                "actor",
                "User"
            )
        ).strip()

        if actor:
            actors.append(actor)

        complexity_values.append(
            normalize_complexity(
                module_result.get(
                    "complexity",
                    "Medium"
                )
            )
        )

        coverage_scores.append(
            normalize_coverage_score(
                module_result.get(
                    "coverage_score",
                    0
                )
            )
        )

        for item in module_result.get(
            "functional_requirements",
            []
        ):

            if str(item).strip():
                functional_requirements.append(
                    str(item).strip()
                )

        for item in module_result.get(
            "qa_risks",
            []
        ):

            if str(item).strip():
                qa_risks.append(
                    str(item).strip()
                )

        for item in module_result.get(
            "missing_information",
            []
        ):

            if str(item).strip():
                missing_information.append(
                    str(item).strip()
                )

        for item in module_result.get(
            "coverage_gaps",
            []
        ):

            if str(item).strip():
                coverage_gaps.append(
                    str(item).strip()
                )

        ai_test_cases = module_result.get(
            "test_cases",
            []
        )

        if not isinstance(
            ai_test_cases,
            list
        ):
            continue

        for test_case in ai_test_cases:

            if not is_valid_test_case(
                test_case
            ):
                continue

            if is_duplicate_case(
                normalized_cases,
                test_case
            ):
                continue

            case_module = str(
                test_case.get(
                    "module",
                    module_name or "Unknown"
                )
            ).strip()

            normalized_case = {
                "date": today,

                "test_case_id": (
                    f"TC_{len(normalized_cases) + 1:03d}"
                ),

                "module": (
                    case_module
                    if case_module
                    else "Unknown"
                ),

                "test_case_type": (
                    normalize_test_case_type(
                        test_case.get(
                            "test_case_type"
                        )
                    )
                ),

                "test_case": str(
                    test_case.get(
                        "test_case"
                    )
                ).strip(),

                "test_data": clean_test_data(
                    test_case.get(
                        "test_data"
                    )
                ),

                "expected_result": str(
                    test_case.get(
                        "expected_result"
                    )
                ).strip(),

                "priority": (
                    normalize_priority(
                        test_case.get(
                            "priority"
                        )
                    )
                ),

                "coverage_level": (
                    normalize_coverage_level(
                        test_case.get(
                            "coverage_level"
                        )
                    )
                )
            }

            normalized_cases.append(
                normalized_case
            )

    # ========================================================
    # REMOVE DUPLICATES FROM METADATA
    # ========================================================

    def unique_list(values):
        result = []
        seen = set()

        for value in values:

            normalized = normalize_text(
                value
            )

            if not normalized:
                continue

            if normalized in seen:
                continue

            seen.add(normalized)
            result.append(value)

        return result

    module_names = unique_list(
        module_names
    )

    actors = unique_list(
        actors
    )

    functional_requirements = unique_list(
        functional_requirements
    )

    qa_risks = unique_list(
        qa_risks
    )

    missing_information = unique_list(
        missing_information
    )

    coverage_gaps = unique_list(
        coverage_gaps
    )

    # ========================================================
    # OVERALL COMPLEXITY
    # ========================================================

    if "High" in complexity_values:
        overall_complexity = "High"

    elif "Medium" in complexity_values:
        overall_complexity = "Medium"

    else:
        overall_complexity = "Low"

    # ========================================================
    # OVERALL COVERAGE SCORE
    # ========================================================

    if coverage_scores:
        overall_coverage_score = round(
            sum(coverage_scores)
            / len(coverage_scores)
        )
    else:
        overall_coverage_score = 0

    # ========================================================
    # MODULE COVERAGE SAFETY CHECK
    # ========================================================

    discovered_module_names = {
        normalize_text(
            module.get(
                "module",
                ""
            )
        )
        for module in modules
        if module.get("module")
    }

    generated_module_names = {
        normalize_text(
            case.get(
                "module",
                ""
            )
        )
        for case in normalized_cases
        if case.get("module")
    }

    modules_without_cases = (
        discovered_module_names
        - generated_module_names
    )

    if modules_without_cases:

        coverage_gaps.append(
            "The following identified modules did not "
            "produce test cases: "
            + ", ".join(
                sorted(
                    modules_without_cases
                )
            )
        )

    # ========================================================
    # FINAL MODULE LABEL
    # ========================================================

    if len(module_names) == 1:
        final_module = module_names[0]

    elif module_names:
        final_module = (
            f"Multiple Modules ({len(module_names)})"
        )

    else:
        final_module = "Requirement Analysis"

    # ========================================================
    # FINAL ACTOR
    # ========================================================

    if len(actors) == 1:
        final_actor = actors[0]

    elif actors:
        final_actor = ", ".join(actors)

    else:
        final_actor = "User"

    # ========================================================
    # FINAL RESULT
    # ========================================================

    final_result = {
        "module": final_module,

        "actor": final_actor,

        "complexity": overall_complexity,

        "coverage_score": (
            normalize_coverage_score(
                overall_coverage_score
            )
        ),

        "scenario_count": len(
            normalized_cases
        ),

        "functional_requirements": (
            functional_requirements
        ),

        "qa_risks": qa_risks,

        "missing_information": (
            missing_information
        ),

        "coverage_gaps": (
            coverage_gaps
        ),

        "test_cases": normalized_cases
    }

    print("\n==============================================")
    print("MSSPL SmartQA - Analysis Complete")
    print("==============================================")

    print(
        f"Modules discovered: "
        f"{len(module_names)}"
    )

    print(
        f"Test cases generated: "
        f"{len(normalized_cases)}"
    )

    print(
        f"Coverage score: "
        f"{final_result['coverage_score']}"
    )

    return final_result