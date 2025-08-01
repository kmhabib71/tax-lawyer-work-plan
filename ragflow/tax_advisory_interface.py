from flask import Flask, render_template, request, jsonify
import json
import os
import time
from datetime import datetime

class TaxCalculationEngine:
    """Bangladesh Income Tax Calculator - FY 2024-25"""
    
    def __init__(self):
        # Tax slabs for individual (male) - FY 2024-25
        self.tax_slabs = [
            (350000, 0.00),   # First 3.5L - 0%
            (100000, 0.05),   # Next 1L (3.5L-4.5L) - 5%
            (300000, 0.10),   # Next 3L (4.5L-7.5L) - 10%
            (400000, 0.15),   # Next 4L (7.5L-11.5L) - 15%
            (500000, 0.20),   # Next 5L (11.5L-16.5L) - 20%
            (float('inf'), 0.25)  # Above 16.5L - 25%
        ]
        
        # Exemption amounts
        self.exemptions = {
            'male': 350000,
            'female': 400000,
            'senior_citizen_male': 400000,
            'senior_citizen_female': 450000,
            'disabled_male': 475000,
            'disabled_female': 500000
        }
    
    def calculate_tax(self, income, exemption_type='male', investments=0):
        """Calculate income tax with detailed breakdown"""
        
        # Get exemption amount
        exemption = self.exemptions.get(exemption_type, 350000)
        
        # Calculate taxable income
        taxable_income = max(0, income - exemption)
        
        if taxable_income == 0:
            return {
                'total_income': income,
                'exemption': exemption,
                'taxable_income': 0,
                'gross_tax': 0,
                'investment_rebate': 0,
                'final_tax': 0,
                'tax_breakdown': [],
                'response_time': 0
            }
        
        # Calculate gross tax with breakdown
        gross_tax = 0
        remaining_income = taxable_income
        tax_breakdown = []
        
        for i, (slab_amount, rate) in enumerate(self.tax_slabs):
            if remaining_income <= 0:
                break
                
            taxable_in_slab = min(remaining_income, slab_amount)
            tax_in_slab = taxable_in_slab * rate
            gross_tax += tax_in_slab
            
            if taxable_in_slab > 0:
                # Calculate slab range (FIXED for correct exemption display)
                if i == 0:
                    slab_range = f"First {exemption:,} BDT (Exemption)"
                else:
                    # Calculate cumulative amounts from exemption point
                    prev_exemption_based = exemption
                    for j in range(1, i):
                        prev_exemption_based += self.tax_slabs[j][0]
                    
                    if slab_amount == float('inf'):
                        slab_range = f"Above {prev_exemption_based:,} BDT"
                    else:
                        current_limit = prev_exemption_based + slab_amount
                        slab_range = f"{prev_exemption_based:,} - {current_limit:,} BDT"
                
                tax_breakdown.append({
                    'slab_range': slab_range,
                    'taxable_amount': taxable_in_slab,
                    'rate': rate * 100,
                    'tax_amount': tax_in_slab
                })
            
            remaining_income -= taxable_in_slab
        
        # Calculate investment rebate (15% of investments, limited to gross tax)
        max_rebate_investment = min(investments, 1500000)  # Max 15L investment rebate
        rebate_amount = min(max_rebate_investment * 0.15, gross_tax)
        
        # Final tax
        final_tax = max(0, gross_tax - rebate_amount)
        
        return {
            'total_income': income,
            'exemption': exemption,
            'taxable_income': taxable_income,
            'gross_tax': gross_tax,
            'investment_rebate': rebate_amount,
            'final_tax': final_tax,
            'tax_breakdown': tax_breakdown
        }

# Initialize Flask app and tax engine
app = Flask(__name__)
tax_engine = TaxCalculationEngine()

@app.route('/')
def index():
    """Main interface page"""
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Tax Lawyer Bangladesh - Income Tax Calculator</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #2c3e50, #3498db);
            color: white;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 30px;
        }
        .container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }
        .input-section, .result-section {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #2c3e50;
        }
        input, select {
            width: 100%;
            padding: 12px;
            border: 2px solid #ecf0f1;
            border-radius: 5px;
            font-size: 16px;
            box-sizing: border-box;
        }
        input:focus, select:focus {
            border-color: #3498db;
            outline: none;
        }
        .calculate-btn {
            background: linear-gradient(135deg, #27ae60, #2ecc71);
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 5px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            width: 100%;
            transition: all 0.3s;
        }
        .calculate-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.2);
        }
        .result-item {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #ecf0f1;
        }
        .result-item:last-child {
            border-bottom: none;
            font-weight: bold;
            font-size: 18px;
            color: #27ae60;
        }
        .breakdown-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        .breakdown-table th, .breakdown-table td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ecf0f1;
        }
        .breakdown-table th {
            background-color: #f8f9fa;
            font-weight: bold;
        }
        .loading {
            display: none;
            text-align: center;
            color: #3498db;
        }
        .scenario-buttons {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        .scenario-btn {
            background: #3498db;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
        }
        .scenario-btn:hover {
            background: #2980b9;
        }
        @media (max-width: 768px) {
            .container {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏛️ AI Tax Lawyer Bangladesh</h1>
        <p>Income Tax Calculator 2024-25 | Powered by RAGFlow</p>
    </div>

    <div class="container">
        <div class="input-section">
            <h2>📊 Tax Calculation Input</h2>
            
            <div class="scenario-buttons">
                <h4 style="width: 100%; margin-bottom: 10px; color: #2c3e50;">🟢 TIER 1: Individual Salaried</h4>
                <button class="scenario-btn" onclick="loadScenario('scenario1_1')">1.1 Standard Employee</button>
                <button class="scenario-btn" onclick="loadScenario('scenario1_2')">1.2 Senior Citizen</button>
                <button class="scenario-btn" onclick="loadScenario('scenario1_3')">1.3 Young Professional</button>
                
                <h4 style="width: 100%; margin-top: 15px; margin-bottom: 10px; color: #f39c12;">🟡 TIER 2: Business/Professional</h4>
                <button class="scenario-btn" onclick="loadScenario('scenario2_1')">2.1 IT Consultant</button>
                <button class="scenario-btn" onclick="loadScenario('scenario2_2')">2.2 Medical Practice</button>
                <button class="scenario-btn" onclick="loadScenario('scenario2_3')">2.3 Trading Business</button>
                
                <h4 style="width: 100%; margin-top: 15px; margin-bottom: 10px; color: #e74c3c;">🔴 TIER 3: Corporate (Simplified)</h4>
                <button class="scenario-btn" onclick="loadScenario('scenario3_1')">3.1 Manufacturing</button>
                <button class="scenario-btn" onclick="loadScenario('scenario3_2')">3.2 Export Company</button>
                <button class="scenario-btn" onclick="loadScenario('scenario3_3')">3.3 Financial Holding</button>
                
                <button class="scenario-btn" onclick="loadScenario('clear')" style="background: #95a5a6; margin-top: 10px;">Clear Form</button>
            </div>
            
            <form id="taxForm">
                <div class="form-group">
                    <label for="annual_salary">Annual Salary (BDT)</label>
                    <input type="number" id="annual_salary" name="annual_salary" placeholder="e.g., 800000" required>
                </div>
                
                <div class="form-group">
                    <label for="other_income">Other Income (HRA, Bonus, etc.) (BDT)</label>
                    <input type="number" id="other_income" name="other_income" placeholder="e.g., 100000" value="0">
                </div>
                
                <div class="form-group">
                    <label for="taxpayer_type">Taxpayer Category</label>
                    <select id="taxpayer_type" name="taxpayer_type">
                        <option value="male">Individual (Male)</option>
                        <option value="female">Individual (Female)</option>
                        <option value="senior_citizen_male">Senior Citizen (Male)</option>
                        <option value="senior_citizen_female">Senior Citizen (Female)</option>
                        <option value="disabled_male">Disabled Person (Male)</option>
                        <option value="disabled_female">Disabled Person (Female)</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="business_expenses">Business Expenses (if applicable) (BDT)</label>
                    <input type="number" id="business_expenses" name="business_expenses" placeholder="e.g., 285000" value="0">
                </div>
                
                <div class="form-group">
                    <label for="investments">Total Investments (Insurance, DPS, Savings, etc.) (BDT)</label>
                    <input type="number" id="investments" name="investments" placeholder="e.g., 250000" value="0">
                </div>
                
                <button type="submit" class="calculate-btn">Calculate Tax 🧮</button>
            </form>
            
            <div class="loading" id="loading">
                <p>⏳ Calculating your tax...</p>
            </div>
        </div>

        <div class="result-section">
            <h2>📋 Tax Calculation Result</h2>
            <div id="results">
                <p style="text-align: center; color: #7f8c8d; font-style: italic;">
                    Fill in the form and click "Calculate Tax" to see your tax calculation results here.
                </p>
            </div>
        </div>
    </div>

    <script>
        // All 9 validation scenarios from VALIDATION_TEST_SCENARIOS.md
        const scenarios = {
            // TIER 1: Individual Salaried
            scenario1_1: {
                annual_salary: 800000,
                other_income: 100000,  // HRA
                taxpayer_type: 'male',
                investments: 250000    // 50K insurance + 200K DPS
            },
            scenario1_2: {
                annual_salary: 420000,  // Pension
                other_income: 30000,    // Bank interest
                taxpayer_type: 'senior_citizen_female',
                investments: 25000     // Life insurance
            },
            scenario1_3: {
                annual_salary: 300000,  // 25K monthly
                other_income: 0,
                taxpayer_type: 'male',
                investments: 100000    // Savings certificates
            },
            
            // TIER 2: Business/Professional
            scenario2_1: {
                annual_salary: 1500000, // Professional income
                other_income: 200000,   // Teaching income
                taxpayer_type: 'male',
                investments: 375000,    // 75K insurance + 300K stock
                business_expenses: 285000 // Rent + utilities + depreciation
            },
            scenario2_2: {
                annual_salary: 1200000, // Practice income
                other_income: 800000,   // Hospital part-time
                taxpayer_type: 'male',
                investments: 600000,    // 100K insurance + 500K savings
                business_expenses: 540000 // Rent + staff + medical supplies
            },
            scenario2_3: {
                annual_salary: 410000,  // Net trading income
                other_income: 80000,    // Rental income
                taxpayer_type: 'male',
                investments: 375000,    // 250K DPS + 125K insurance
                business_expenses: 0    // Already deducted in trading income
            },
            
            // TIER 3: Corporate (Simplified for individual calculation)
            scenario3_1: {
                annual_salary: 5000000,  // High earner equivalent
                other_income: 1000000,
                taxpayer_type: 'male',
                investments: 500000
            },
            scenario3_2: {
                annual_salary: 4000000,  // Export business owner
                other_income: 800000,
                taxpayer_type: 'male',
                investments: 400000
            },
            scenario3_3: {
                annual_salary: 6000000,  // Financial services
                other_income: 2000000,
                taxpayer_type: 'male',
                investments: 750000
            }
        };

        function loadScenario(scenarioName) {
            if (scenarioName === 'clear') {
                document.getElementById('taxForm').reset();
                return;
            }
            
            const scenario = scenarios[scenarioName];
            if (scenario) {
                document.getElementById('annual_salary').value = scenario.annual_salary;
                document.getElementById('other_income').value = scenario.other_income;
                document.getElementById('taxpayer_type').value = scenario.taxpayer_type;
                document.getElementById('business_expenses').value = scenario.business_expenses || 0;
                document.getElementById('investments').value = scenario.investments;
            }
        }

        function formatNumber(num) {
            return new Intl.NumberFormat('en-BD').format(num);
        }

        document.getElementById('taxForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const loading = document.getElementById('loading');
            const results = document.getElementById('results');
            
            loading.style.display = 'block';
            results.innerHTML = '';
            
            const formData = new FormData(this);
            const data = Object.fromEntries(formData);
            
            try {
                const response = await fetch('/calculate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    const calc = result.calculation;
                    
                    let html = `
                        <div class="result-item">
                            <span>Total Income:</span>
                            <span>৳${formatNumber(calc.total_income)}</span>
                        </div>
                        <div class="result-item">
                            <span>Tax Exemption:</span>
                            <span>৳${formatNumber(calc.exemption)}</span>
                        </div>
                        <div class="result-item">
                            <span>Taxable Income:</span>
                            <span>৳${formatNumber(calc.taxable_income)}</span>
                        </div>
                        <div class="result-item">
                            <span>Gross Tax:</span>
                            <span>৳${formatNumber(calc.gross_tax)}</span>
                        </div>
                        <div class="result-item">
                            <span>Investment Rebate:</span>
                            <span>৳${formatNumber(calc.investment_rebate)}</span>
                        </div>
                        <div class="result-item">
                            <span>Final Tax Payable:</span>
                            <span>৳${formatNumber(calc.final_tax)}</span>
                        </div>
                    `;
                    
                    if (calc.tax_breakdown && calc.tax_breakdown.length > 0) {
                        html += `
                            <h3 style="margin-top: 30px; color: #2c3e50;">Tax Calculation Breakdown</h3>
                            <table class="breakdown-table">
                                <thead>
                                    <tr>
                                        <th>Income Slab</th>
                                        <th>Taxable Amount</th>
                                        <th>Rate</th>
                                        <th>Tax Amount</th>
                                    </tr>
                                </thead>
                                <tbody>
                        `;
                        
                        calc.tax_breakdown.forEach(slab => {
                            html += `
                                <tr>
                                    <td>${slab.slab_range}</td>
                                    <td>৳${formatNumber(slab.taxable_amount)}</td>
                                    <td>${slab.rate}%</td>
                                    <td>৳${formatNumber(slab.tax_amount)}</td>
                                </tr>
                            `;
                        });
                        
                        html += `
                                </tbody>
                            </table>
                        `;
                    }
                    
                    html += `
                        <p style="margin-top: 20px; text-align: center; color: #7f8c8d; font-size: 14px;">
                            Response Time: ${result.response_time}ms | Calculated at: ${result.timestamp}
                        </p>
                    `;
                    
                    results.innerHTML = html;
                } else {
                    results.innerHTML = `<p style="color: red;">Error: ${result.error}</p>`;
                }
            } catch (error) {
                results.innerHTML = `<p style="color: red;">Network error: ${error.message}</p>`;
            } finally {
                loading.style.display = 'none';
            }
        });
    </script>
</body>
</html>
    '''

@app.route('/calculate', methods=['POST'])
def calculate_tax():
    """API endpoint for tax calculation"""
    try:
        start_time = time.time()
        
        data = request.get_json()
        
        # Extract and validate input
        annual_salary = float(data.get('annual_salary', 0))
        other_income = float(data.get('other_income', 0))
        taxpayer_type = data.get('taxpayer_type', 'male')
        business_expenses = float(data.get('business_expenses', 0))
        investments = float(data.get('investments', 0))
        
        # Calculate total income (deduct business expenses from gross income)
        gross_income = annual_salary + other_income
        total_income = max(0, gross_income - business_expenses)
        
        # Perform tax calculation
        result = tax_engine.calculate_tax(total_income, taxpayer_type, investments)
        
        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return jsonify({
            'success': True,
            'calculation': result,
            'response_time': f"{response_time:.2f}",
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

if __name__ == '__main__':
    print("=== AI Tax Lawyer Bangladesh - Web Interface ===")
    print("Starting Flask web server...")
    print("\nOnce started, open your browser and go to:")
    print("http://localhost:5000")
    print("\nPress Ctrl+C to stop the server")
    print("="*50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)