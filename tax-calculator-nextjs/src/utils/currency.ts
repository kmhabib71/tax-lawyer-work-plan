// Currency formatting utilities for Bangladesh Taka (BDT)

export const formatBDT = (amount: number): string => {
  return new Intl.NumberFormat('bn-BD', {
    style: 'currency',
    currency: 'BDT',
    currencyDisplay: 'symbol'
  }).format(amount).replace('BDT', '৳')
}

export const formatNumber = (amount: number): string => {
  return new Intl.NumberFormat('bn-BD').format(amount)
}

export const formatPercentage = (rate: number): string => {
  return `${(rate * 100).toFixed(1)}%`
}

export const formatCompactBDT = (amount: number): string => {
  if (amount >= 10000000) { // 1 crore
    return `৳${(amount / 10000000).toFixed(1)}Cr`
  } else if (amount >= 100000) { // 1 lakh
    return `৳${(amount / 100000).toFixed(1)}L`
  } else if (amount >= 1000) { // 1 thousand
    return `৳${(amount / 1000).toFixed(1)}K`
  }
  return formatBDT(amount)
}

export const parseBDTAmount = (value: string): number => {
  // Remove currency symbols and commas, parse as number
  const cleaned = value.replace(/[৳,\s]/g, '')
  return parseFloat(cleaned) || 0
}