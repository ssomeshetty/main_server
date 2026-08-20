'use client';

import { useState } from 'react';
import { Locale } from '@/lib/dictionary';

interface FinancialSectionProps {
  declaration: any;
  lang: Locale;
  dictionary: any;
}

// Format currency in Indian Rupees
function formatCurrency(amount: number, lang: Locale): string {
  if (!amount) return lang === 'kn' ? 'ಮಾಹಿತಿ ಲಭ್ಯವಿಲ್ಲ' : 'Not available';
  
  const formatter = new Intl.NumberFormat(lang === 'kn' ? 'en-IN' : 'en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  });
  
  return formatter.format(amount);
}

function formatCrore(amount: number, lang: Locale): string {
  if (!amount) return lang === 'kn' ? 'ಮಾಹಿತಿ ಲಭ್ಯವಿಲ್ಲ' : 'Not available';
  
  const crore = amount / 10000000;
  const formatted = crore.toLocaleString(lang === 'kn' ? 'en-IN' : 'en-IN', {
    maximumFractionDigits: 2,
  });
  
  return lang === 'kn'
    ? `₹ ${formatted} ಕೋಟಿ`
    : `₹ ${formatted} Crore`;
}

export default function FinancialSection({ declaration, lang, dictionary }: FinancialSectionProps) {
  const [showDetails, setShowDetails] = useState(false);

  const totalAssets = declaration.total_assets || 0;
  const totalLiabilities = declaration.total_liabilities || 0;
  const netWorth = declaration.net_worth || (totalAssets - totalLiabilities);

  const assetsPercentage = totalAssets > 0 ? Math.min((totalLiabilities / totalAssets) * 100, 100) : 0;

  // Color coding based on net worth
  const netWorthColor = netWorth >= 0 ? 'text-green-600' : 'text-red-600';
  const netWorthBg = netWorth >= 0 ? 'bg-green-50' : 'bg-red-50';

  return (
    <section className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-100 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 id="financial-heading" className="text-xl font-bold text-gray-900">
            {dictionary.title}
          </h2>
          <p className="text-sm text-gray-500 mt-1">
            {dictionary.yearLabel} {declaration.declaration_year}
          </p>
        </div>

        {/* Declaration Link */}
        {declaration.declaration_url && (
          <a
            href={declaration.declaration_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 text-sm font-medium"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
            {dictionary.viewAffidavit}
          </a>
        )}
      </div>

      <div className="p-6">
        {/* Net Worth Summary */}
        <div className={`rounded-xl p-6 mb-6 ${netWorthBg}`}>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
            <div>
              <p className="text-sm text-gray-600 mb-1">{dictionary.totalAssets}</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCrore(totalAssets, lang)}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600 mb-1">{dictionary.totalLiabilities}</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCrore(totalLiabilities, lang)}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600 mb-1">{dictionary.netWorth}</p>
              <p className={`text-2xl font-bold ${netWorthColor}`}>
                {formatCrore(netWorth, lang)}
              </p>
            </div>
          </div>

          {/* Visual Bar */}
          <div className="mt-6">
            <div className="flex h-4 rounded-full overflow-hidden bg-gray-200">
              <div 
                className="bg-green-500"
                style={{ width: `${100 - assetsPercentage}%` }}
                aria-hidden="true"
              />
              <div 
                className="bg-red-400"
                style={{ width: `${assetsPercentage}%` }}
                aria-hidden="true"
              />
            </div>
            <div className="flex justify-between mt-2 text-xs text-gray-500">
              <span>{dictionary.assets}</span>
              <span>{dictionary.liabilities}</span>
            </div>
          </div>
        </div>

        {/* Asset Breakdown (Collapsible) */}
        <div>
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="flex items-center justify-between w-full text-left"
            aria-expanded={showDetails}
            aria-controls="asset-details"
          >
            <h3 className="text-lg font-semibold text-gray-800">
              {dictionary.assetBreakdown}
            </h3>
            <svg 
              className={`w-5 h-5 text-gray-400 transition-transform ${showDetails ? 'rotate-180' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {showDetails && (
            <div id="asset-details" className="mt-4">
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {/* Immovable Assets */}
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-500 uppercase tracking-wide mb-2">
                    {dictionary.immovableAssets}
                  </p>
                  <p className="font-semibold text-gray-900">
                    {formatCrore(
                      (declaration.residential_property_value || 0) +
                      (declaration.commercial_property_value || 0) +
                      (declaration.agricultural_land_value || 0),
                      lang
                    )}
                  </p>
                  <div className="mt-2 space-y-1 text-sm">
                    <p className="text-gray-600">
                      {dictionary.residential}: {formatCurrency(declaration.residential_property_value, lang)}
                    </p>
                    <p className="text-gray-600">
                      {dictionary.commercial}: {formatCurrency(declaration.commercial_property_value, lang)}
                    </p>
                    <p className="text-gray-600">
                      {dictionary.land}: {formatCurrency(declaration.agricultural_land_value, lang)}
                    </p>
                  </div>
                </div>

                {/* Movable Assets */}
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-500 uppercase tracking-wide mb-2">
                    {dictionary.movableAssets}
                  </p>
                  <p className="font-semibold text-gray-900">
                    {formatCrore(
                      (declaration.bank_deposits || 0) +
                      (declaration.shares_and_securities || 0) +
                      (declaration.vehicles_value || 0) +
                      (declaration.jewelry_value || 0),
                      lang
                    )}
                  </p>
                  <div className="mt-2 space-y-1 text-sm">
                    <p className="text-gray-600">
                      {dictionary.bankDeposits}: {formatCurrency(declaration.bank_deposits, lang)}
                    </p>
                    <p className="text-gray-600">
                      {dictionary.shares}: {formatCurrency(declaration.shares_and_securities, lang)}
                    </p>
                    <p className="text-gray-600">
                      {dictionary.vehicles}: {formatCurrency(declaration.vehicles_value, lang)}
                    </p>
                  </div>
                </div>

                {/* Liabilities */}
                <div className="p-4 bg-red-50 rounded-lg">
                  <p className="text-xs text-red-500 uppercase tracking-wide mb-2">
                    {dictionary.totalLiabilities}
                  </p>
                  <p className="font-semibold text-gray-900">
                    {formatCrore(totalLiabilities, lang)}
                  </p>
                  <div className="mt-2 space-y-1 text-sm">
                    <p className="text-gray-600">
                      {dictionary.personalLoans}: {formatCurrency(declaration.personal_loans, lang)}
                    </p>
                    <p className="text-gray-600">
                      {dictionary.businessLoans}: {formatCurrency(declaration.business_loans, lang)}
                    </p>
                    <p className="text-gray-600">
                      {dictionary.mortgage}: {formatCurrency(declaration.mortgage, lang)}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Verification Badge */}
      <div className="px-6 py-4 bg-gray-50 border-t border-gray-100 flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <svg className="w-4 h-4 text-gray-400" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
          </svg>
          <span>
            {declaration.is_verified 
              ? dictionary.verifiedSource 
              : dictionary.unverifiedSource}
          </span>
        </div>
        <p className="text-xs text-gray-400">
          {dictionary.sourceDisclaimer}
        </p>
      </div>
    </section>
  );
}