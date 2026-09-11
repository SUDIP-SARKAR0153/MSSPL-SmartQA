def generate_test_cases(requirement: str):
    """
    Generate manual QA test cases based on the requirement.
    """

    requirement_lower = requirement.lower()

    # -------------------------
    # LOGIN
    # -------------------------
    if any(keyword in requirement_lower for keyword in ["login", "log in", "sign in"]):

        return [
            {
                "test_case_id": "TC_LOGIN_001",
                "module": "Login",
                "test_case_type": "Positive",
                "test_case": "Login with valid email and password",
                "test_data": {
                    "email": "valid_user@example.com",
                    "password": "ValidPassword123"
                },
                "expected_result": "User should be successfully logged in and redirected to the account/dashboard page."
            },
            {
                "test_case_id": "TC_LOGIN_002",
                "module": "Login",
                "test_case_type": "Negative",
                "test_case": "Login with invalid email",
                "test_data": {
                    "email": "invalid@example.com",
                    "password": "ValidPassword123"
                },
                "expected_result": "An appropriate error message should be displayed and the user should not be logged in."
            },
            {
                "test_case_id": "TC_LOGIN_003",
                "module": "Login",
                "test_case_type": "Negative",
                "test_case": "Login with invalid password",
                "test_data": {
                    "email": "valid_user@example.com",
                    "password": "WrongPassword"
                },
                "expected_result": "An appropriate error message should be displayed and the user should not be logged in."
            },
            {
                "test_case_id": "TC_LOGIN_004",
                "module": "Login",
                "test_case_type": "Negative",
                "test_case": "Login with empty email",
                "test_data": {
                    "email": "",
                    "password": "ValidPassword123"
                },
                "expected_result": "Email validation message should be displayed and login should not proceed."
            },
            {
                "test_case_id": "TC_LOGIN_005",
                "module": "Login",
                "test_case_type": "Negative",
                "test_case": "Login with empty password",
                "test_data": {
                    "email": "valid_user@example.com",
                    "password": ""
                },
                "expected_result": "Password validation message should be displayed and login should not proceed."
            }
        ]

    # -------------------------
    # REGISTRATION
    # -------------------------
    elif any(keyword in requirement_lower for keyword in ["register", "registration", "sign up", "signup", "create account"]):

        return [
            {
                "test_case_id": "TC_REG_001",
                "module": "Registration",
                "test_case_type": "Positive",
                "test_case": "Register with valid user details",
                "test_data": {
                    "name": "John Doe",
                    "email": "john@example.com",
                    "password": "ValidPassword123"
                },
                "expected_result": "User should be successfully registered and an appropriate success message should be displayed."
            },
            {
                "test_case_id": "TC_REG_002",
                "module": "Registration",
                "test_case_type": "Negative",
                "test_case": "Register with an already registered email",
                "test_data": {
                    "name": "John Doe",
                    "email": "existing@example.com",
                    "password": "ValidPassword123"
                },
                "expected_result": "The system should prevent duplicate registration and display an appropriate error message."
            },
            {
                "test_case_id": "TC_REG_003",
                "module": "Registration",
                "test_case_type": "Negative",
                "test_case": "Register with invalid email format",
                "test_data": {
                    "name": "John Doe",
                    "email": "invalid-email",
                    "password": "ValidPassword123"
                },
                "expected_result": "Email validation message should be displayed and registration should not proceed."
            },
            {
                "test_case_id": "TC_REG_004",
                "module": "Registration",
                "test_case_type": "Negative",
                "test_case": "Register with empty mandatory fields",
                "test_data": {
                    "name": "",
                    "email": "",
                    "password": ""
                },
                "expected_result": "Mandatory field validation messages should be displayed and registration should not proceed."
            }
        ]

    # -------------------------
    # SEARCH
    # -------------------------
    elif any(keyword in requirement_lower for keyword in ["search", "find product", "search product"]):

        return [
            {
                "test_case_id": "TC_SEARCH_001",
                "module": "Search",
                "test_case_type": "Positive",
                "test_case": "Search using a valid keyword",
                "test_data": {
                    "keyword": "Laptop"
                },
                "expected_result": "Relevant search results matching the keyword should be displayed."
            },
            {
                "test_case_id": "TC_SEARCH_002",
                "module": "Search",
                "test_case_type": "Negative",
                "test_case": "Search using a keyword with no matching results",
                "test_data": {
                    "keyword": "XYZ12345"
                },
                "expected_result": "A proper 'No results found' message should be displayed."
            },
            {
                "test_case_id": "TC_SEARCH_003",
                "module": "Search",
                "test_case_type": "Negative",
                "test_case": "Search with an empty keyword",
                "test_data": {
                    "keyword": ""
                },
                "expected_result": "The system should handle the empty search appropriately without errors."
            },
            {
                "test_case_id": "TC_SEARCH_004",
                "module": "Search",
                "test_case_type": "Negative",
                "test_case": "Search using special characters",
                "test_data": {
                    "keyword": "@#$%"
                },
                "expected_result": "The system should handle special characters correctly without crashing."
            }
        ]

    # -------------------------
    # GENERIC FALLBACK
    # -------------------------
    else:

        return [
            {
                "test_case_id": "TC_GENERIC_001",
                "module": "General",
                "test_case_type": "Positive",
                "test_case": "Verify the requirement works with valid input",
                "test_data": "Valid input according to the requirement",
                "expected_result": "The system should successfully perform the expected functionality."
            },
            {
                "test_case_id": "TC_GENERIC_002",
                "module": "General",
                "test_case_type": "Negative",
                "test_case": "Verify the requirement with invalid input",
                "test_data": "Invalid input",
                "expected_result": "The system should reject invalid input and display an appropriate error message."
            },
            {
                "test_case_id": "TC_GENERIC_003",
                "module": "General",
                "test_case_type": "Negative",
                "test_case": "Verify the requirement with empty input",
                "test_data": "",
                "expected_result": "The system should validate mandatory input and prevent invalid processing."
            }
        ]