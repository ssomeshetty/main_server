'use client';

import { useState } from 'react';
import { Locale } from '@/lib/dictionary';

interface PublicRecordsSectionProps {
  records: any[];
  lang: Locale;
  dictionary: any;
}

// Record type configurations
const recordTypeConfig: Record<string, { icon: string; color: string; label: string }> = {
  speech: { 
    icon: 'M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z', 
    color: 'bg-blue-100 text-blue-600',
    label: 'Speech'
  },
  statement: { 
    icon: 'M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z', 
    color: 'bg-purple-100 text-purple-600',
    label: 'Statement'
  },
  controversy: { 
    icon: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z', 
    color: 'bg-red-100 text-red-600',
    label: 'Controversy'
  },
  allegation: { 
    icon: 'M13 10V3L4 14h7v7l9-11h-7z', 
    color: 'bg-orange-100 text-orange-600',
    label: 'Allegation'
  },
  promise: { 
    icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z', 
    color: 'bg-green-100 text-green-600',
    label: 'Promise'
  },
  initiative: { 
    icon: 'M13 7h8m0 0v8m0-8l-8 8-4-4-6 6', 
    color: 'bg-teal-100 text-teal-600',
    label: 'Initiative'
  },
  bill_proposed: { 
    icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z', 
    color: 'bg-indigo-100 text-indigo-600',
    label: 'Bill Proposed'
  },
  other: { 
    icon: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z', 
    color: 'bg-gray-100 text-gray-600',
    label: 'Other'
  },
};

export default function PublicRecordsSection({ records, lang, dictionary }: PublicRecordsSectionProps) {
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [filterType, setFilterType] = useState<string>('all');

  // Filter records by type
  const filteredRecords = filterType === 'all' 
    ? records 
    : records.filter(r => r.record_type === filterType);

  // Get unique types for filter dropdown
  const uniqueTypes = [...new Set(records.map(r => r.record_type))];

  const toggleExpand = (id: number) => {
    setExpandedId(expandedId === id ? null : id);
  };

  return (
    <section className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-100">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h2 id="public-records-heading" className="text-xl font-bold text-gray-900">
              {dictionary.title}
            </h2>
            <p className="text-sm text-gray-500 mt-1">
              {dictionary.recordCount.replace('{count}', records.length.toString())}
            </p>
          </div>

          {/* Type Filter */}
          <div className="flex items-center gap-2">
            <label htmlFor="type-filter" className="text-sm text-gray-600">
              {dictionary.filterByType}
            </label>
            <select
              id="type-filter"
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">{dictionary.allTypes}</option>
              {uniqueTypes.map(type => (
                <option key={type} value={type}>
                  {recordTypeConfig[type]?.label || type}
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
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p>{dictionary.noRecordsFound}</p>
          </div>
        ) : (
          filteredRecords.map((record) => {
            const typeConfig = recordTypeConfig[record.record_type] || recordTypeConfig.other;
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
                  <div className="flex items-start gap-4">
                    {/* Type Icon */}
                    <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${typeConfig.color}`}>
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                        <path d={typeConfig.icon} />
                      </svg>
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-semibold text-gray-900 truncate">
                          {lang === 'kn' ? record.title_kn : record.title_en}
                        </h3>
                      </div>

                      {/* Metadata */}
                      <div className="flex flex-wrap items-center gap-3 text-sm text-gray-500">
                        {record.event_date && (
                          <span>{record.event_date}</span>
                        )}
                        {record.location && (
                          <span className="flex items-center gap-1">
                            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd"/>
                            </svg>
                            {record.location}
                          </span>
                        )}
                        {record.source_organization && (
                          <span>{record.source_organization}</span>
                        )}
                      </div>

                      {/* Summary Preview */}
                      {(record.summary_en || record.summary_kn) && (
                        <p className="mt-2 text-gray-600 line-clamp-2">
                          {lang === 'kn' ? record.summary_kn : record.summary_en}
                        </p>
                      )}

                      {/* Categories & Tags */}
                      {(record.categories?.length > 0 || record.tags?.length > 0) && (
                        <div className="mt-2 flex flex-wrap gap-2">
                          {record.categories?.slice(0, 3).map((cat: string) => (
                            <span 
                              key={cat}
                              className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded"
                            >
                              {cat}
                            </span>
                          ))}
                          {record.tags?.slice(0, 2).map((tag: string) => (
                            <span 
                              key={tag}
                              className="px-2 py-0.5 bg-blue-50 text-blue-600 text-xs rounded"
                            >
                              #{tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* AI Badge & Expand Icon */}
                    <div className="flex flex-col items-end gap-2">
                      {/* AI-Assisted Summary Tag */}
                      <span className="inline-flex items-center gap-1 px-2 py-1 bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 rounded text-xs text-purple-700">
                        <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor">
                          <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" strokeWidth="2" fill="none"/>
                        </svg>
                        {dictionary.aiGenerated}
                      </span>

                      {/* Verification Status */}
                      {record.is_verified && (
                        <span className="inline-flex items-center gap-1 text-green-600 text-xs">
                          <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
                          </svg>
                          {dictionary.verified}
                        </span>
                      )}

                      {/* Expand Icon */}
                      <svg 
                        className={`w-5 h-5 text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                        aria-hidden="true"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </div>
                  </div>
                </button>

                {/* Expanded Details */}
                {isExpanded && (
                  <div id={`record-${record.id}`} className="px-6 pb-6">
                    {/* AI Summary Section */}
                    {(record.summary_en || record.summary_kn) && (
                      <div className="mt-4 p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg border border-purple-100">
                        <div className="flex items-center gap-2 mb-3">
                          <svg className="w-5 h-5 text-purple-600" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" strokeWidth="2" fill="none"/>
                          </svg>
                          <h4 className="font-semibold text-purple-900">
                            {dictionary.aiSummaryLabel}
                          </h4>
                        </div>
                        <p className="text-gray-700 leading-relaxed">
                          {lang === 'kn' ? record.summary_kn : record.summary_en}
                        </p>
                        <p className="mt-2 text-xs text-purple-600">
                          {dictionary.aiDisclaimer}
                        </p>
                      </div>
                    )}

                    {/* Full Content */}
                    {(record.content_en || record.content_kn) && (
                      <div className="mt-4">
                        <h4 className="text-sm font-semibold text-gray-700 mb-2">
                          {dictionary.fullContent}
                        </h4>
                        <div className="p-4 bg-white rounded-lg border border-gray-200 max-h-64 overflow-y-auto">
                          <p className="text-gray-600 whitespace-pre-wrap">
                            {lang === 'kn' ? record.content_kn : record.content_en}
                          </p>
                        </div>
                      </div>
                    )}

                    {/* Event Details */}
                    {(record.event_name || record.event_date || record.location) && (
                      <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                        {record.event_name && (
                          <div>
                            <span className="font-medium text-gray-500">{dictionary.event}:</span>
                            <p className="text-gray-900">{record.event_name}</p>
                          </div>
                        )}
                        {record.event_date && (
                          <div>
                            <span className="font-medium text-gray-500">{dictionary.date}:</span>
                            <p className="text-gray-900">{record.event_date}</p>
                          </div>
                        )}
                        {record.location && (
                          <div>
                            <span className="font-medium text-gray-500">{dictionary.location}:</span>
                            <p className="text-gray-900">{record.location}</p>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Source Link with Verification Button */}
                    {record.source_url && (
                      <div className="mt-4 flex flex-wrap items-center gap-4">
                        <a
                          href={record.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 text-sm font-medium"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                          </svg>
                          {dictionary.viewSource}
                        </a>

                        {/* Verification Button */}
                        {record.source_organization && (
                          <button
                            className="inline-flex items-center gap-2 px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg text-sm transition-colors"
                            aria-label={`${dictionary.verifySource}: ${record.source_organization}`}
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                            </svg>
                            {dictionary.verifySource}
                          </button>
                        )}
                      </div>
                    )}

                    {/* Verification Details */}
                    {record.verification_details && (
                      <div className="mt-4 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                        <p className="text-sm text-yellow-800">
                          <span className="font-medium">{dictionary.verificationNote}:</span> {record.verification_details}
                        </p>
                      </div>
                    )}

                    {/* Sentiment Score */}
                    {record.sentiment_score !== null && (
                      <div className="mt-4 flex items-center gap-3">
                        <span className="text-sm text-gray-500">{dictionary.sentiment}:</span>
                        <div className="flex items-center gap-2">
                          <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                            <div 
                              className={`h-full rounded-full ${
                                record.sentiment_score > 0 ? 'bg-green-500' : 
                                record.sentiment_score < 0 ? 'bg-red-500' : 'bg-gray-500'
                              }`}
                              style={{ width: `${Math.abs(record.sentiment_score) * 100}%` }}
                            />
                          </div>
                          <span className={`text-sm font-medium ${
                            record.sentiment_score > 0 ? 'text-green-600' : 
                            record.sentiment_score < 0 ? 'text-red-600' : 'text-gray-600'
                          }`}>
                            {record.sentiment_score > 0 ? '+' : ''}{record.sentiment_score.toFixed(2)}
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </article>
            );
          })
        )}
      </div>

      {/* AI Content Disclaimer */}
      <div className="px-6 py-4 bg-gradient-to-r from-purple-50 to-pink-50 border-t border-purple-100">
        <div className="flex items-start gap-3">
          <svg className="w-5 h-5 text-purple-500 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 2a8 8 0 100 16 8 8 0 000-16zm1 11H9v2a1 1 0 01-2 0V9a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 01-1 1zm0-4H9v2a1 1 0 01-2 0V9a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 01-1 1z" />
            <path d="M10 2a8 8 0 100 16 8 8 0 000-16z" stroke="currentColor" strokeWidth="2" fill="none"/>
          </svg>
          <div className="text-sm text-purple-800">
            <p className="font-medium mb-1">{dictionary.aiContentHeader}</p>
            <p className="text-purple-700">{dictionary.aiContentDisclaimer}</p>
          </div>
        </div>
      </div>
    </section>
  );
}