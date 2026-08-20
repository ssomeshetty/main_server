'use client';

import { useState } from 'react';
import { Locale } from '@/lib/dictionary';

interface LegalRecordsSectionProps {
  records: any[];
  lang: Locale;
  dictionary: any;
}

// Status color mapping
const statusColors: Record<string, { bg: string; text: string }> = {
  charges_filed: { bg: 'bg-orange-100', text: 'text-orange-800' },
  trial_in_progress: { bg: 'bg-blue-100', text: 'text-blue-800' },
  admitted: { bg: 'bg-yellow-100', text: 'text-yellow-800' },
  discharged: { bg: 'bg-green-100', text: 'text-green-800' },
  acquitted: { bg: 'bg-green-100', text: 'text-green-800' },
  convicted: { bg: 'bg-red-100', text: 'text-red-800' },
  pending: { bg: 'bg-gray-100', text: 'text-gray-800' },
  withdrawn: { bg: 'bg-gray-100', text: 'text-gray-800' },
};

export default function LegalRecordsSection({ records, lang, dictionary }: LegalRecordsSectionProps) {
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>('all');

  // Filter records by status
  const filteredRecords = filterStatus === 'all' 
    ? records 
    : records.filter(r => r.case_status === filterStatus);

  // Get unique statuses for filter dropdown
  const uniqueStatuses = Array.from(new Set(records.map(r => r.case_status)));

  const toggleExpand = (id: number) => {
    setExpandedId(expandedId === id ? null : id);
  };

  return (
    <section className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-100">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h2 id="legal-heading" className="text-xl font-bold text-gray-900">
              {dictionary.title}
            </h2>
            <p className="text-sm text-gray-500 mt-1">
              {dictionary.recordCount.replace('{count}', records.length.toString())}
            </p>
          </div>

          {/* Status Filter */}
          <div className="flex items-center gap-2">
            <label htmlFor="status-filter" className="text-sm text-gray-600">
              {dictionary.filterByStatus}
            </label>
            <select
              id="status-filter"
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">{dictionary.allStatuses}</option>
              {uniqueStatuses.map(status => (
                <option key={status} value={status}>
                  {dictionary.statusLabels[status] || status}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Records List */}
      <div className="divide-y divide-gray-100">
        {filteredRecords.length === 0 ? (
          <div className="px-6 py-12 text-center text-gray-500">
            <svg className="w-12 h-12 mx-auto text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p>{dictionary.noRecordsFound}</p>
          </div>
        ) : (
          filteredRecords.map((record, index) => {
            const statusStyle = statusColors[record.case_status] || statusColors.pending;
            const isExpanded = expandedId === record.id;

            return (
              <article 
                key={record.id} 
                className={`transition-colors ${isExpanded ? 'bg-blue-50/50' : 'hover:bg-gray-50'}`}
              >
                {/* Summary Row (Clickable) */}
                <button
                  onClick={() => toggleExpand(record.id)}
                  className="w-full px-6 py-4 text-left focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500"
                  aria-expanded={isExpanded}
                  aria-controls={`record-${record.id}`}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-sm font-medium text-gray-500">
                          {dictionary.caseNumber}: {record.case_number}
                        </span>
                        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${statusStyle.bg} ${statusStyle.text}`}>
                          {dictionary.statusLabels[record.case_status] || record.case_status_display}
                        </span>
                      </div>
                      
                      {record.district && (
                        <p className="text-sm text-gray-600">
                          <span className="font-medium">{dictionary.district}:</span> {record.district}
                        </p>
                      )}
                      
                      {record.ipc_sections && record.ipc_sections.length > 0 && (
                        <p className="text-sm text-gray-500 mt-1">
                          <span className="font-medium">{dictionary.sections}:</span> {record.ipc_sections.join(', ')}
                        </p>
                      )}

                      {record.fir_date && (
                        <p className="text-sm text-gray-500 mt-1">
                          <span className="font-medium">{dictionary.firDate}:</span> {record.fir_date}
                        </p>
                      )}
                    </div>

                    {/* Expand/Collapse Icon */}
                    <svg 
                      className={`w-5 h-5 text-gray-400 flex-shrink-0 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                      aria-hidden="true"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </button>

                {/* Expanded Details */}
                {isExpanded && (
                  <div id={`record-${record.id}`} className="px-6 pb-6">
                    {/* Description */}
                    {(record.description_en || record.description_kn) && (
                      <div className="mt-4 p-4 bg-white rounded-lg border border-gray-200">
                        <h4 className="text-sm font-semibold text-gray-700 mb-2">
                          {dictionary.caseDetails}
                        </h4>
                        <p className="text-gray-600">
                          {lang === 'kn' ? record.description_kn : record.description_en}
                        </p>
                      </div>
                    )}

                    {/* Court Information */}
                    {(record.court_name || record.case_type) && (
                      <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                        {record.court_name && (
                          <div>
                            <span className="font-medium text-gray-500">{dictionary.court}:</span>
                            <p className="text-gray-900">{record.court_name}</p>
                          </div>
                        )}
                        {record.case_type && (
                          <div>
                            <span className="font-medium text-gray-500">{dictionary.caseType}:</span>
                            <p className="text-gray-900">{record.case_type}</p>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Next Hearing Date */}
                    {record.next_hearing_date && (
                      <div className="mt-4 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                        <p className="text-sm text-yellow-800">
                          <span className="font-medium">{dictionary.nextHearing}:</span> {record.next_hearing_date}
                        </p>
                      </div>
                    )}

                    {/* Source Link */}
                    {record.case_url && (
                      <div className="mt-4">
                        <a
                          href={record.case_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 text-sm font-medium"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                          </svg>
                          {dictionary.viewOnECI}
                        </a>
                      </div>
                    )}

                    {/* Verification Status */}
                    <div className="mt-4 flex items-center gap-2 text-sm">
                      {record.is_verified ? (
                        <span className="flex items-center gap-1 text-green-600">
                          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
                          </svg>
                          {dictionary.verified}
                        </span>
                      ) : (
                        <span className="flex items-center gap-1 text-gray-500">
                          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd"/>
                          </svg>
                          {dictionary.unverified}
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </article>
            );
          })
        )}
      </div>

      {/* Disclaimer */}
      <div className="px-6 py-4 bg-gray-50 border-t border-gray-100">
        <p className="text-xs text-gray-500 flex items-start gap-2">
          <svg className="w-4 h-4 text-gray-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd"/>
          </svg>
          <span>{dictionary.disclaimer}</span>
        </p>
      </div>
    </section>
  );
}