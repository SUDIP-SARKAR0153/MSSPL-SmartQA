import { useState } from "react";
import "./App.css";

function App() {
  const [requirement, setRequirement] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [coverageMode, setCoverageMode] = useState("standard");
  const [analysisCompleted, setAnalysisCompleted] = useState(false);

  // ============================================================
  // ANALYZE REQUIREMENT
  // ============================================================

  const analyzeRequirement = async () => {
    if (!requirement.trim()) {
      alert("Please enter a requirement or user story.");
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/analyze-requirement",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            requirement: requirement,
            coverage_mode: coverageMode,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to analyze requirement");
      }

      const data = await response.json();

      setResult(data);

      // AI analysis has completed.
      // Coverage selection will now happen locally.
      setAnalysisCompleted(true);
    } catch (error) {
      console.error("MSSPL SmartQA Error:", error);

      alert(
        "MSSPL SmartQA Error:\n\n" +
          error.message +
          "\n\nPlease check the browser console for more details."
      );
    } finally {
      setLoading(false);
    }
  };

  // ============================================================
  // LOCAL TEST CASE FILTERING
  // IMPORTANT:
  // No AI call happens here.
  // ============================================================

  const getFilteredTestCases = () => {
    if (!result || !result.test_cases) {
      return [];
    }

    const testCases = result.test_cases;

    // ----------------------------------------------------------
    // QUICK
    // Critical + High priority
    // ----------------------------------------------------------

    if (coverageMode === "quick") {
      return testCases.filter(
        (testCase) =>
          testCase.priority === "Critical" ||
          testCase.priority === "High"
      );
    }

    // ----------------------------------------------------------
    // STANDARD
    // Critical + High + Medium
    // ----------------------------------------------------------

    if (coverageMode === "standard") {
      return testCases.filter(
        (testCase) =>
          testCase.priority === "Critical" ||
          testCase.priority === "High" ||
          testCase.priority === "Medium"
      );
    }

    // ----------------------------------------------------------
    // COMPREHENSIVE
    // All meaningful cases, maximum 35 displayed
    // ----------------------------------------------------------

    if (coverageMode === "comprehensive") {
      return testCases.slice(0, 35);
    }

    return testCases;
  };

  // ============================================================
  // CLEAR
  // ============================================================

  const clearAll = () => {
    setRequirement("");
    setResult(null);
    setAnalysisCompleted(false);
    setCoverageMode("standard");
  };

  // ============================================================
  // COPY RESULTS
  // ============================================================

  const copyResults = () => {
    if (!result) return;

    navigator.clipboard.writeText(
      JSON.stringify(result, null, 2)
    );

    alert("Results copied successfully!");
  };

  // ============================================================
  // RENDER
  // ============================================================

  return (
    <div className="app">

      {/* ======================================================
          HEADER
      ====================================================== */}

      <header className="header">
        <div className="header-inner">

          <div className="brand">

            <div className="brand-icon">
              🧪
            </div>

            <div>
              <h1>MSSPL SmartQA</h1>

              <p>
                AI-Powered Assistant for Manual Testing
              </p>
            </div>

          </div>

          <div className="status">

            <span className="status-dot"></span>

            AI Assistant Online

          </div>

        </div>
      </header>


      {/* ======================================================
          MAIN CONTENT
      ====================================================== */}

      <main className="container">

        {/* ====================================================
            HERO
        ==================================================== */}

        <section className="hero">

          <div className="hero-badge">
            ✨ SMART QA INTELLIGENCE
          </div>

          <h2>
            Turn Requirements into
            <br />
            <span>QA Intelligence</span>
          </h2>

          <p>
            Analyze requirements, identify QA risks, discover missing
            information, and generate actionable testing insights faster.
          </p>

        </section>


        {/* ====================================================
            REQUIREMENT INPUT
        ==================================================== */}

        <section className="input-card">

          <div className="input-card-header">

            <div>

              <h2>
                Requirement / User Story
              </h2>

              <p>
                Enter or paste your requirement below to start the analysis.
              </p>

            </div>

            <div className="ai-label">
              🤖 AI Powered
            </div>

          </div>


          {/* REQUIREMENT TEXTAREA */}

          <textarea
            value={requirement}
            onChange={(e) => {
              setRequirement(e.target.value);

              // New requirement means a new analysis is required.
              setAnalysisCompleted(false);
            }}
            placeholder="Example: As a registered user, I want to login using my email and password so that I can securely access my account."
          />


          {/* ==================================================
              COVERAGE MODE
          ================================================== */}

          <div className="coverage-mode-section">

            <div className="coverage-mode-header">

              <div>

                <h3>
                  Test Coverage Level
                </h3>

                <p>
                  Choose how deeply MSSPL SmartQA should display
                  the generated test scenarios.
                </p>

              </div>

              <span className="coverage-ai-badge">
                🧠 Smart Filtering
              </span>

            </div>


            <div className="coverage-mode-grid">

              {/* ==================================================
                  QUICK
              ================================================== */}

              <button
                className={`coverage-mode-card ${
                  coverageMode === "quick"
                    ? "active"
                    : ""
                }`}
                onClick={() =>
                  setCoverageMode("quick")
                }
                type="button"
              >

                <div className="coverage-mode-icon">
                  ⚡
                </div>

                <div className="coverage-mode-content">

                  <strong>
                    Quick
                  </strong>

                  <span>
                    Essential coverage
                  </span>

                  <small>
                    Critical & high-priority scenarios
                  </small>

                </div>

                {coverageMode === "quick" && (
                  <div className="selected-check">
                    ✓
                  </div>
                )}

              </button>


              {/* ==================================================
                  STANDARD
              ================================================== */}

              <button
                className={`coverage-mode-card ${
                  coverageMode === "standard"
                    ? "active"
                    : ""
                }`}
                onClick={() =>
                  setCoverageMode("standard")
                }
                type="button"
              >

                <div className="coverage-mode-icon">
                  🧪
                </div>

                <div className="coverage-mode-content">

                  <strong>
                    Standard
                  </strong>

                  <span>
                    Balanced coverage
                  </span>

                  <small>
                    Critical, high & medium scenarios
                  </small>

                </div>

                {coverageMode === "standard" && (
                  <div className="selected-check">
                    ✓
                  </div>
                )}

              </button>


              {/* ==================================================
                  COMPREHENSIVE
              ================================================== */}

              <button
                className={`coverage-mode-card ${
                  coverageMode === "comprehensive"
                    ? "active"
                    : ""
                }`}
                onClick={() =>
                  setCoverageMode("comprehensive")
                }
                type="button"
              >

                <div className="coverage-mode-icon">
                  🔍
                </div>

                <div className="coverage-mode-content">

                  <strong>
                    Comprehensive
                  </strong>

                  <span>
                    Maximum coverage
                  </span>

                  <small>
                    All meaningful scenarios, up to 35
                  </small>

                </div>

                {coverageMode === "comprehensive" && (
                  <div className="selected-check">
                    ✓
                  </div>
                )}

              </button>

            </div>

          </div>


          {/* ==================================================
              INPUT FOOTER
          ================================================== */}

          <div className="input-footer">

            <span className="character-count">
              {requirement.length} characters
            </span>

            <div className="input-actions">

              <button
                className="clear-button"
                onClick={clearAll}
              >
                Clear
              </button>


              <button
                className="analyze-button"
                onClick={analyzeRequirement}
                disabled={
                  loading ||
                  analysisCompleted
                }
              >

                {loading
                  ? "Analyzing..."
                  : analysisCompleted
                  ? "Analysis Completed ✓"
                  : "Analyze Requirement →"}

              </button>

            </div>

          </div>


          <div className="powered-by">

            ✨ Powered by{" "}

            <strong>
              MSSPL SmartQA AI
            </strong>

          </div>

        </section>


        {/* ====================================================
            SMARTQA FEATURES
        ==================================================== */}

        <section className="features-section">

          <div className="features-heading">

            <span>
              SMART QA TOOLKIT
            </span>

            <h2>
              Everything You Need for Manual Testing
            </h2>

            <p>
              MSSPL SmartQA helps manual testers transform requirements
              into actionable QA insights faster and more effectively.
            </p>

          </div>


          <div className="features-grid">

            {/* Requirement Analysis */}

            <div className="feature-card feature-blue">

              <div className="feature-icon">
                🧠
              </div>

              <div>

                <h3>
                  Requirement Analysis
                </h3>

                <p>
                  Analyze user stories, identify functional requirements,
                  QA risks, and missing information.
                </p>

              </div>

            </div>


            {/* Test Case Generator */}

            <div className="feature-card feature-purple">

              <div className="feature-icon">
                🧪
              </div>

              <div>

                <h3>
                  Test Case Generator
                </h3>

                <p>
                  Generate structured positive and negative manual
                  test cases from requirements.
                </p>

              </div>

            </div>


            {/* Bug Report Assistant */}

            <div className="feature-card feature-pink">

              <div className="feature-icon">
                🐞
              </div>

              <div>

                <h3>
                  Bug Report Assistant
                </h3>

                <p>
                  Turn rough bug descriptions into clear, professional
                  bug reports with reproducible steps.
                </p>

              </div>

            </div>


            {/* QA Risk & Coverage */}

            <div className="feature-card feature-orange">

              <div className="feature-icon">
                🎯
              </div>

              <div>

                <h3>
                  QA Risk & Coverage
                </h3>

                <p>
                  Discover edge cases, boundary conditions, negative
                  scenarios, and potential coverage gaps.
                </p>

              </div>

            </div>

          </div>

        </section>


        {/* ====================================================
            LOADING
        ==================================================== */}

        {loading && (

          <section className="loading-card">

            <div className="spinner"></div>

            <h3>
              MSSPL SmartQA is analyzing your requirement...
            </h3>

            <p>
              Understanding the complete requirement and
              generating meaningful manual test scenarios.
            </p>

          </section>

        )}


        {/* ====================================================
            RESULTS
        ==================================================== */}

        {result && !loading && (

          <section className="results-section">

            {/* RESULTS HEADER */}

            <div className="results-header">

              <div>

                <span className="results-label">
                  AI ANALYSIS COMPLETE
                </span>

                <h2>
                  QA Intelligence Report
                </h2>

              </div>

              <button
                className="copy-button"
                onClick={copyResults}
              >
                📋 Copy Results
              </button>

            </div>


            {/* ==================================================
                SUMMARY
            ================================================== */}

            <div className="summary-grid">

              <div className="summary-card">

                <span>
                  MODULE
                </span>

                <strong>
                  {result.module || "N/A"}
                </strong>

              </div>


              <div className="summary-card">

                <span>
                  ACTOR
                </span>

                <strong>
                  {result.actor || "N/A"}
                </strong>

              </div>


              <div className="summary-card">

                <span>
                  QA RISKS
                </span>

                <strong>
                  {result.qa_risks
                    ? result.qa_risks.length
                    : 0}
                </strong>

              </div>


              <div className="summary-card">

                <span>
                  MISSING INFO
                </span>

                <strong>
                  {result.missing_information
                    ? result.missing_information.length
                    : 0}
                </strong>

              </div>

            </div>


            {/* ==================================================
                FUNCTIONAL REQUIREMENTS
            ================================================== */}

            {result.functional_requirements && (

              <div className="result-card">

                <div className="result-card-title">

                  <span className="result-icon">
                    📋
                  </span>

                  <div>

                    <h3>
                      Functional Requirements
                    </h3>

                    <p>
                      Requirements identified by MSSPL SmartQA
                    </p>

                  </div>

                </div>


                <ul>

                  {result.functional_requirements.map(
                    (item, index) => (

                      <li key={index}>
                        {item}
                      </li>

                    )
                  )}

                </ul>

              </div>

            )}


            {/* ==================================================
                QA RISKS
            ================================================== */}

            {result.qa_risks && (

              <div className="result-card risk-card">

                <div className="result-card-title">

                  <span className="result-icon">
                    ⚠️
                  </span>

                  <div>

                    <h3>
                      QA Risks
                    </h3>

                    <p>
                      Potential areas that require additional testing
                    </p>

                  </div>

                </div>


                <ul>

                  {result.qa_risks.map(
                    (item, index) => (

                      <li key={index}>
                        {item}
                      </li>

                    )
                  )}

                </ul>

              </div>

            )}


            {/* ==================================================
                MISSING INFORMATION
            ================================================== */}

            {result.missing_information && (

              <div className="result-card missing-card">

                <div className="result-card-title">

                  <span className="result-icon">
                    🔍
                  </span>

                  <div>

                    <h3>
                      Missing Information
                    </h3>

                    <p>
                      Clarifications that may improve test coverage
                    </p>

                  </div>

                </div>


                <ul>

                  {result.missing_information.map(
                    (item, index) => (

                      <li key={index}>
                        {item}
                      </li>

                    )
                  )}

                </ul>

              </div>

            )}


            {/* ==================================================
                TEST CASES
            ================================================== */}

            {result.test_cases && (

              <div className="result-card">

                <div className="result-card-title">

                  <span className="result-icon">
                    🧪
                  </span>

                  <div>

                    <h3>
                      Generated Test Cases
                    </h3>

                    <p>
                      Showing{" "}
                      <strong>
                        {getFilteredTestCases().length}
                      </strong>{" "}
                      of{" "}
                      <strong>
                        {result.test_cases.length}
                      </strong>{" "}
                      generated scenarios
                    </p>

                  </div>

                </div>


                {/* COVERAGE STATUS */}

                <div className="coverage-status">

                  <strong>
                    {coverageMode === "quick"
                      ? "⚡ Quick Coverage"
                      : coverageMode === "standard"
                      ? "🧪 Standard Coverage"
                      : "🔍 Comprehensive Coverage"}
                  </strong>

                  <span>
                    AI analyzed the requirement once.
                    Coverage is filtered locally.
                  </span>

                </div>


                <div className="table-wrapper">

                  <table>

                    <thead>

                      <tr>

                        <th>
                          Date
                        </th>

                        <th>
                          Test Case ID
                        </th>

                        <th>
                          Module
                        </th>

                        <th>
                          Type
                        </th>

                        <th>
                          Test Case
                        </th>

                        <th>
                          Test Data
                        </th>

                        <th>
                          Expected Result
                        </th>

                      </tr>

                    </thead>


                    <tbody>

                      {getFilteredTestCases().map(
                        (testCase, index) => (

                          <tr key={index}>

                            <td>
                              {testCase.date || "-"}
                            </td>

                            <td>
                              {testCase.test_case_id ||
                                `TC_${index + 1}`}
                            </td>

                            <td>
                              {testCase.module || "-"}
                            </td>

                            <td>

                              <span
                                className={
                                  testCase.test_case_type ===
                                  "Positive"
                                    ? "positive-badge"
                                    : "negative-badge"
                                }
                              >
                                {testCase.test_case_type ||
                                  "-"}
                              </span>

                            </td>

                            <td>
                              {testCase.test_case || "-"}
                            </td>

                            <td>
                              {testCase.test_data || "-"}
                            </td>

                            <td>
                              {testCase.expected_result || "-"}
                            </td>

                          </tr>

                        )
                      )}

                    </tbody>

                  </table>

                </div>

              </div>

            )}

          </section>

        )}

      </main>


      {/* ======================================================
          FOOTER
      ====================================================== */}

      <footer className="footer">

        <p>
          MSSPL SmartQA • AI-Powered Manual Testing Assistant
        </p>

        <span>
          Built for smarter, faster and more effective QA
        </span>

      </footer>

    </div>
  );
}

export default App;