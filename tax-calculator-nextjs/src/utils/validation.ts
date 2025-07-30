// Form validation utilities and helpers

export const validateNID = (nid: string): boolean => {
  // Bangladesh NID validation: 10, 13, or 17 digits
  const nidRegex = /^[0-9]{10}$|^[0-9]{13}$|^[0-9]{17}$/
  return nidRegex.test(nid)
}

export const validateAge = (age: number): boolean => {
  return age >= 18 && age <= 100
}

export const validateAmount = (amount: number): boolean => {
  return amount >= 0 && amount <= 999999999 // Max 99.99 crore
}

export const validatePhone = (phone: string): boolean => {
  // Bangladesh mobile number validation
  const phoneRegex = /^(?:\+88|88)?(01[3-9]\d{8})$/
  return phoneRegex.test(phone)
}

export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

export const sanitizeNumericInput = (value: string): number => {
  // Remove non-numeric characters except decimal point
  const cleaned = value.replace(/[^0-9.]/g, '')
  const parsed = parseFloat(cleaned)
  return isNaN(parsed) ? 0 : Math.max(0, parsed)
}

export const formatInputAmount = (value: number): string => {
  if (value === 0) return ''
  return value.toString()
}

// Tax year validation
export const getCurrentTaxYear = (): string => {
  const currentDate = new Date()
  const currentYear = currentDate.getFullYear()
  const currentMonth = currentDate.getMonth() + 1 // 0-indexed
  
  // Tax year in Bangladesh runs from July 1 to June 30
  if (currentMonth >= 7) {
    return `${currentYear}-${(currentYear + 1).toString().slice(-2)}`
  } else {
    return `${currentYear - 1}-${currentYear.toString().slice(-2)}`
  }
}

export const getValidTaxYears = (): string[] => {
  const currentTaxYear = getCurrentTaxYear()
  const currentYear = parseInt(currentTaxYear.split('-')[0])
  
  return [
    `${currentYear}-${(currentYear + 1).toString().slice(-2)}`, // Current year
    `${currentYear - 1}-${currentYear.toString().slice(-2)}`, // Previous year
    `${currentYear - 2}-${(currentYear - 1).toString().slice(-2)}`, // Two years ago
  ]
}