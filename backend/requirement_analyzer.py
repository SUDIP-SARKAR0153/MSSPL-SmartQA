def analyze_requirement(requirement: str):
    """
    Analyze a requirement from a Manual QA perspective.
    """

    requirement_lower = requirement.lower()

    # -------------------------
    # LOGIN
    # -------------------------
    if any(keyword in requirement_lower for keyword in [
        "login",
        "log in",
        "sign in"
    ]):

        return {
            "requirement": requirement,
            "module": "Login",
            "actor": "Registered User",
            "functional_requirements": [
                "User should be able to login with valid credentials.",
                "Invalid credentials should display an appropriate error message."
            ],
            "qa_risks": [
                "Invalid email",
                "Invalid password",
                "Empty email",
                "Empty password"
            ],
            "missing_information": [
                "Password validation rules are not specified.",
                "Maximum email length is not specified.",
                "Exact error message is not specified."
            ]
        }

    # -------------------------
    # REGISTRATION
    # -------------------------
    elif any(keyword in requirement_lower for keyword in [
        "register",
        "registration",
        "sign up",
        "signup",
        "create account"
    ]):

        return {
            "requirement": requirement,
            "module": "Registration",
            "actor": "New Customer",
            "functional_requirements": [
                "User should be able to create a new account with valid details.",
                "The system should prevent registration with an already registered email."
            ],
            "qa_risks": [
                "Invalid email format",
                "Duplicate email",
                "Empty mandatory fields",
                "Weak password"
            ],
            "missing_information": [
                "Password validation rules are not specified.",
                "Email uniqueness rules are not specified.",
                "Required fields are not clearly specified.",
                "Exact validation and error messages are not specified."
            ]
        }

    # -------------------------
    # SEARCH
    # -------------------------
    elif any(keyword in requirement_lower for keyword in [
        "search",
        "find product",
        "search product"
    ]):

        return {
            "requirement": requirement,
            "module": "Search",
            "actor": "User",
            "functional_requirements": [
                "User should be able to search using a valid keyword.",
                "The system should display relevant search results."
            ],
            "qa_risks": [
                "Empty search",
                "No matching results",
                "Special characters",
                "Very long search input"
            ],
            "missing_information": [
                "Maximum search length is not specified.",
                "Search behavior for special characters is not specified.",
                "Expected behavior when no results are found is not specified."
            ]
        }

    # -------------------------
    # GENERIC FALLBACK
    # -------------------------
    else:

        return {
            "requirement": requirement,
            "module": "General",
            "actor": "User",
            "functional_requirements": [
                "The system should satisfy the functionality described in the requirement."
            ],
            "qa_risks": [
                "Invalid input",
                "Missing mandatory input",
                "Unexpected user behavior"
            ],
            "missing_information": [
                "Detailed acceptance criteria are not specified.",
                "Validation rules are not specified.",
                "Expected error behavior is not specified."
            ]
        }