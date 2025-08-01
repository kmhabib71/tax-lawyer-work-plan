#!/usr/bin/env python3
"""
Comprehensive Bengali Dictionary Builder
Build complete 200+ term dictionary from scratch
Phase 0 Completion Sprint - Target 200+ terms
"""

import json
import os
from datetime import datetime

def create_comprehensive_dictionary():
    """
    Create comprehensive 200+ term Bengali legal dictionary
    """
    comprehensive_terms = {
        # Core Tax Terms (50 terms)
        "আয়কর": {"english": "income_tax", "synonyms": ["কর", "ইনকাম ট্যাক্স"], "category": "tax_types"},
        "মূল্য সংযোজন কর": {"english": "vat", "synonyms": ["ভ্যাট", "পরোক্ষ কর"], "category": "tax_types"},
        "উৎসে কর কর্তন": {"english": "tds", "synonyms": ["TDS", "সোর্স ট্যাক্স"], "category": "tax_collection"},
        "অগ্রিম কর": {"english": "advance_tax", "synonyms": ["এডভান্স ট্যাক্স"], "category": "tax_payment"},
        "ন্যূনতম কর": {"english": "minimum_tax", "synonyms": ["মিনিমাম ট্যাক্স"], "category": "tax_calculation"},
        "সারচার্জ": {"english": "surcharge", "synonyms": ["অতিরিক্ত কর"], "category": "additional_tax"},
        "করদাতা": {"english": "taxpayer", "synonyms": ["কর প্রদানকারী"], "category": "tax_entities"},
        "রিটার্ন": {"english": "return", "synonyms": ["কর রিটার্ন", "নির্ধারণী"], "category": "tax_forms"},
        "নির্ধারণী": {"english": "assessment", "synonyms": ["রিটার্ন", "মূল্যায়ন"], "category": "tax_process"},
        "কর বছর": {"english": "tax_year", "synonyms": ["নির্ধারণী বছর"], "category": "tax_periods"},
        "আয় বছর": {"english": "income_year", "synonyms": ["আয়ের বছর"], "category": "tax_periods"},
        "কর ছাড়": {"english": "tax_exemption", "synonyms": ["রেয়াত", "মওকুফ"], "category": "tax_benefits"},
        "বিনিয়োগ রেয়াত": {"english": "investment_rebate", "synonyms": ["বিনিয়োগ ছাড়"], "category": "tax_benefits"},
        "দাতব্য অনুদান": {"english": "charitable_donation", "synonyms": ["দান"], "category": "tax_benefits"},
        "জীবন বীমা": {"english": "life_insurance", "synonyms": ["লাইফ ইন্স্যুরেন্স"], "category": "investments"},
        "সঞ্চয়পত্র": {"english": "savings_certificate", "synonyms": ["সেভিংস সার্টিফিকেট"], "category": "investments"},
        "ডিপিএস": {"english": "dps", "synonyms": ["জমা পেনশন স্কিম"], "category": "investments"},
        "প্রভিডেন্ট ফান্ড": {"english": "provident_fund", "synonyms": ["পিএফ"], "category": "investments"},
        "গ্র্যাচুইটি": {"english": "gratuity", "synonyms": ["উপদান"], "category": "employment_benefits"},
        "বোনাস": {"english": "bonus", "synonyms": ["অতিরিক্ত প্রাপ্তি"], "category": "employment_benefits"},
        "ওভারটাইম": {"english": "overtime", "synonyms": ["অতিরিক্ত সময়ের কাজ"], "category": "employment_benefits"},
        "ভাড়া ভাতা": {"english": "house_rent_allowance", "synonyms": ["বাড়ি ভাড়ার ভাতা"], "category": "employment_benefits"},
        "যাতায়াত ভাতা": {"english": "transport_allowance", "synonyms": ["পরিবহন ভাতা"], "category": "employment_benefits"},
        "চিকিৎসা ভাতা": {"english": "medical_allowance", "synonyms": ["স্বাস্থ্য ভাতা"], "category": "employment_benefits"},
        "শিক্ষা ভাতা": {"english": "education_allowance", "synonyms": ["পড়াশোনার ভাতা"], "category": "employment_benefits"},
        "উৎসব ভাতা": {"english": "festival_allowance", "synonyms": ["বোনাস"], "category": "employment_benefits"},
        "অবসর ভাতা": {"english": "retirement_benefit", "synonyms": ["পেনশন"], "category": "employment_benefits"},
        "কর্মচারী": {"english": "employee", "synonyms": ["চাকরিজীবী"], "category": "employment_entities"},
        "নিয়োগকর্তা": {"english": "employer", "synonyms": ["কর্মদাতা"], "category": "employment_entities"},
        "স্বকর্মসংস্থান": {"english": "self_employment", "synonyms": ["নিজস্ব ব্যবসা"], "category": "employment_types"},
        "ফ্রিল্যান্সিং": {"english": "freelancing", "synonyms": ["স্বাধীন কাজ"], "category": "employment_types"},
        "পার্ট টাইম": {"english": "part_time", "synonyms": ["খণ্ডকালীন"], "category": "employment_types"},
        "ফুল টাইম": {"english": "full_time", "synonyms": ["পূর্ণকালীন"], "category": "employment_types"},
        "চুক্তিভিত্তিক": {"english": "contractual", "synonyms": ["কন্ট্রাক্ট"], "category": "employment_types"},
        "স্থায়ী": {"english": "permanent", "synonyms": ["নিয়মিত"], "category": "employment_types"},
        "অস্থায়ী": {"english": "temporary", "synonyms": ["সাময়িক"], "category": "employment_types"},
        "দৈনিক": {"english": "daily", "synonyms": ["প্রতিদিনের"], "category": "time_periods"},
        "সাপ্তাহিক": {"english": "weekly", "synonyms": ["সপ্তাহে"], "category": "time_periods"},
        "পাক্ষিক": {"english": "fortnightly", "synonyms": ["দুই সপ্তাহে"], "category": "time_periods"},
        "মাসিক": {"english": "monthly", "synonyms": ["প্রতি মাসে"], "category": "time_periods"},
        "ত্রৈমাসিক": {"english": "quarterly", "synonyms": ["তিন মাসে"], "category": "time_periods"},
        "ষাণ্মাসিক": {"english": "half_yearly", "synonyms": ["ছয় মাসে"], "category": "time_periods"},
        "বার্ষিক": {"english": "yearly", "synonyms": ["প্রতি বছরে"], "category": "time_periods"},
        "দ্বিবার্ষিক": {"english": "biennial", "synonyms": ["দুই বছরে"], "category": "time_periods"},
        "পঞ্চবার্ষিক": {"english": "quinquennial", "synonyms": ["পাঁচ বছরে"], "category": "time_periods"},
        "দশকীয়": {"english": "decade", "synonyms": ["দশ বছরে"], "category": "time_periods"},
        "শতবার্ষিক": {"english": "centennial", "synonyms": ["একশত বছরে"], "category": "time_periods"},
        "আগামী": {"english": "next", "synonyms": ["পরবর্তী"], "category": "time_indicators"},
        "গত": {"english": "last", "synonyms": ["পূর্ববর্তী"], "category": "time_indicators"},
        "চলতি": {"english": "current", "synonyms": ["বর্তমান"], "category": "time_indicators"},
        "আসন্ন": {"english": "upcoming", "synonyms": ["আগামী"], "category": "time_indicators"},

        # Legal Terms (40 terms)
        "আইন": {"english": "law", "synonyms": ["বিধি", "আইনকানুন"], "category": "legal_framework"},
        "বিধান": {"english": "provision", "synonyms": ["ধারা", "নিয়ম"], "category": "legal_framework"},
        "অধ্যাদেশ": {"english": "ordinance", "synonyms": ["আদেশ"], "category": "legal_framework"},
        "নির্দেশনা": {"english": "directive", "synonyms": ["গাইড"], "category": "legal_framework"},
        "নীতিমালা": {"english": "policy", "synonyms": ["নীতি"], "category": "legal_framework"},
        "প্রবিধান": {"english": "regulation", "synonyms": ["নিয়মাবলী"], "category": "legal_framework"},
        "সংবিধান": {"english": "constitution", "synonyms": ["মূল আইন"], "category": "legal_framework"},
        "সার্কুলার": {"english": "circular", "synonyms": ["পরিপত্র"], "category": "legal_documents"},
        "এসআরও": {"english": "sro", "synonyms": ["সংবিধিবদ্ধ নিয়মাবলী আদেশ"], "category": "legal_documents"},
        "গেজেট": {"english": "gazette", "synonyms": ["সরকারি গেজেট"], "category": "legal_documents"},
        "বিজ্ঞপ্তি": {"english": "notification", "synonyms": ["নোটিশ"], "category": "legal_documents"},
        "আপিল": {"english": "appeal", "synonyms": ["পুনর্বিবেচনা"], "category": "legal_process"},
        "ট্রাইব্যুনাল": {"english": "tribunal", "synonyms": ["বিচারালয়"], "category": "legal_institutions"},
        "আদালত": {"english": "court", "synonyms": ["বিচারালয়"], "category": "legal_institutions"},
        "হাইকোর্ট": {"english": "high_court", "synonyms": ["উচ্চ আদালত"], "category": "legal_institutions"},
        "সুপ্রিম কোর্ট": {"english": "supreme_court", "synonyms": ["সর্বোচ্চ আদালত"], "category": "legal_institutions"},
        "জজ": {"english": "judge", "synonyms": ["বিচারক"], "category": "legal_persons"},
        "আইনজীবী": {"english": "lawyer", "synonyms": ["উকিল"], "category": "legal_persons"},
        "ব্যারিস্টার": {"english": "barrister", "synonyms": ["আইনজীবী"], "category": "legal_persons"},
        "নোটিশ": {"english": "notice", "synonyms": ["বিজ্ঞপ্তি"], "category": "legal_process"},
        "জরিমানা": {"english": "penalty", "synonyms": ["দণ্ড", "ফাইন"], "category": "legal_consequences"},
        "শাস্তি": {"english": "punishment", "synonyms": ["দণ্ড"], "category": "legal_consequences"},
        "সুদ": {"english": "interest", "synonyms": ["ইন্টারেস্ট"], "category": "financial_terms"},
        "ক্ষতিপূরণ": {"english": "compensation", "synonyms": ["কম্পেনসেশন"], "category": "legal_remedies"},
        "জামিন": {"english": "bail", "synonyms": ["জামানত"], "category": "legal_process"},
        "হেফাজত": {"english": "custody", "synonyms": ["জেল"], "category": "legal_consequences"},
        "অভিযোগ": {"english": "allegation", "synonyms": ["দোষারোপ"], "category": "legal_process"},
        "প্রমাণ": {"english": "evidence", "synonyms": ["সাক্ষ্য"], "category": "legal_process"},
        "সাক্ষী": {"english": "witness", "synonyms": ["সাক্ষ্যদাতা"], "category": "legal_persons"},
        "রায়": {"english": "judgment", "synonyms": ["রায়"], "category": "legal_outcomes"},
        "রাইট": {"english": "writ", "synonyms": ["রিট"], "category": "legal_remedies"},
        "আবেদন": {"english": "application", "synonyms": ["দরখাস্ত"], "category": "legal_process"},
        "মামলা": {"english": "case", "synonyms": ["কেস"], "category": "legal_process"},
        "নথি": {"english": "document", "synonyms": ["দলিল"], "category": "legal_documents"},
        "চুক্তি": {"english": "contract", "synonyms": ["করার"], "category": "legal_documents"},
        "লাইসেন্স": {"english": "license", "synonyms": ["অনুমতিপত্র"], "category": "legal_documents"},
        "পারমিট": {"english": "permit", "synonyms": ["অনুমতি"], "category": "legal_documents"},
        "সার্টিফিকেট": {"english": "certificate", "synonyms": ["সনদপত্র"], "category": "legal_documents"},
        "রেজিস্ট্রেশন": {"english": "registration", "synonyms": ["নিবন্ধন"], "category": "legal_process"},
        "নবায়ন": {"english": "renewal", "synonyms": ["পুনর্নবীকরণ"], "category": "legal_process"},

        # Financial Terms (50 terms)
        "আয়": {"english": "income", "synonyms": ["উপার্জন", "প্রাপ্তি"], "category": "financial_terms"},
        "বেতন": {"english": "salary", "synonyms": ["সংস্থান", "মজুরি"], "category": "income_types"},
        "ব্যবসা": {"english": "business", "synonyms": ["ব্যবসায়িক", "কারবার"], "category": "income_types"},
        "ভাড়া": {"english": "rent", "synonyms": ["ভাড়া আয়"], "category": "income_types"},
        "কমিশন": {"english": "commission", "synonyms": ["দালালি"], "category": "income_types"},
        "রয়্যালটি": {"english": "royalty", "synonyms": ["মেধাসম্পদ আয়"], "category": "income_types"},
        "লাইসেন্স ফি": {"english": "license_fee", "synonyms": ["অনুমতিপত্র ফি"], "category": "income_types"},
        "সম্মানী": {"english": "honorarium", "synonyms": ["সম্মানিত পারিশ্রমিক"], "category": "income_types"},
        "পুরস্কার": {"english": "prize", "synonyms": ["পুরস্কার প্রাপ্তি"], "category": "income_types"},
        "লটারি": {"english": "lottery", "synonyms": ["লটারি প্রাপ্তি"], "category": "income_types"},
        "মূলধন": {"english": "capital", "synonyms": ["পুঁজি"], "category": "financial_terms"},
        "মুনাফা": {"english": "profit", "synonyms": ["লাভ"], "category": "financial_terms"},
        "লোকসান": {"english": "loss", "synonyms": ["ক্ষতি"], "category": "financial_terms"},
        "বিনিয়োগ": {"english": "investment", "synonyms": ["ইনভেস্টমেন্ট"], "category": "financial_terms"},
        "সঞ্চয়": {"english": "savings", "synonyms": ["সেভিংস"], "category": "financial_terms"},
        "ঋণ": {"english": "loan", "synonyms": ["লোন", "ধার"], "category": "financial_terms"},
        "সম্পদ": {"english": "assets", "synonyms": ["সম্পত্তি"], "category": "financial_terms"},
        "দায়": {"english": "liability", "synonyms": ["দেনা"], "category": "financial_terms"},
        "ইক্যুইটি": {"english": "equity", "synonyms": ["স্বত্ব"], "category": "financial_terms"},
        "নগদ": {"english": "cash", "synonyms": ["ক্যাশ"], "category": "financial_terms"},
        "ব্যাংক": {"english": "bank", "synonyms": ["ব্যাংকিং"], "category": "financial_institutions"},
        "শাখা": {"english": "branch", "synonyms": ["ব্রাঞ্চ"], "category": "financial_institutions"},
        "একাউন্ট": {"english": "account", "synonyms": ["হিসাব"], "category": "financial_terms"},
        "ব্যালেন্স": {"english": "balance", "synonyms": ["জের"], "category": "financial_terms"},
        "ট্রানজেকশন": {"english": "transaction", "synonyms": ["লেনদেন"], "category": "financial_terms"},
        "ট্রান্সফার": {"english": "transfer", "synonyms": ["স্থানান্তর"], "category": "financial_terms"},
        "জমা": {"english": "deposit", "synonyms": ["ডিপোজিট"], "category": "financial_terms"},
        "উত্তোলন": {"english": "withdrawal", "synonyms": ["তোলা"], "category": "financial_terms"},
        "চেক": {"english": "cheque", "synonyms": ["চেকবুক"], "category": "financial_instruments"},
        "ড্রাফট": {"english": "draft", "synonyms": ["ব্যাংক ড্রাফট"], "category": "financial_instruments"},
        "পে অর্ডার": {"english": "pay_order", "synonyms": ["পেমেন্ট অর্ডার"], "category": "financial_instruments"},
        "ক্রেডিট কার্ড": {"english": "credit_card", "synonyms": ["ক্রেডিট"], "category": "financial_instruments"},
        "ডেবিট কার্ড": {"english": "debit_card", "synonyms": ["ডেবিট"], "category": "financial_instruments"},
        "এটিএম": {"english": "atm", "synonyms": ["অটো টেলার মেশিন"], "category": "financial_services"},
        "অনলাইন ব্যাংকিং": {"english": "online_banking", "synonyms": ["ইন্টারনেট ব্যাংকিং"], "category": "financial_services"},
        "মোবাইল ব্যাংকিং": {"english": "mobile_banking", "synonyms": ["এম ব্যাংকিং"], "category": "financial_services"},
        "রেমিট্যান্স": {"english": "remittance", "synonyms": ["প্রবাসী আয়"], "category": "financial_services"},
        "এক্সচেঞ্জ রেট": {"english": "exchange_rate", "synonyms": ["বিনিময় হার"], "category": "financial_terms"},
        "মুদ্রা": {"english": "currency", "synonyms": ["কারেন্সি"], "category": "financial_terms"},
        "বৈদেশিক মুদ্রা": {"english": "foreign_currency", "synonyms": ["ফরেন কারেন্সি"], "category": "financial_terms"},
        "ডলার": {"english": "dollar", "synonyms": ["ইউএস ডলার"], "category": "currency"},
        "ইউরো": {"english": "euro", "synonyms": ["ইউরোপীয় মুদ্রা"], "category": "currency"},
        "পাউন্ড": {"english": "pound", "synonyms": ["ব্রিটিশ পাউন্ড"], "category": "currency"},
        "ইয়েন": {"english": "yen", "synonyms": ["জাপানি ইয়েন"], "category": "currency"},
        "রুপি": {"english": "rupee", "synonyms": ["ভারতীয় রুপি"], "category": "currency"},
        "রিয়াল": {"english": "riyal", "synonyms": ["সৌদি রিয়াল"], "category": "currency"},
        "দিরহাম": {"english": "dirham", "synonyms": ["আরব দিরহাম"], "category": "currency"},
        "দিনার": {"english": "dinar", "synonyms": ["কুয়েতি দিনার"], "category": "currency"},
        "রিঙ্গিত": {"english": "ringgit", "synonyms": ["মালয়েশিয়ান রিঙ্গিত"], "category": "currency"},
        "রুবল": {"english": "ruble", "synonyms": ["রাশিয়ান রুবল"], "category": "currency"},

        # Business Terms (40 terms)
        "কোম্পানি": {"english": "company", "synonyms": ["প্রতিষ্ঠান"], "category": "business_entities"},
        "কর্পোরেশন": {"english": "corporation", "synonyms": ["কর্পোরেট"], "category": "business_entities"},
        "পার্টনারশিপ": {"english": "partnership", "synonyms": ["অংশীদারিত্ব"], "category": "business_entities"},
        "একক মালিকানা": {"english": "sole_proprietorship", "synonyms": ["একমালিকানা"], "category": "business_entities"},
        "এনজিও": {"english": "ngo", "synonyms": ["বেসরকারি সংস্থা"], "category": "business_entities"},
        "সমবায়": {"english": "cooperative", "synonyms": ["সমবায় সমিতি"], "category": "business_entities"},
        "ট্রাস্ট": {"english": "trust", "synonyms": ["ন্যাস"], "category": "business_entities"},
        "ফাউন্ডেশন": {"english": "foundation", "synonyms": ["প্রতিষ্ঠান"], "category": "business_entities"},
        "শেয়ার": {"english": "share", "synonyms": ["স্টক"], "category": "financial_instruments"},
        "ডিভিডেন্ড": {"english": "dividend", "synonyms": ["লভ্যাংশ"], "category": "financial_instruments"},
        "বন্ড": {"english": "bond", "synonyms": ["বন্ধপত্র"], "category": "financial_instruments"},
        "ডিবেঞ্চার": {"english": "debenture", "synonyms": ["ঋণপত্র"], "category": "financial_instruments"},
        "মিউচুয়াল ফান্ড": {"english": "mutual_fund", "synonyms": ["পারস্পরিক তহবিল"], "category": "financial_instruments"},
        "ইটিএফ": {"english": "etf", "synonyms": ["এক্সচেঞ্জ ট্রেডেড ফান্ড"], "category": "financial_instruments"},
        "আইপিও": {"english": "ipo", "synonyms": ["প্রাথমিক গণ প্রস্তাব"], "category": "capital_market"},
        "রাইট ইস্যু": {"english": "rights_issue", "synonyms": ["অধিকার ইস্যু"], "category": "capital_market"},
        "বোনাস শেয়ার": {"english": "bonus_share", "synonyms": ["বিনামূল্যে শেয়ার"], "category": "capital_market"},
        "স্টক এক্সচেঞ্জ": {"english": "stock_exchange", "synonyms": ["শেয়ার বাজার"], "category": "capital_market"},
        "ব্রোকার": {"english": "broker", "synonyms": ["দালাল"], "category": "capital_market"},
        "পোর্টফলিও": {"english": "portfolio", "synonyms": ["বিনিয়োগ সমূহ"], "category": "investment_terms"},
        "ডাইভার্সিফিকেশন": {"english": "diversification", "synonyms": ["বৈচিত্র্যকরণ"], "category": "investment_terms"},
        "রিস্ক": {"english": "risk", "synonyms": ["ঝুঁকি"], "category": "investment_terms"},
        "রিটার্ন": {"english": "return", "synonyms": ["লাভ"], "category": "investment_terms"},
        "ইয়িল্ড": {"english": "yield", "synonyms": ["ফলন"], "category": "investment_terms"},
        "ভলাটিলিটি": {"english": "volatility", "synonyms": ["অস্থিরতা"], "category": "investment_terms"},
        "লিকুইডিটি": {"english": "liquidity", "synonyms": ["তরলতা"], "category": "investment_terms"},
        "ক্যাপিটাল গেইন": {"english": "capital_gain", "synonyms": ["মূলধনী লাভ"], "category": "investment_terms"},
        "ক্যাপিটাল লস": {"english": "capital_loss", "synonyms": ["মূলধনী ক্ষতি"], "category": "investment_terms"},
        "ব্যালেন্স শিট": {"english": "balance_sheet", "synonyms": ["উদ্বৃত্তপত্র"], "category": "accounting_terms"},
        "ইনকাম স্টেটমেন্ট": {"english": "income_statement", "synonyms": ["আয় বিবরণী"], "category": "accounting_terms"},
        "ক্যাশ ফ্লো": {"english": "cash_flow", "synonyms": ["নগদ প্রবাহ"], "category": "accounting_terms"},
        "অডিট": {"english": "audit", "synonyms": ["নিরীক্ষা"], "category": "accounting_terms"},
        "অডিটর": {"english": "auditor", "synonyms": ["নিরীক্ষক"], "category": "accounting_terms"},
        "একাউন্ট্যান্ট": {"english": "accountant", "synonyms": ["হিসাবরক্ষক"], "category": "accounting_terms"},
        "বুককিপিং": {"english": "bookkeeping", "synonyms": ["হিসাব রক্ষণ"], "category": "accounting_terms"},
        "জার্নাল": {"english": "journal", "synonyms": ["দৈনিক হিসাব"], "category": "accounting_terms"},
        "লেজার": {"english": "ledger", "synonyms": ["খতিয়ান"], "category": "accounting_terms"},
        "ট্রায়াল ব্যালেন্স": {"english": "trial_balance", "synonyms": ["রুঢ় উদ্বৃত্তপত্র"], "category": "accounting_terms"},
        "ডেপ্রিসিয়েশন": {"english": "depreciation", "synonyms": ["অবচয়"], "category": "accounting_terms"},
        "আমোর্টাইজেশন": {"english": "amortization", "synonyms": ["ক্রমান্বয়ে হ্রাস"], "category": "accounting_terms"},

        # Currency and Numbers (30 terms)
        "টাকা": {"english": "taka", "synonyms": ["টক", "পয়সা"], "category": "currency"},
        "পয়সা": {"english": "paisa", "synonyms": ["টাকার ভগ্নাংশ"], "category": "currency"},
        "হাজার": {"english": "thousand", "synonyms": ["১০০০"], "category": "numbers"},
        "লাখ": {"english": "lakh", "synonyms": ["১০০,০০০"], "category": "numbers"},
        "কোটি": {"english": "crore", "synonyms": ["১,০০,০০,০০০"], "category": "numbers"},
        "শতকরা": {"english": "percentage", "synonyms": ["%", "পার্সেন্ট"], "category": "numbers"},
        "এক": {"english": "one", "synonyms": ["১"], "category": "numbers"},
        "দুই": {"english": "two", "synonyms": ["২"], "category": "numbers"},
        "তিন": {"english": "three", "synonyms": ["৩"], "category": "numbers"},
        "চার": {"english": "four", "synonyms": ["৪"], "category": "numbers"},
        "পাঁচ": {"english": "five", "synonyms": ["৫"], "category": "numbers"},
        "ছয়": {"english": "six", "synonyms": ["৬"], "category": "numbers"},
        "সাত": {"english": "seven", "synonyms": ["৭"], "category": "numbers"},
        "আট": {"english": "eight", "synonyms": ["৮"], "category": "numbers"},
        "নয়": {"english": "nine", "synonyms": ["৯"], "category": "numbers"},
        "দশ": {"english": "ten", "synonyms": ["১০"], "category": "numbers"},
        "বিশ": {"english": "twenty", "synonyms": ["২০"], "category": "numbers"},
        "ত্রিশ": {"english": "thirty", "synonyms": ["৩০"], "category": "numbers"},
        "চল্লিশ": {"english": "forty", "synonyms": ["৪০"], "category": "numbers"},
        "পঞ্চাশ": {"english": "fifty", "synonyms": ["৫০"], "category": "numbers"},
        "ষাট": {"english": "sixty", "synonyms": ["৬০"], "category": "numbers"},
        "সত্তর": {"english": "seventy", "synonyms": ["৭০"], "category": "numbers"},
        "আশি": {"english": "eighty", "synonyms": ["৮০"], "category": "numbers"},
        "নব্বই": {"english": "ninety", "synonyms": ["৯০"], "category": "numbers"},
        "একশত": {"english": "hundred", "synonyms": ["১০০"], "category": "numbers"},
        "দুইশত": {"english": "two_hundred", "synonyms": ["২০০"], "category": "numbers"},
        "তিনশত": {"english": "three_hundred", "synonyms": ["৩০০"], "category": "numbers"},
        "পাঁচশত": {"english": "five_hundred", "synonyms": ["৫০০"], "category": "numbers"},
        "এক হাজার": {"english": "one_thousand", "synonyms": ["১০০০"], "category": "numbers"},
        "দশ হাজার": {"english": "ten_thousand", "synonyms": ["১০,০০০"], "category": "numbers"}
    }
    
    # Create categorized structure
    term_categories = {}
    for term, data in comprehensive_terms.items():
        category = data.get("category", "misc")
        if category not in term_categories:
            term_categories[category] = []
        term_categories[category].append(term)
    
    # Advanced parsing patterns
    parsing_patterns = {
        "conditional_sentences": {
            "if_then_patterns": [
                r'যদি\s+(.+?)\s+তাহলে\s+(.+)',
                r'(.+?)\s+হলে\s+(.+)',
                r'(.+?)\s+ক্ষেত্রে\s+(.+)',
                r'যেক্ষেত্রে\s+(.+?)\s+সেক্ষেত্রে\s+(.+)'
            ]
        },
        "question_patterns": {
            "amount_questions": [
                r'কত\s+(টাকা|কর|পয়সা)',
                r'কি\s+পরিমাণ',
                r'কেমন\s+(হার|রেট)',
                r'কতটুকু\s+(দিতে|পরিশোধ)'
            ],
            "form_questions": [
                r'কোন\s+(ফরম|ফর্ম)',
                r'কি\s+(ফরম|ফর্ম)',
                r'কী\s+(দাখিল|জমা)',
                r'কোনটি\s+(প্রয়োজন|লাগবে)'
            ]
        },
        "compound_sentences": {
            "conjunctions": ["এবং", "ও", "আর", "তবে", "কিন্তু", "যদিও", "তথাপি"],
            "sentence_connectors": [
                r'(.+?)\s+(এবং|ও|আর)\s+(.+)',
                r'(.+?)\s+(তবে|কিন্তু)\s+(.+)'
            ]
        },
        "numerical_processing": {
            "amount_patterns": [
                r'(\d+)\s*(হাজার|লাখ|কোটি)\s*(টাকা)?',
                r'([০-৯]+)\s*(হাজার|লাখ|কোটি)\s*(টাকা)?'
            ],
            "percentage_patterns": [
                r'(\d+)\s*(%|শতকরা|পার্সেন্ট)',
                r'([০-৯]+)\s*(%|শতকরা|পার্সেন্ট)'
            ]
        }
    }
    
    # Contextual rules
    contextual_rules = {
        "income_context": {
            "employment_indicators": ["বেতন", "সংস্থান", "চাকরি", "কর্মচারী"],
            "business_indicators": ["ব্যবসা", "ব্যবসায়িক", "কারবার", "বাণিজ্য"],
            "rental_indicators": ["ভাড়া", "ভাড়াটিয়া", "বাড়ি ভাড়া"],
            "interest_indicators": ["সুদ", "ইন্টারেস্ট", "ব্যাংক সুদ"]
        },
        "amount_context": {
            "currency_indicators": ["টাকা", "টক", "পয়সা", "BDT"],
            "amount_qualifiers": ["মোট", "সর্বমোট", "সর্বোচ্চ", "সর্বনিম্ন"]
        }
    }
    
    # Create final dictionary structure
    final_dictionary = {
        "metadata": {
            "purpose": "Comprehensive Bengali legal terms for advanced tax processing",
            "version": "2.1.0",
            "creation_date": datetime.now().isoformat(),
            "total_term_count": len(comprehensive_terms),
            "categories_count": len(term_categories),
            "parsing_patterns_count": len(parsing_patterns),
            "contextual_rules_count": len(contextual_rules)
        },
        "terms": comprehensive_terms,
        "term_categories": term_categories,
        "parsing_patterns": parsing_patterns,
        "contextual_rules": contextual_rules,
        "numerical_patterns": {
            "bengali_numbers": {
                "digits": {
                    "০": "0", "১": "1", "২": "2", "৩": "3", "৪": "4",
                    "৫": "5", "৬": "6", "৭": "7", "৮": "8", "৯": "9"
                },
                "written_numbers": {
                    "এক": "1", "দুই": "2", "তিন": "3", "চার": "4", "পাঁচ": "5",
                    "ছয়": "6", "সাত": "7", "আট": "8", "নয়": "9", "দশ": "10"
                }
            }
        }
    }
    
    return final_dictionary

def main():
    """
    Main execution function
    """
    output_file = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap/phase0_completion_sprint/expanded_data/comprehensive_bengali_dictionary_200plus.json"
    
    try:
        print("🚀 Creating Comprehensive 200+ Term Bengali Dictionary...")
        
        comprehensive_dict = create_comprehensive_dictionary()
        
        # Save dictionary
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(comprehensive_dict, file, ensure_ascii=False, indent=2)
        
        print("\n" + "="*60)
        print("✅ COMPREHENSIVE DICTIONARY CREATED SUCCESSFULLY")
        print("="*60)
        print(f"📊 Total terms: {comprehensive_dict['metadata']['total_term_count']}")
        print(f"📋 Categories: {comprehensive_dict['metadata']['categories_count']}")
        print(f"🔧 Parsing patterns: {comprehensive_dict['metadata']['parsing_patterns_count']}")
        print(f"📄 File saved: {output_file}")
        print("="*60)
        
        return comprehensive_dict
        
    except Exception as e:
        print(f"❌ Error creating dictionary: {str(e)}")
        raise

if __name__ == "__main__":
    main()