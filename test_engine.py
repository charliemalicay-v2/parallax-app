import math
import pytest
from main import ParallaxCalculationEngine

# The 'Golden Dataset' mock extracted directly from the original Excel file
GOLDEN_EXCEL_FIXTURES = [
    {
        "case_id": "Standard Residential Foundation",
        "inputs": {"qty": 250.0, "rate": 85.00, "multiplier": 1.10},
        "excel_intermediates": {
            "helper_material_base": 21250.0,
            "helper_labor_allowance": 9562.5,
            "helper_overhead_factor": 3081.25
        },
        "excel_final_output": 33893.75
    },
    {
        "case_id": "High-Risk Commercial Infrastructure",
        "inputs": {"qty": 1200.0, "rate": 140.00, "multiplier": 1.35},
        "excel_intermediates": {
            "helper_material_base": 168000.0,
            "helper_labor_allowance": 75600.0,
            "helper_overhead_factor": 85260.0
        },
        "excel_final_output": 328860.0
    }
]

@pytest.mark.parametrize("fixture", GOLDEN_EXCEL_FIXTURES, ids=lambda f: f["case_id"])
def test_excel_translation_tolerance(fixture):
    """
    Validates that the Python execution pipeline matches the intermediate 
    and final outputs of the spreadsheet source file within 2%.
    """
    inputs = fixture["inputs"]
    excel_helpers = fixture["excel_intermediates"]
    excel_final = fixture["excel_final_output"]
    
    # Run the Python logic engine
    python_results = ParallaxCalculationEngine.execute_pipeline(**inputs)
    
    # Define our mathematical guardrail: 2% relative tolerance
    TOLERANCE = 0.02
    
    # 1. Validate Intermediate Helper Nodes
    assert math.isclose(
        python_results["helper_material_base"], 
        excel_helpers["helper_material_base"], 
        rel_tol=TOLERANCE
    ), f"Material base mismatch in {fixture['case_id']}"

    assert math.isclose(
        python_results["helper_labor_allowance"], 
        excel_helpers["helper_labor_allowance"], 
        rel_tol=TOLERANCE
    ), f"Labor allowance mismatch in {fixture['case_id']}"

    assert math.isclose(
        python_results["helper_overhead_factor"], 
        excel_helpers["helper_overhead_factor"], 
        rel_tol=TOLERANCE
    ), f"Overhead factor mismatch in {fixture['case_id']}"
    
    # 2. Validate Final Accumulated Output
    assert math.isclose(
        python_results["final_estimate"], 
        excel_final, 
        rel_tol=TOLERANCE
    ), f"Final output calculation drift exceeded 2% limit in {fixture['case_id']}"
