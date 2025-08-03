# Data Strategy & Hierarchy Plan
*AI Tax Lawyer Bangladesh - Week 2 Implementation*

## 🎯 Data Quality Hierarchy

### Layer 1: PRIMARY SOURCES (curated-cleaned-files/) ✅
**Priority: HIGHEST - Use First**
```
📁 curated-cleaned-files/ (15 files)
├── income_tax_act_2023_cleaned.json (2.4MB) 
├── আয়কর_আইন_২০২৩.json (2.4MB)
├── মলয_সযজন_কর_ও_সমপরক_শলক_আইন_২০১২.json (983KB)
├── কসটমস_আইন_২০২৩.json (774KB) 
├── অরথ_আইন_২০২৪.json (376KB)
├── অরথ_অধযদশ_২০২৫.json (1.1MB)
├── comprehensive_bengali_dictionary_200plus.json (46KB)
├── business_expense_limits.json
├── ereturn_validation_rules.json
└── [6 other core files]
```
**Use For**: Core legal frameworks, primary calculations, validation rules

### Layer 2: STRUCTURED DATA (senior_tax_lawyer_content/) ⚡
**Priority: HIGH - Use for System Integration**
```
📁 senior_tax_lawyer_content/ (130 files)
├── Section-wise Income Tax Act (English & Bengali)
├── All 8 Schedules of Income Tax Act 2023
├── TDS/VDS Rules (2019-2026)
├── VAT & SD Act sections and schedules
├── SROs and Circulars
└── Customs references
```
**Use For**: Micro-agent rule engines, API responses, lookup tables

### Layer 3: ENHANCED CONTENT (professional_enhanced_output/) 📚
**Priority: MEDIUM - Use for Comprehensive Coverage**
```
📁 professional_enhanced_output/ (1,525 files)
├── AI-enhanced OCR content
├── Comprehensive section coverage
├── Professional quality improvements
└── Extended legal content
```
**Use For**: RAGFlow knowledge base, comprehensive search, edge cases

### Layer 4: LEGACY DATA (current project data/) ⚠️
**Priority: LOW - Audit & Replace**
```
📁 ai-tax-lawyer-bangladesh/data/ (160 files)
└── Previously migrated mixed-quality files
```
**Action**: Audit for MongoDB usage, replace with higher quality sources

## 📋 Week 2 Implementation Plan

### Phase 1: Data Foundation (Day 8)
1. **Audit current MongoDB** - check what's already loaded
2. **Migrate Layer 1 files** to project data structure
3. **Create data mapping** for Layer 2 integration
4. **Establish data validation** pipeline

### Phase 2: Rules Engine Data (Days 8-9)
- **Task 1.1**: Use `income_tax_act_2023_cleaned.json` for core rules
- **Task 2.2**: Use Layer 2 schedule files for slab calculations  
- **Task 3.2**: Use `ereturn_validation_rules.json` + Layer 2 exemption files
- **Task 4.2**: Use business rules from Layer 1 + penalty sections from Layer 2

### Phase 3: Micro-Agent Data (Days 10-11)
- **Tax Slab Calculator**: Layer 1 + Layer 2 schedule files
- **Rebate & Exemption Agent**: Layer 1 validation + Layer 2 exemption files
- **Penalty Calculator**: Layer 1 business rules + Layer 2 penalty sections
- **Rate Manager**: Layer 2 SROs + current rate data

### Phase 4: Helper Agent Data (Days 12-14)
- **Bengali NLP**: `comprehensive_bengali_dictionary_200plus.json`
- **Document Parser**: Layer 1 validation rules + Layer 2 structures
- **Query Router**: All layers for comprehensive routing
- **Validation Agent**: Layer 1 rules for validation

## 🔄 Data Integration Strategy

### MongoDB Collections Structure
```javascript
// Priority-based data loading
collections: {
  // Layer 1 - Core Legal Framework
  core_tax_laws: "curated-cleaned-files/income_tax_act_2023_cleaned.json",
  validation_rules: "curated-cleaned-files/ereturn_validation_rules.json",
  business_rules: "curated-cleaned-files/business_expense_limits.json",
  
  // Layer 2 - Structured Rules  
  tax_sections: "senior_tax_lawyer_content/income-tax-act-*",
  tax_schedules: "senior_tax_lawyer_content/*-schedule-*", 
  tds_rules: "senior_tax_lawyer_content/tds-rules-*",
  vat_rules: "senior_tax_lawyer_content/vat-*",
  
  // Layer 3 - Enhanced Content (RAGFlow)
  comprehensive_content: "professional_enhanced_output/*"
}
```

### Data Source Selection Rules
1. **For calculations**: Always use Layer 1 (curated-cleaned-files)
2. **For lookups**: Prefer Layer 2 (senior_tax_lawyer_content)
3. **For search**: Use Layer 3 (professional_enhanced_output) 
4. **For validation**: Layer 1 validation rules are authoritative

### Conflict Resolution
- Layer 1 overrides all other layers
- Layer 2 overrides Layer 3
- Version dates determine precedence within same layer

## 🚀 Next Actions

### Immediate (Today)
1. ✅ Audit current MongoDB collections
2. ✅ Check data overlap between layers
3. ✅ Create migration scripts for Layer 1 data
4. ✅ Update Week 2 tasks with correct data references

### Week 2 Daily Actions
- **Day 8**: Implement Layer 1 integration for rules engine
- **Day 9**: Add Layer 2 structured data for detailed rules  
- **Day 10-11**: Configure micro-agents with appropriate data layers
- **Day 12-14**: Integrate all layers for helper agents

This strategy ensures **data quality**, **systematic integration**, and **fallback mechanisms** for comprehensive coverage.