# AI Tax Advisory System - Validation Test Scenarios
## Comprehensive Testing Framework for System Quality Assurance

**Purpose**: These 9 scenarios will be used throughout development phases to validate system performance, accuracy, and capabilities across all complexity levels.

**Testing Approach**: Each scenario includes expected calculation steps, legal provisions, and detailed reasoning to ensure comprehensive validation.

---

# 🟢 **TIER 1: SIMPLE - INDIVIDUAL SALARIED**
**Target Users**: Salaried employees, basic income sources
**Expected Response Time**: <1 second
**Complexity Level**: Basic arithmetic with standard exemptions

## **Scenario 1.1: Standard Salaried Employee**
### **Query:**
> "I'm a 28-year-old male software engineer working in Dhaka. My annual salary is 8,00,000 BDT with house rent allowance of 1,00,000 BDT. I have life insurance premium of 50,000 BDT and DPS investment of 2,00,000 BDT. Calculate my income tax for the year 2024-25."

### **Expected System Response:**
- **Total Income**: 9,00,000 BDT (8,00,000 + 1,00,000)
- **Exemption**: 3,50,000 BDT (individual male basic exemption)
- **Taxable Income**: 5,50,000 BDT
- **Tax Calculation**:
  - First 3,50,000: 0% = 0 BDT
  - Next 1,00,000 (3,50,000-4,50,000): 5% = 5,000 BDT
  - Next 1,00,000 (4,50,000-5,50,000): 10% = 10,000 BDT
- **Gross Tax**: 15,000 BDT
- **Investment Rebate**: 15% on 2,50,000 BDT = 37,500 BDT (limited to gross tax = 15,000 BDT)
- **Final Tax**: 0 BDT (rebate covers all tax)

### **Validation Points:**
- ✅ Correct exemption application
- ✅ Progressive tax slab calculation
- ✅ Investment rebate limitation logic
- ✅ Bengali number formatting
- ✅ Clear step-by-step breakdown

---

## **Scenario 1.2: Female Senior Citizen**
### **Query:**
> "আমি একজন ৬৬ বছর বয়সী মহিলা। আমার বার্ষিক পেনশন ৪,২০,০০০ টাকা এবং ব্যাংক সুদ ৩০,০০০ টাকা। জীবন বীমা প্রিমিয়াম ২৫,০০০ টাকা। আমার আয়কর কত হবে ২০২৪-২৫ সালের জন্য?"

### **Expected System Response:**
- **Total Income**: 4,50,000 BDT (4,20,000 + 30,000)
- **Exemption**: 4,00,000 BDT (female senior citizen exemption)
- **Taxable Income**: 50,000 BDT
- **Tax Calculation**:
  - First 3,50,000: 0% = 0 BDT
  - Next 50,000: 5% = 2,500 BDT
- **Investment Rebate**: 15% on 25,000 = 3,750 BDT (limited to 2,500 BDT)
- **Final Tax**: 0 BDT

### **Validation Points:**
- ✅ Bengali language processing
- ✅ Senior citizen + female exemption logic
- ✅ Multiple income source handling
- ✅ Investment rebate calculation
- ✅ Zero tax result handling

---

## **Scenario 1.3: Young Professional with Minimal Income**
### **Query:**
> "I just started my career as a junior executive. My monthly salary is 25,000 BDT with no other income. I invested 1,00,000 BDT in government savings certificates. What will be my tax liability?"

### **Expected System Response:**
- **Total Income**: 3,00,000 BDT (25,000 × 12)
- **Exemption**: 3,50,000 BDT (basic individual exemption)
- **Taxable Income**: 0 BDT (income below exemption limit)
- **Tax Calculation**: No tax applicable
- **Investment Rebate**: Not applicable (no gross tax to reduce)
- **Final Tax**: 0 BDT

### **Validation Points:**
- ✅ Below-exemption income handling
- ✅ Monthly to annual salary conversion
- ✅ Investment rebate when no tax applicable
- ✅ Clear explanation for zero tax
- ✅ Encouragement for continued investing

---

# 🟡 **TIER 2: MODERATE - BUSINESS/PROFESSIONAL**
**Target Users**: Business owners, professionals, freelancers
**Expected Response Time**: 1-2 seconds
**Complexity Level**: Multiple income sources, business expenses, professional allowances

## **Scenario 2.1: Freelance IT Consultant**
### **Query:**
> "I'm a freelance software consultant. My professional income for 2024-25 was 15,00,000 BDT. Business expenses include office rent 1,80,000 BDT, internet and utilities 60,000 BDT, computer depreciation 45,000 BDT. I also received 2,00,000 BDT from teaching at a private university. My investments: life insurance 75,000 BDT, stock market 3,00,000 BDT. Calculate my tax."

### **Expected System Response:**
- **Professional Income**: 15,00,000 BDT
- **Teaching Income**: 2,00,000 BDT
- **Total Gross Income**: 17,00,000 BDT
- **Business Expenses**: 2,85,000 BDT (office rent + utilities + depreciation)
- **Net Business Income**: 14,15,000 BDT (17,00,000 - 2,85,000)
- **Exemption**: 3,50,000 BDT
- **Taxable Income**: 10,65,000 BDT
- **Tax Calculation**:
  - 0-3,50,000: 0% = 0
  - 3,50,000-4,50,000: 5% = 5,000
  - 4,50,000-7,50,000: 10% = 30,000
  - 7,50,000-10,65,000: 15% = 47,250
- **Gross Tax**: 82,250 BDT
- **Investment Rebate**: 15% on 3,75,000 = 56,250 BDT
- **Final Tax**: 26,000 BDT

### **Validation Points:**
- ✅ Professional income classification
- ✅ Business expense deduction rules
- ✅ Multiple income source aggregation
- ✅ Depreciation handling
- ✅ Investment rebate calculation and limits

---

## **Scenario 2.2: Medical Practice Owner**
### **Query:**
> "ডাক্তার হিসেবে আমার নিজের চেম্বার আছে। রোগী দেখার আয় ১২,০০,০০০ টাকা, হাসপাতালে পার্ট-টাইম ডিউটি থেকে ৮,০০,০০০ টাকা। চেম্বারের ভাড়া ১,২০,০০০ টাকা, কর্মচারী বেতন ২,৪০,০০০ টাকা, ওষুধ ও যন্ত্রপাতি খরচ ১,৮০,০০০ টাকা। বিনিয়োগ: জীবন বীমা ১,০০,০০০ টাকা, সঞ্চয়পত্র ৫,০০,০০০ টাকা। কর কত হবে?"

### **Expected System Response:**
- **Professional Practice Income**: 12,00,000 BDT
- **Hospital Part-time Income**: 8,00,000 BDT
- **Total Gross Income**: 20,00,000 BDT
- **Business Expenses**: 5,40,000 BDT (rent + staff salary + medical supplies)
- **Net Professional Income**: 14,60,000 BDT
- **Exemption**: 3,50,000 BDT
- **Taxable Income**: 11,10,000 BDT
- **Tax Calculation**:
  - 0-3,50,000: 0% = 0
  - 3,50,000-4,50,000: 5% = 5,000
  - 4,50,000-7,50,000: 10% = 30,000
  - 7,50,000-11,10,000: 15% = 54,000
- **Gross Tax**: 89,000 BDT
- **Investment Rebate**: 15% on 6,00,000 = 90,000 BDT (limited to 89,000)
- **Final Tax**: 0 BDT

### **Validation Points:**
- ✅ Bengali language understanding
- ✅ Professional practice expense rules
- ✅ Healthcare sector specific deductions
- ✅ Staff salary as business expense
- ✅ Multiple investment types handling

---

## **Scenario 2.3: Small Trading Business**
### **Query:**
> "I run a small electronics trading business. Annual sales 45,00,000 BDT, cost of goods sold 32,00,000 BDT, office expenses 2,50,000 BDT, transport costs 1,80,000 BDT, staff salaries 3,60,000 BDT. I also earned 80,000 BDT from property rent. Investments: DPS 2,50,000 BDT, life insurance 1,25,000 BDT. I'm 35 years old married male. Calculate tax liability."

### **Expected System Response:**
- **Trading Income**: 45,00,000 - 32,00,000 = 13,00,000 BDT (gross profit)
- **Business Expenses**: 8,90,000 BDT (office + transport + salaries)
- **Net Trading Income**: 4,10,000 BDT
- **Rental Income**: 80,000 BDT
- **Total Income**: 4,90,000 BDT
- **Exemption**: 3,50,000 BDT
- **Taxable Income**: 1,40,000 BDT
- **Tax Calculation**:
  - 0-3,50,000: 0% = 0
  - Next 1,40,000: 5% = 7,000
- **Investment Rebate**: 15% on 3,75,000 = 56,250 BDT (limited to 7,000)
- **Final Tax**: 0 BDT

### **Validation Points:**
- ✅ Trading business profit calculation
- ✅ Cost of goods sold handling
- ✅ Business expense categorization
- ✅ Rental income as separate source
- ✅ Investment rebate optimization

---

# 🔴 **TIER 3: COMPLEX - CORPORATE ADJUSTMENTS**  
**Target Users**: Corporate tax managers, complex business scenarios
**Expected Response Time**: 2-3 seconds
**Complexity Level**: Legal provision analysis, adjustment calculations, multi-step reasoning

## **Scenario 3.1: Pharmaceutical Manufacturing Company** 
### **Query:**
> "Pharmaceuticals Bangladesh Ltd., a subsidiary of Switzerland Viking, reported net profit of 56,00,00,000 BDT for the year ending June 30, 2024. Annual turnover is 120,00,00,000 BDT. Adjust the net profit to determine the taxable income under the Bangladesh Income Tax Act (2023), considering the following: Director's salary of 3,30,000 BDT (not taxed at source), Head office expense claim of 60,00,000 BDT, Life insurance premium of 11,000 BDT included in expenses, Commission of 10,000 BDT to an auditor without complying with Section 149, Donation of 50,000 BDT to a children's home, 9,50,000 BDT of salaries for the Managing Director's household staff plus 10,00,000 BDT of other perquisites, Interest expense of 9,50,000 BDT while the company gave an interest-free loan of 75,00,00,000 BDT to a local subsidiary (bank loan is 2,10,00,00,000 BDT), Interest income of 11,000 BDT from bank deposits included in earnings, A 20% shareholder is a minor girl (special consideration for dividend income)."

### **Expected System Response:**
**Step 1: Net Profit Analysis**
- Reported Net Profit: 56,00,00,000 BDT
- Turnover: 120,00,00,000 BDT

**Step 2: Adjustments Required**

**Add Back (Disallowed Expenses):**
1. **Director's Salary**: 3,30,000 BDT
   - *Legal Basis*: Section 30(2)(c) - Director's remuneration without shareholder approval
   - *Reasoning*: No evidence of shareholder approval for director's salary

2. **Head Office Expense**: 60,00,000 BDT  
   - *Legal Basis*: Section 30(2)(g) - Head office expenses limitation
   - *Reasoning*: Exceeds allowable percentage of turnover (typically 1-2%)

3. **Auditor Commission**: 10,000 BDT
   - *Legal Basis*: Section 149 - Audit fees without tax deduction
   - *Reasoning*: Commission paid without complying with TDS requirements

4. **MD's Household Staff**: 9,50,000 BDT
   - *Legal Basis*: Section 30(2)(d) - Personal expenses of directors
   - *Reasoning*: Household staff salaries are personal, not business expenses

5. **MD's Other Perquisites**: 10,00,000 BDT
   - *Legal Basis*: Section 30(2)(d) - Personal benefits
   - *Reasoning*: Personal perquisites not related to business

6. **Proportionate Interest Disallowance**: 3,41,071 BDT
   - *Legal Basis*: Section 80 - Interest on borrowings for non-business purpose
   - *Calculation*: (75,00,00,000 ÷ 2,10,00,00,000) × 9,50,000 = 3,41,071 BDT
   - *Reasoning*: Interest proportionate to interest-free loan given

**Deduct (Allowable Items):**
1. **Life Insurance Premium**: 11,000 BDT - Allowable business expense
2. **Charitable Donation**: 50,000 BDT - Allowable under donation provisions

**Step 3: Final Calculation**
- Net Profit: 56,00,00,000 BDT
- Add Disallowed: 86,21,071 BDT
- Less Allowable: 61,000 BDT
- **Adjusted Taxable Income**: 56,85,60,071 BDT

**Step 4: Corporate Tax Calculation**
- Corporate Tax Rate: 22.5% (manufacturing company)
- **Tax Payable**: 12,79,26,016 BDT

### **Validation Points:**
- ✅ Complex multi-step legal reasoning  
- ✅ Correct application of Income Tax Act sections
- ✅ Proportionate interest calculation accuracy
- ✅ Director's remuneration disallowance rules
- ✅ Head office expense limitation logic
- ✅ Comprehensive adjustment rationale

---

## **Scenario 3.2: Textile Export Company**
### **Query:**
> "Bengal Textile Mills Ltd. is a leading garments exporter. For FY 2023-24: Total revenue 180,00,00,000 BDT (Export: 150,00,00,000 BDT, Domestic: 30,00,00,000 BDT), Net profit before tax 25,00,00,000 BDT. Adjustments needed: Entertainment expenses 15,00,000 BDT (no proper documentation), Provision for bad debts 2,50,00,000 BDT (not written off), Gift to foreign buyers 8,00,000 BDT, Research & development expenses 4,00,00,000 BDT (new product development), Export incentive received 5,00,00,000 BDT, Accelerated depreciation claimed 3,00,00,000 BDT (furniture and fixtures), Interest on term loan 6,00,00,000 BDT for factory expansion, Loss from fire (uninsured portion) 1,20,00,000 BDT. The company has 200 workers and qualifies for industrial undertaking benefits."

### **Expected System Response:**
**Step 1: Income Classification**
- Export Revenue: 150,00,00,000 BDT (83.33%)
- Domestic Revenue: 30,00,00,000 BDT (16.67%)
- Net Profit Before Tax: 25,00,00,000 BDT

**Step 2: Detailed Adjustments**

**Add Back (Disallowed):**
1. **Entertainment Expenses**: 15,00,000 BDT
   - *Legal Basis*: Section 30(2)(f) - Inadequate documentation
   - *Reasoning*: Entertainment expenses without proper vouchers not allowable

2. **Provision for Bad Debts**: 2,50,00,000 BDT
   - *Legal Basis*: Section 30(1) - Only actual write-offs allowed
   - *Reasoning*: Provisions not allowable, only actual bad debt write-offs

3. **Gifts to Foreign Buyers**: 8,00,000 BDT  
   - *Legal Basis*: Section 30(2)(i) - Business gifts limitation
   - *Reasoning*: Exceeds allowable gift limits per recipient

4. **Excess Depreciation**: 1,50,00,000 BDT
   - *Legal Basis*: Second Schedule - Standard depreciation rates
   - *Calculation*: Claimed 3,00,00,000 vs allowable 1,50,00,000
   - *Reasoning*: Furniture & fixtures maximum 10% per annum

**Deduct (Additional Allowances):**
1. **R&D Expenses**: 4,00,00,000 BDT
   - *Legal Basis*: Section 44 - Research and development incentive
   - *Reasoning*: 100% deduction for approved R&D expenses

2. **Fire Loss (Uninsured)**: 1,20,00,000 BDT
   - *Legal Basis*: Section 30(1) - Business loss allowable
   - *Reasoning*: Genuine business loss due to unforeseen circumstances

**Step 3: Export Incentive Treatment**
- Export Incentive: 5,00,00,000 BDT
- *Legal Basis*: Section 46 - Tax exemption on export incentives
- *Treatment*: Fully exempt from tax

**Step 4: Final Calculation**
- Net Profit Before Tax: 25,00,00,000 BDT
- Add Disallowances: 4,23,00,000 BDT
- Less Additional Allowances: 5,20,00,000 BDT
- **Adjusted Taxable Income**: 24,03,00,000 BDT

**Step 5: Tax Calculation with Export Benefits**
- Industrial Undertaking Rate: 20% (instead of 22.5%)
- Export Portion (83.33%): Eligible for reduced rate
- **Tax Payable**: 4,80,60,000 BDT

### **Validation Points:**
- ✅ Export vs domestic revenue segregation
- ✅ Industrial undertaking benefit application  
- ✅ R&D expense incentive calculation
- ✅ Depreciation rate compliance checking
- ✅ Export incentive exemption handling
- ✅ Bad debt provision vs write-off distinction

---

## **Scenario 3.3: Financial Services Holding Company**
### **Query:**
> "Prime Financial Holdings Ltd. is a diversified financial services company. FY 2023-24 details: Dividend income from subsidiaries 45,00,00,000 BDT, Interest income from inter-company loans 12,00,00,000 BDT, Management fees from subsidiaries 8,00,00,000 BDT, Investment gain from selling shares 15,00,00,000 BDT (held for 2 years), Operating expenses 18,00,00,000 BDT including provision for loan losses 5,00,00,000 BDT (subsidiary bank), Directors' fees and benefits 2,50,00,000 BDT (5 independent directors), Professional fees to related party 3,00,00,000 BDT (sister concern), Contribution to employees' welfare fund 1,50,00,000 BDT, Interest expense on debentures 4,00,00,000 BDT, Foreign exchange loss 2,00,00,000 BDT (revaluation), Advance tax paid 6,00,00,000 BDT. The company is listed on Dhaka Stock Exchange and has 40% institutional shareholding."

### **Expected System Response:**
**Step 1: Income Source Analysis**
- Dividend Income: 45,00,00,000 BDT
- Interest Income (Inter-company): 12,00,00,000 BDT  
- Management Fees: 8,00,00,000 BDT
- Capital Gains: 15,00,00,000 BDT
- **Total Income**: 80,00,00,000 BDT

**Step 2: Capital Gains Treatment**
- Investment Gain: 15,00,00,000 BDT
- *Legal Basis*: Section 47 - Capital gains on securities
- *Holding Period*: 2 years (long-term)
- *Tax Rate*: 10% (separate rate for listed company shares)
- *Capital Gains Tax*: 1,50,00,000 BDT (calculated separately)

**Step 3: Dividend Income Treatment**  
- Dividend from Subsidiaries: 45,00,00,000 BDT
- *Legal Basis*: Section 56 - Inter-corporate dividend exemption
- *Treatment*: 100% exempt if holding >10% shares
- *Tax Impact*: Fully exempt from tax

**Step 4: Operating Expense Analysis**

**Allowable Expenses:**
1. **Loan Loss Provision**: 0 BDT (Not applicable to holding company)
   - *Reasoning*: Holding company cannot claim bank subsidiary provisions
2. **Directors' Fees**: 2,50,00,000 BDT (Allowable with proper approval)
3. **Employee Welfare Fund**: 1,50,00,000 BDT (Allowable business expense)  
4. **Interest on Debentures**: 4,00,00,000 BDT (Allowable financing cost)
5. **Forex Loss**: 2,00,00,000 BDT (Business loss from operations)

**Questionable Expenses:**
1. **Related Party Professional Fees**: 3,00,00,000 BDT
   - *Legal Basis*: Section 30(2)(h) - Arm's length pricing
   - *Adjustment*: Subject to transfer pricing rules
   - *Allowable Amount*: 2,00,00,000 BDT (market rate assessment)

**Step 5: Final Calculation**
- Management Fees: 8,00,00,000 BDT
- Interest Income: 12,00,00,000 BDT  
- **Gross Income**: 20,00,00,000 BDT
- Less: Allowable Expenses: 12,00,00,000 BDT
- **Taxable Income**: 8,00,00,000 BDT

**Step 6: Tax Computation**
- Regular Income Tax (22.5%): 1,80,00,000 BDT
- Capital Gains Tax (10%): 1,50,00,000 BDT
- **Total Tax Liability**: 3,30,00,000 BDT
- Less: Advance Tax Paid: 6,00,00,000 BDT
- **Refund Due**: 2,70,00,000 BDT

### **Validation Points:**
- ✅ Inter-corporate dividend exemption rules
- ✅ Capital gains separate computation
- ✅ Transfer pricing adjustment logic
- ✅ Holding company specific provisions
- ✅ Advance tax adjustment and refund calculation
- ✅ Multiple income source tax treatment

---

# 📊 **VALIDATION FRAMEWORK**

## **Performance Benchmarks**

### **Response Time Targets**
- **Simple Queries**: <1 second
- **Moderate Queries**: 1-2 seconds  
- **Complex Queries**: 2-3 seconds

### **Accuracy Requirements**
- **Legal Provision Matching**: >95%
- **Calculation Accuracy**: 100% (mathematical precision)
- **Citation Correctness**: >98%
- **Language Processing**: >90% (Bengali/English)

### **Completeness Metrics**
- **Step Coverage**: All required calculation steps shown
- **Legal Basis**: Relevant sections cited for each adjustment
- **Reasoning Quality**: Clear explanation for each decision
- **Format Consistency**: Structured, professional presentation

## **Testing Protocol**

### **Phase 1 Testing** (Data Enhancement)
- Test data availability for all scenario components
- Verify legal provision coverage
- Validate calculation rule completeness

### **Phase 2 Testing** (AI Engine)  
- Query classification accuracy (95%+ target)
- Entity extraction precision (90%+ target)
- Legal reasoning coherence assessment
- Response generation quality evaluation

### **Phase 3 Testing** (Integration)
- End-to-end scenario execution
- Performance under load testing
- User acceptance testing with tax professionals
- Production environment validation

## **Success Criteria**
✅ All 9 scenarios executed successfully
✅ Response times meet targets  
✅ Calculation accuracy verified by tax experts
✅ Legal citations validated against current law
✅ User satisfaction >4.5/5 across all complexity levels

---

**Test Manager**: [Assign Lead]
**Legal Validation**: [Tax Expert Team]
**Technical Validation**: [QA Lead]
**Last Updated**: July 30, 2024