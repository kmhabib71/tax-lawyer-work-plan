'use client'

import { Calculator, Shield, Heart, Globe, Github, Twitter } from 'lucide-react'

export default function Footer() {
  return (
    <footer className="bg-gray-900 text-white">
      <div className="container-responsive py-12">
        {/* Main Footer Content */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          {/* Brand Section */}
          <div className="md:col-span-2">
            <div className="flex items-center space-x-3 mb-4">
              <div className="p-2 bg-bangladeshi-green/20 rounded-xl">
                <Calculator className="w-6 h-6 text-bangladeshi-green" />
              </div>
              <div>
                <h3 className="text-lg font-bold">AI Tax Calculator BD</h3>
                <p className="text-sm text-gray-400 bengali-text">
                  বাংলাদেশের সবচেয়ে নির্ভুল কর ক্যালকুলেটর
                </p>
              </div>
            </div>
            
            <p className="text-gray-300 text-sm mb-4 max-w-md">
              The most accurate AI-powered tax calculator for Bangladesh, 
              built with comprehensive tax engine covering all eReturn scenarios 
              with 100% mathematical precision.
            </p>
            
            {/* Features */}
            <div className="flex flex-wrap gap-4">
              <div className="flex items-center space-x-2 text-xs bg-gray-800 px-3 py-2 rounded-full">
                <Shield className="w-3 h-3 text-green-400" />
                <span>NBR Compliant</span>
              </div>
              <div className="flex items-center space-x-2 text-xs bg-gray-800 px-3 py-2 rounded-full">
                <Calculator className="w-3 h-3 text-blue-400" />
                <span>100% Accurate</span>
              </div>
              <div className="flex items-center space-x-2 text-xs bg-gray-800 px-3 py-2 rounded-full">
                <Globe className="w-3 h-3 text-purple-400" />
                <span>Mobile First</span>
              </div>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-sm font-semibold mb-4">Quick Links</h4>
            <ul className="space-y-2 text-sm text-gray-300">
              <li>
                <a href="#calculator" className="hover:text-bangladeshi-green transition-colors">
                  Tax Calculator
                </a>
              </li>
              <li>
                <a href="#features" className="hover:text-bangladeshi-green transition-colors">
                  Features
                </a>
              </li>
              <li>
                <a href="#api" className="hover:text-bangladeshi-green transition-colors">
                  Developer API
                </a>
              </li>
              <li>
                <a href="#guides" className="hover:text-bangladeshi-green transition-colors">
                  Tax Guides
                </a>
              </li>
              <li>
                <a href="#support" className="hover:text-bangladeshi-green transition-colors">
                  Support
                </a>
              </li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h4 className="text-sm font-semibold mb-4">Resources</h4>
            <ul className="space-y-2 text-sm text-gray-300">
              <li>
                <a href="#tax-act" className="hover:text-bangladeshi-green transition-colors">
                  Income Tax Act 2023
                </a>
              </li>
              <li>
                <a href="#circular" className="hover:text-bangladeshi-green transition-colors">
                  Tax Circular 2024-25
                </a>
              </li>
              <li>
                <a href="#ereturn" className="hover:text-bangladeshi-green transition-colors">
                  eReturn Guide
                </a>
              </li>
              <li>
                <a href="#faq" className="hover:text-bangladeshi-green transition-colors">
                  FAQ
                </a>
              </li>
              <li>
                <a href="#privacy" className="hover:text-bangladeshi-green transition-colors">
                  Privacy Policy
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Technical Information */}
        <div className="bg-gray-800 rounded-lg p-4 mb-8">
          <h4 className="text-sm font-semibold mb-3 flex items-center">
            <Calculator className="w-4 h-4 mr-2 text-bangladeshi-green" />
            Technical Specifications
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs text-gray-400">
            <div>
              <p className="font-medium text-gray-300">Engine</p>
              <p>Comprehensive Tax Engine v2024.25</p>
            </div>
            <div>
              <p className="font-medium text-gray-300">Precision</p>
              <p>15 Decimal Places (Decimal Arithmetic)</p>
            </div>
            <div>
              <p className="font-medium text-gray-300">Coverage</p>
              <p>212 Tax Topics, 449K+ Rules</p>
            </div>
            <div>
              <p className="font-medium text-gray-300">Response Time</p>
              <p>&lt;200ms Calculation Speed</p>
            </div>
          </div>
        </div>

        {/* Social Links & Copyright */}
        <div className="flex flex-col sm:flex-row items-center justify-between pt-8 border-t border-gray-800">
          <div className="flex items-center space-x-4 mb-4 sm:mb-0">
            <a
              href="https://github.com/ai-tax-bd"
              className="text-gray-400 hover:text-white transition-colors"
              aria-label="GitHub"
            >
              <Github className="w-5 h-5" />
            </a>
            <a
              href="https://twitter.com/aitaxbd"
              className="text-gray-400 hover:text-white transition-colors"
              aria-label="Twitter"
            >
              <Twitter className="w-5 h-5" />
            </a>
          </div>

          <div className="text-center sm:text-right">
            <p className="text-xs text-gray-400 mb-1">
              © 2024 AI Tax Calculator Bangladesh. All rights reserved.
            </p>
            <p className="text-xs text-gray-500 flex items-center justify-center sm:justify-end">
              Made with <Heart className="w-3 h-3 mx-1 text-red-400" /> for Bangladesh
            </p>
          </div>
        </div>

        {/* Disclaimer */}
        <div className="mt-8 p-4 bg-yellow-900/20 border border-yellow-700/30 rounded-lg">
          <p className="text-xs text-yellow-200">
            <strong>Disclaimer:</strong> This calculator is provided for informational purposes only. 
            While we strive for 100% accuracy using the comprehensive tax engine based on Income Tax Act 2023 
            and Circular 2024-25, please consult with a qualified tax professional for complex situations. 
            Always verify calculations with official NBR guidelines.
          </p>
        </div>
      </div>
    </footer>
  )
}