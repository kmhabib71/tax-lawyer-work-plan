'use client'

import { useState } from 'react'
import { Calculator, Shield, Zap, CheckCircle, ArrowRight, RefreshCcw } from 'lucide-react'
import { motion } from 'framer-motion'
import TaxCalculatorForm from '@/components/TaxCalculatorForm'
import TaxResult from '@/components/TaxResult'
import Header from '@/components/Header'
import Footer from '@/components/Footer'
import { TaxCalculationResult } from '@/types/tax'

export default function HomePage() {
  const [calculationResult, setCalculationResult] = useState<TaxCalculationResult | null>(null)
  const [isCalculating, setIsCalculating] = useState(false)

  const handleCalculationComplete = (result: TaxCalculationResult) => {
    setCalculationResult(result)
    setIsCalculating(false)
  }

  const handleNewCalculation = () => {
    setCalculationResult(null)
    setIsCalculating(false)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-green-50">
      <Header />
      
      {/* Hero Section */}
      <section className="container-responsive py-8 sm:py-12 lg:py-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-8 sm:mb-12"
        >
          <div className="flex justify-center mb-6">
            <div className="p-4 bg-bangladeshi-green/10 rounded-2xl">
              <Calculator className="w-12 h-12 sm:w-16 sm:h-16 text-bangladeshi-green" />
            </div>
          </div>
          
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-gray-900 mb-4">
            AI Tax Calculator
            <span className="block text-bangladeshi-green bengali-text">বাংলাদেশ</span>
          </h1>
          
          <p className="text-lg sm:text-xl text-gray-600 max-w-3xl mx-auto mb-8">
            ১০০% নির্ভুল কর গণনা করুন আমাদের AI চালিত ট্যাক্স ক্যালকুলেটর দিয়ে।
            <span className="block mt-2 text-base sm:text-lg">
              Calculate your Bangladesh income tax with 100% mathematical precision.
            </span>
          </p>

          {/* Feature badges */}
          <div className="flex flex-wrap justify-center gap-4 mb-8">
            <div className="flex items-center gap-2 bg-white/80 backdrop-blur-sm px-4 py-2 rounded-full shadow-soft">
              <Shield className="w-4 h-4 text-green-600" />
              <span className="text-sm font-medium text-gray-700">100% Secure</span>
            </div>
            <div className="flex items-center gap-2 bg-white/80 backdrop-blur-sm px-4 py-2 rounded-full shadow-soft">
              <Zap className="w-4 h-4 text-blue-600" />
              <span className="text-sm font-medium text-gray-700">&lt;200ms Response</span>
            </div>
            <div className="flex items-center gap-2 bg-white/80 backdrop-blur-sm px-4 py-2 rounded-full shadow-soft">
              <CheckCircle className="w-4 h-4 text-bangladeshi-green" />
              <span className="text-sm font-medium text-gray-700">NBR Compliant</span>
            </div>
          </div>
        </motion.div>

        {/* Main Calculator Interface */}
        <div className="max-w-4xl mx-auto">
          {!calculationResult ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              <TaxCalculatorForm
                onCalculationComplete={handleCalculationComplete}
                isCalculating={isCalculating}
                setIsCalculating={setIsCalculating}
              />
            </motion.div>
          ) : (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.4 }}
            >
              <TaxResult 
                result={calculationResult}
                onNewCalculation={handleNewCalculation}
              />
            </motion.div>
          )}
        </div>
      </section>

      {/* Features Section */}
      {!calculationResult && (
        <section className="container-responsive py-12 sm:py-16 lg:py-20">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="text-center mb-12"
          >
            <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
              Why Choose Our AI Calculator?
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Built with the comprehensive tax engine that covers all eReturn scenarios
            </p>
          </motion.div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.5 + index * 0.1 }}
                className="card-elevated hover:scale-105 transition-transform duration-200"
              >
                <div className="flex items-center mb-4">
                  <div className={`p-3 rounded-xl ${feature.iconBg}`}>
                    <feature.icon className={`w-6 h-6 ${feature.iconColor}`} />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 ml-4">
                    {feature.title}
                  </h3>
                </div>
                <p className="text-gray-600 leading-relaxed">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </section>
      )}

      <Footer />
    </div>
  )
}

const features = [
  {
    icon: Calculator,
    title: '100% Mathematical Precision',
    description: 'Uses Decimal arithmetic with 15-digit precision to eliminate floating-point errors completely.',
    iconBg: 'bg-blue-100',
    iconColor: 'text-blue-600',
  },
  {
    icon: Shield,
    title: 'Complete eReturn Coverage',
    description: 'Handles all 10 income types, 8 taxpayer categories, investment rebates, and surcharges.',
    iconBg: 'bg-green-100',
    iconColor: 'text-green-600',
  },
  {
    icon: Zap,
    title: 'Lightning Fast',
    description: 'Get detailed tax breakdown in under 200ms with comprehensive audit trail.',
    iconBg: 'bg-yellow-100',
    iconColor: 'text-yellow-600',
  },
  {
    icon: CheckCircle,
    title: 'NBR Compliant',
    description: 'Based on Income Tax Act 2023 and Circular 2024-25 with 212 processed topics.',
    iconBg: 'bg-bangladeshi-green/10',
    iconColor: 'text-bangladeshi-green',
  },
  {
    icon: RefreshCcw,
    title: 'Real-time Updates',
    description: 'Always up-to-date with latest tax rules and circular amendments.',
    iconBg: 'bg-purple-100',
    iconColor: 'text-purple-600',
  },
  {
    icon: ArrowRight,
    title: 'Mobile Optimized',
    description: 'Touch-friendly interface designed for smartphones and tablets.',
    iconBg: 'bg-pink-100',
    iconColor: 'text-pink-600',
  },
]