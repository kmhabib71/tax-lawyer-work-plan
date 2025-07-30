'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { motion } from 'framer-motion'
import { 
  User, 
  DollarSign, 
  PiggyBank, 
  Building, 
  CreditCard, 
  ChevronLeft, 
  ChevronRight,
  Calculator,
  Loader2
} from 'lucide-react'
import { toast } from 'sonner'
import { TaxCalculationResult, FormStep, TaxpayerCategory, Gender, SpecialStatus } from '@/types/tax'

// Validation schema
const taxFormSchema = z.object({
  // Taxpayer Info
  name: z.string().min(2, 'Name must be at least 2 characters'),
  nid: z.string().min(10, 'NID must be at least 10 digits'),
  category: z.nativeEnum(TaxpayerCategory),
  gender: z.nativeEnum(Gender),
  age: z.number().min(18, 'Must be at least 18 years old').max(100, 'Age must be realistic'),
  special_status: z.array(z.nativeEnum(SpecialStatus)).default([]),
  
  // Income (simplified for demo) - Handle empty strings by transforming them to 0
  salary: z.number().min(0, 'Salary cannot be negative'),
  house_rent_allowance: z.preprocess(
    (val) => val === '' || val === undefined ? 0 : Number(val),
    z.number().min(0, 'House rent allowance cannot be negative')
  ),
  business_income: z.preprocess(
    (val) => val === '' || val === undefined ? 0 : Number(val),
    z.number().min(0, 'Business income cannot be negative')
  ),
  rental_income: z.preprocess(
    (val) => val === '' || val === undefined ? 0 : Number(val),
    z.number().min(0, 'Rental income cannot be negative')
  ),
  other_income: z.preprocess(
    (val) => val === '' || val === undefined ? 0 : Number(val),
    z.number().min(0, 'Other income cannot be negative')
  ),
  
  // Investments - Handle empty strings by transforming them to 0
  life_insurance: z.preprocess(
    (val) => val === '' || val === undefined ? 0 : Number(val),
    z.number().min(0, 'Life insurance amount cannot be negative')
  ),
  dps: z.preprocess(
    (val) => val === '' || val === undefined ? 0 : Number(val),
    z.number().min(0, 'DPS amount cannot be negative')
  ),
  government_securities: z.preprocess(
    (val) => val === '' || val === undefined ? 0 : Number(val),
    z.number().min(0, 'Government securities amount cannot be negative')
  ),
  stock_market: z.preprocess(
    (val) => val === '' || val === undefined ? 0 : Number(val),
    z.number().min(0, 'Stock market investment cannot be negative')
  ),
})

type TaxFormData = z.infer<typeof taxFormSchema>

interface Props {
  onCalculationComplete: (result: TaxCalculationResult) => void
  isCalculating: boolean
  setIsCalculating: (calculating: boolean) => void
}

export default function TaxCalculatorForm({ 
  onCalculationComplete, 
  isCalculating, 
  setIsCalculating 
}: Props) {
  const [currentStep, setCurrentStep] = useState(0)
  
  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
    watch,
    setValue,
    getValues
  } = useForm<TaxFormData>({
    resolver: zodResolver(taxFormSchema),
    mode: 'onChange',
    defaultValues: {
      category: TaxpayerCategory.INDIVIDUAL,
      gender: Gender.MALE,
      age: 25,
      special_status: [],
      salary: 0,
      house_rent_allowance: 0,
      business_income: 0,
      rental_income: 0,
      other_income: 0,
      life_insurance: 0,
      dps: 0,
      government_securities: 0,
      stock_market: 0,
    }
  })

  const steps = [
    {
      id: FormStep.TAXPAYER_INFO,
      title: 'Personal Information',
      subtitle: 'Basic taxpayer details',
      icon: User,
      bengaliTitle: 'ব্যক্তিগত তথ্য'
    },
    {
      id: FormStep.INCOME_DETAILS,
      title: 'Income Details',
      subtitle: 'All sources of income',
      icon: DollarSign,
      bengaliTitle: 'আয়ের বিস্তারিত'
    },
    {
      id: FormStep.INVESTMENTS,
      title: 'Investments',
      subtitle: 'Tax rebate eligible investments',
      icon: PiggyBank,
      bengaliTitle: 'বিনিয়োগ'
    }
  ]

  const onSubmit = async (data: TaxFormData) => {
    console.log('Form submitted, current step:', currentStep)
    setIsCalculating(true)
    
    try {
      // Transform form data to match our comprehensive tax engine format
      const requestData = {
        taxpayer: {
          name: data.name,
          nid: data.nid,
          category: data.category,
          gender: data.gender,
          age: data.age,
          special_status: data.special_status || [],
          residential_status: 'resident'
        },
        income: {
          employment: {
            basic_salary: data.salary,
            house_rent_allowance: data.house_rent_allowance || 0,
            medical_allowance: 0,
            conveyance_allowance: 0,
            other_allowances: 0,
            bonus: 0,
            overtime: 0
          },
          business: {
            trading_income: data.business_income || 0,
            manufacturing_income: 0,
            service_income: 0,
            professional_income: 0
          },
          property: {
            house_rent: data.rental_income || 0,
            commercial_rent: 0,
            land_rent: 0
          },
          agriculture: {
            crops: 0,
            livestock: 0,
            fisheries: 0,
            poultry: 0
          },
          capital_gains: {
            securities: 0,
            property: 0,
            other_assets: 0
          },
          financial: {
            bank_interest: 0,
            dividends: 0,
            mutual_funds: 0,
            debentures: 0
          },
          other: {
            royalty: 0,
            technical_fees: 0,
            commission: 0,
            lottery_winnings: data.other_income || 0,
            gifts: 0
          },
          export: {
            goods: 0,
            services: 0
          },
          industrial: {
            manufacturing: 0,
            processing: 0
          },
          foreign: {
            employment: 0,
            business: 0,
            investment: 0
          }
        },
        investments: {
          life_insurance: data.life_insurance || 0,
          dps: data.dps || 0,
          government_securities: data.government_securities || 0,
          stock_market: data.stock_market || 0,
          mutual_funds: 0,
          provident_fund: 0,
          superannuation_fund: 0,
          benevolent_fund: 0,
          zakat_fund: 0,
          universal_pension: 0,
          other_investments: 0,
          donations: 0
        },
        assets: {
          land_buildings: 0,
          agricultural_land: 0,
          bank_deposits: 0,
          securities: 0,
          shares: 0,
          bonds: 0,
          business_capital: 0,
          inventory: 0,
          jewelry: 0,
          vehicles: 0,
          furniture: 0,
          other_assets: 0,
          loans_payable: 0,
          other_liabilities: 0
        },
        payments: {
          advance_tax: 0,
          tds: 0,
          ait: 0,
          previous_year_tax: 0,
          penalties: 0,
          interest_paid: 0
        }
      }

      // Call our comprehensive tax calculation API
      const response = await fetch('/api/calculate-tax', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      })

      if (!response.ok) {
        throw new Error('Failed to calculate tax')
      }

      const result = await response.json()
      
      if (result.success) {
        onCalculationComplete(result.data)
        toast.success('Tax calculation completed successfully!')
      } else {
        throw new Error(result.error?.message || 'Calculation failed')
      }
    } catch (error) {
      console.error('Tax calculation error:', error)
      toast.error('Failed to calculate tax. Please try again.')
      setIsCalculating(false)
    }
  }

  const nextStep = () => {
    console.log('Next step clicked, current step:', currentStep, 'total steps:', steps.length)
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1)
    }
  }

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  const currentStepData = steps[currentStep]

  return (
    <div className="card-elevated max-w-2xl mx-auto">
      {/* Step Indicator */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          {steps.map((step, index) => (
            <div
              key={step.id}
              className={`flex items-center ${
                index !== steps.length - 1 ? 'flex-1' : ''
              }`}
            >
              <div
                className={`flex items-center justify-center w-10 h-10 rounded-full ${
                  index <= currentStep
                    ? 'bg-bangladeshi-green text-white'
                    : 'bg-gray-200 text-gray-500'
                } transition-colors duration-200`}
              >
                <step.icon className="w-5 h-5" />
              </div>
              {index !== steps.length - 1 && (
                <div
                  className={`h-1 flex-1 mx-4 rounded ${
                    index < currentStep ? 'bg-bangladeshi-green' : 'bg-gray-200'
                  } transition-colors duration-200`}
                />
              )}
            </div>
          ))}
        </div>
        
        <div className="mt-4 text-center">
          <h2 className="text-xl font-bold text-gray-900">
            {currentStepData.title}
          </h2>
          <p className="text-sm text-gray-600 bengali-text mt-1">
            {currentStepData.bengaliTitle}
          </p>
          <p className="text-sm text-gray-500 mt-1">
            {currentStepData.subtitle}
          </p>
        </div>
      </div>

      {/* Form Content */}
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <motion.div
          key={currentStep}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.3 }}
        >
          {/* Step 0: Personal Information */}
          {currentStep === 0 && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Full Name / পূর্ণ নাম
                  </label>
                  <input
                    {...register('name')}
                    type="text"
                    className="input-primary"
                    placeholder="Enter your full name"
                  />
                  {errors.name && (
                    <p className="text-red-500 text-sm mt-1">{errors.name.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    National ID / জাতীয় পরিচয়পত্র
                  </label>
                  <input
                    {...register('nid')}
                    type="text"
                    className="input-primary"
                    placeholder="10-17 digit NID number"
                  />
                  {errors.nid && (
                    <p className="text-red-500 text-sm mt-1">{errors.nid.message}</p>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Age / বয়স
                  </label>
                  <input
                    {...register('age', { valueAsNumber: true })}
                    type="number"
                    className="input-primary"
                    placeholder="25"
                    min="18"
                    max="100"
                  />
                  {errors.age && (
                    <p className="text-red-500 text-sm mt-1">{errors.age.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Gender / লিঙ্গ
                  </label>
                  <select {...register('gender')} className="input-primary">
                    <option value={Gender.MALE}>Male / পুরুষ</option>
                    <option value={Gender.FEMALE}>Female / মহিলা</option>
                    <option value={Gender.OTHER}>Other / অন্যান্য</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Category / ধরন
                  </label>
                  <select {...register('category')} className="input-primary">
                    <option value={TaxpayerCategory.INDIVIDUAL}>Individual / ব্যক্তি</option>
                    <option value={TaxpayerCategory.COMPANY}>Company / কোম্পানি</option>
                    <option value={TaxpayerCategory.FIRM}>Firm / ফার্ম</option>
                  </select>
                </div>
              </div>

              {/* Special Status */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Special Status / বিশেষ মর্যাদা (if applicable)
                </label>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {Object.values(SpecialStatus).map((status) => (
                    <label key={status} className="flex items-center space-x-3">
                      <input
                        type="checkbox"
                        value={status}
                        {...register('special_status')}
                        className="rounded border-gray-300 text-bangladeshi-green focus:ring-bangladeshi-green"
                      />
                      <span className="text-sm text-gray-700">
                        {getSpecialStatusLabel(status)}
                      </span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Step 1: Income Details */}
          {currentStep === 1 && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Annual Salary / বার্ষিক বেতন (৳)
                  </label>
                  <input
                    {...register('salary', { valueAsNumber: true })}
                    type="number"
                    className="input-primary"
                    placeholder="500000"
                    min="0"
                    step="1000"
                  />
                  {errors.salary && (
                    <p className="text-red-500 text-sm mt-1">{errors.salary.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    House Rent Allowance / বাড়ি ভাড়া ভাতা (৳)
                  </label>
                  <input
                    {...register('house_rent_allowance', { valueAsNumber: true })}
                    type="number"
                    className="input-primary"
                    placeholder="60000"
                    min="0"
                    step="1000"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Business Income / ব্যবসায়িক আয় (৳)
                  </label>
                  <input
                    {...register('business_income', { valueAsNumber: true })}
                    type="number"
                    className="input-primary"
                    placeholder="0"
                    min="0"
                    step="1000"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Rental Income / ভাড়া আয় (৳)
                  </label>
                  <input
                    {...register('rental_income', { valueAsNumber: true })}
                    type="number"
                    className="input-primary"
                    placeholder="0"
                    min="0"
                    step="1000"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Other Income / অন্যান্য আয় (৳)
                </label>
                <input
                  {...register('other_income', { valueAsNumber: true })}
                  type="number"
                  className="input-primary"
                  placeholder="0"
                  min="0"
                  step="1000"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Include dividends, interest, lottery winnings, etc.
                </p>
              </div>
            </div>
          )}

          {/* Step 2: Investments */}
          {currentStep === 2 && (
            <div className="space-y-6">
              <div className="bg-blue-50 p-4 rounded-lg">
                <p className="text-sm text-blue-800">
                  <strong>Investment Rebate:</strong> You can claim up to 15% rebate on eligible investments, 
                  maximum ৳15 lakh per year and cannot exceed 15% of gross tax.
                </p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Life Insurance Premium / জীবন বীমা প্রিমিয়াম (৳)
                  </label>
                  <input
                    {...register('life_insurance', { valueAsNumber: true })}
                    type="number"
                    className="input-primary"
                    placeholder="50000"
                    min="0"
                    step="1000"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    DPS / Savings Certificates / সঞ্চয়পত্র (৳)
                  </label>
                  <input
                    {...register('dps', { valueAsNumber: true })}
                    type="number"
                    className="input-primary"
                    placeholder="200000"
                    min="0"
                    step="1000"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Government Securities / সরকারি সিকিউরিটিজ (৳)
                  </label>
                  <input
                    {...register('government_securities', { valueAsNumber: true })}
                    type="number"
                    className="input-primary"
                    placeholder="0"
                    min="0"
                    step="1000"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Stock Market Investment / শেয়ার বাজার (৳)
                  </label>
                  <input
                    {...register('stock_market', { valueAsNumber: true })}
                    type="number"
                    className="input-primary"
                    placeholder="0"
                    min="0"
                    step="1000"
                  />
                </div>
              </div>
            </div>
          )}
        </motion.div>

        {/* Debug Info - Remove in production */}
        {process.env.NODE_ENV === 'development' && (
          <div className="mt-4 p-3 bg-gray-100 rounded-lg text-xs">
            <p><strong>Current Step:</strong> {currentStep} / {steps.length - 1}</p>
            <p><strong>Form Valid:</strong> {isValid ? 'Yes' : 'No'}</p>
            <p><strong>Is Calculating:</strong> {isCalculating ? 'Yes' : 'No'}</p>
            <p><strong>Show Submit Button:</strong> {currentStep >= steps.length - 1 ? 'Yes' : 'No'}</p>
            {Object.keys(errors).length > 0 && (
              <div className="mt-2">
                <strong>Validation Errors:</strong>
                <ul className="list-disc list-inside mt-1">
                  {Object.entries(errors).map(([field, error]) => (
                    <li key={field} className="text-red-600">
                      {field}: {error?.message}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Navigation Buttons */}
        <div className="flex justify-between pt-6 border-t border-gray-200">
          <button
            type="button"
            onClick={prevStep}
            disabled={currentStep === 0}
            className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            <ChevronLeft className="w-4 h-4" />
            <span>Previous</span>
          </button>

          {currentStep < steps.length - 1 ? (
            <button
              type="button"
              onClick={(e) => {
                e.preventDefault()
                console.log('Next button clicked, preventing default')
                nextStep()
              }}
              className="btn-bangladeshi flex items-center space-x-2"
            >
              <span>Next</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          ) : (
            <button
              type="submit"
              disabled={isCalculating || !isValid}
              className="btn-bangladeshi disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 min-w-[140px] justify-center"
            >
              {isCalculating ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Calculating...</span>
                </>
              ) : (
                <>
                  <Calculator className="w-4 h-4" />
                  <span>Calculate Tax</span>
                </>
              )}
            </button>
          )}
        </div>
      </form>
    </div>
  )
}

function getSpecialStatusLabel(status: SpecialStatus): string {
  switch (status) {
    case SpecialStatus.SENIOR_CITIZEN:
      return 'Senior Citizen (65+) / প্রবীণ নাগরিক'
    case SpecialStatus.DISABLED_PERSON:
      return 'Disabled Person / প্রতিবন্ধী ব্যক্তি'
    case SpecialStatus.FREEDOM_FIGHTER:
      return 'Freedom Fighter / মুক্তিযোদ্ধা'
    case SpecialStatus.WAR_WOUNDED:
      return 'War Wounded / যুদ্ধাহত'
    case SpecialStatus.THIRD_GENDER:
      return 'Third Gender / তৃতীয় লিঙ্গ'
    default:
      return status
  }
}