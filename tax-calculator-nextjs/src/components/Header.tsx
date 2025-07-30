'use client'

import { useState } from 'react'
import { Menu, X, Calculator, Shield, Globe } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

export default function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  const toggleMenu = () => setIsMenuOpen(!isMenuOpen)

  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-md border-b border-gray-200 safe-area-padding">
      <div className="container-responsive">
        <div className="flex items-center justify-between h-16 sm:h-20">
          {/* Logo */}
          <motion.div 
            className="flex items-center space-x-3"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="p-2 bg-bangladeshi-green/10 rounded-xl">
              <Calculator className="w-6 h-6 sm:w-8 sm:h-8 text-bangladeshi-green" />
            </div>
            <div>
              <h1 className="text-lg sm:text-xl font-bold text-gray-900">
                AI Tax Calculator
              </h1>
              <p className="text-xs sm:text-sm text-gray-600 bengali-text">
                বাংলাদেশ
              </p>
            </div>
          </motion.div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <a
              href="#calculator"
              className="text-gray-700 hover:text-bangladeshi-green transition-colors duration-200 font-medium"
            >
              Calculator
            </a>
            <a
              href="#features"
              className="text-gray-700 hover:text-bangladeshi-green transition-colors duration-200 font-medium"
            >
              Features
            </a>
            <a
              href="#api"
              className="text-gray-700 hover:text-bangladeshi-green transition-colors duration-200 font-medium"
            >
              API
            </a>
            <div className="flex items-center space-x-2 px-3 py-2 bg-green-50 rounded-full">
              <Shield className="w-4 h-4 text-bangladeshi-green" />
              <span className="text-sm font-medium text-bangladeshi-green">
                NBR Certified
              </span>
            </div>
          </nav>

          {/* Mobile Menu Button */}
          <button
            onClick={toggleMenu}
            className="md:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors duration-200 touch-target"
            aria-label="Toggle menu"
            aria-expanded={isMenuOpen}
          >
            {isMenuOpen ? (
              <X className="w-6 h-6 text-gray-700" />
            ) : (
              <Menu className="w-6 h-6 text-gray-700" />
            )}
          </button>
        </div>

        {/* Mobile Navigation */}
        <AnimatePresence>
          {isMenuOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.2 }}
              className="md:hidden border-t border-gray-200 bg-white"
            >
              <nav className="py-4 space-y-4">
                <a
                  href="#calculator"
                  className="block px-4 py-3 text-gray-700 hover:text-bangladeshi-green hover:bg-gray-50 rounded-lg transition-all duration-200 font-medium"
                  onClick={() => setIsMenuOpen(false)}
                >
                  <div className="flex items-center space-x-3">
                    <Calculator className="w-5 h-5" />
                    <span>Tax Calculator</span>
                  </div>
                </a>
                
                <a
                  href="#features"
                  className="block px-4 py-3 text-gray-700 hover:text-bangladeshi-green hover:bg-gray-50 rounded-lg transition-all duration-200 font-medium"
                  onClick={() => setIsMenuOpen(false)}
                >
                  <div className="flex items-center space-x-3">
                    <Shield className="w-5 h-5" />
                    <span>Features</span>
                  </div>
                </a>
                
                <a
                  href="#api"
                  className="block px-4 py-3 text-gray-700 hover:text-bangladeshi-green hover:bg-gray-50 rounded-lg transition-all duration-200 font-medium"
                  onClick={() => setIsMenuOpen(false)}
                >
                  <div className="flex items-center space-x-3">
                    <Globe className="w-5 h-5" />
                    <span>Developer API</span>
                  </div>
                </a>

                {/* Mobile-only features */}
                <div className="px-4 py-3 bg-green-50 rounded-lg mx-4">
                  <div className="flex items-center space-x-3">
                    <Shield className="w-5 h-5 text-bangladeshi-green" />
                    <div>
                      <p className="text-sm font-medium text-bangladeshi-green">
                        NBR Certified Engine
                      </p>
                      <p className="text-xs text-gray-600">
                        100% Compliant with Income Tax Act 2023
                      </p>
                    </div>
                  </div>
                </div>

                {/* Language Toggle */}
                <div className="px-4">
                  <div className="flex items-center justify-between py-3 border-t border-gray-200">
                    <span className="text-sm font-medium text-gray-700">
                      Language / ভাষা
                    </span>
                    <div className="flex items-center space-x-2">
                      <button className="px-3 py-1 text-xs font-medium bg-bangladeshi-green text-white rounded-full">
                        EN
                      </button>
                      <button className="px-3 py-1 text-xs font-medium text-gray-600 border border-gray-300 rounded-full bengali-text">
                        বাং
                      </button>
                    </div>
                  </div>
                </div>
              </nav>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </header>
  )
}