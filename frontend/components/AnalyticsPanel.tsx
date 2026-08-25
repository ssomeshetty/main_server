'use client';

import React from 'react';
import { Shield, Wallet, Target, HelpCircle, Landmark } from 'lucide-react';
import { IntelligenceReport, FinancialDeclaration, CareerTimelineItem } from '../lib/api';

interface Props {
  data: IntelligenceReport;
  financials?: FinancialDeclaration[];
  career?: CareerTimelineItem[];
}

export default function AnalyticsPanel({ data, financials = [], career = [] }: Props) {
  const fin = data.analytics.financial_trajectory;
  const heci = data.analytics.historical_electoral_competitiveness;
  const isi = data.analytics.institutional_seniority;

  return (
    <div className="bg-white rounded-xl shadow-md border border-slate-200 overflow-hidden mb-8">
      <div className="bg-slate-900 text-white p-5 border-b border-slate-800 flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold flex items-center gap-2">
            <Shield className="text-blue-400" size={24} />
            Verified Data Summary
          </h2>
          <p className="text-slate-400 text-sm mt-1">Information shown here comes from verified public records such as election affidavits and Election Commission results.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-slate-200">
        
        {/* Financial Card */}
        <div className="p-6 flex flex-col h-full">
          <div className="flex justify-between items-start mb-6">
            <h3 className="text-slate-800 font-semibold flex items-center gap-2">
              <Wallet className="text-emerald-600" size={20} />
              Declared Assets
            </h3>
          </div>
          
          <div className="mb-6 flex-grow">
            <p className="text-3xl font-bold text-slate-900 leading-none mb-1">
              {fin.state !== 'NO_DATA' ? `₹${(fin.current_net_worth / 10000000).toFixed(1)} Cr` : 'N/A'}
            </p>
            <p className="text-slate-500 text-sm font-medium">Latest Net Worth</p>
            
            {fin.state === 'MULTI_YEAR_DATA' && financials.length > 1 ? (
              <div className="mt-6">
                <div className="flex flex-col gap-0 border-l-2 border-emerald-500 ml-2 pl-4 py-2 relative">
                  {/* Timeline representation */}
                  {[...financials].sort((a, b) => a.declaration_year - b.declaration_year).map((decl, idx) => (
                    <div key={idx} className="relative flex items-center h-8 my-1">
                      <div className="absolute -left-[21px] w-2 h-2 rounded-full bg-white border-2 border-emerald-500"></div>
                      <div className="flex justify-between w-full text-sm">
                        <span className="font-medium text-slate-600">{decl.declaration_year}</span>
                        <span className="font-bold text-slate-800">₹{(decl.net_worth / 10000000).toFixed(1)} Cr</span>
                      </div>
                    </div>
                  ))}
                </div>
                <p className="text-xs text-slate-500 mt-4">{fin.declaration_count} verified declarations</p>
              </div>
            ) : fin.state === 'SINGLE_DECLARATION' ? (
              <div className="mt-6 bg-slate-50 border border-slate-200 rounded-lg p-3">
                <p className="text-sm font-semibold text-slate-700 mb-1">1 verified declaration</p>
                <p className="text-xs text-slate-500">Historical asset comparison is unavailable because only one declaration is recorded.</p>
              </div>
            ) : (
              <p className="text-sm text-slate-500 mt-6">No verified financial affidavits available.</p>
            )}
          </div>
          
          <div className="pt-4 border-t border-slate-100 text-sm mt-auto">
            {fin.state !== 'NO_DATA' && data.provenance.financial_trajectory.latest_source_url && (
              <a href={data.provenance.financial_trajectory.latest_source_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline flex items-center gap-1 font-medium">
                View source →
              </a>
            )}
          </div>
        </div>

        {/* Electoral Card */}
        <div className="p-6 flex flex-col h-full">
          <div className="flex justify-between items-start mb-6">
            <h3 className="text-slate-800 font-semibold flex items-center gap-2">
              <Target className="text-blue-600" size={20} />
              Election Result
            </h3>
          </div>
          
          <div className="mb-6 flex-grow">
            {heci ? (
              <>
                <p className="text-lg font-bold text-slate-900 mb-6">{heci.election_year}</p>
                
                {/* Vote Margin Visualization */}
                <div className="flex flex-col gap-4">
                  {/* Winner Bar */}
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="font-semibold text-slate-800">Winner</span>
                      <span className="font-bold text-emerald-700">{heci.winner_vote_share_pct}%</span>
                    </div>
                    <div className="h-3 w-full bg-slate-100 rounded-full overflow-hidden">
                      <div style={{ width: `${heci.winner_vote_share_pct}%` }} className="bg-emerald-500 h-full rounded-full"></div>
                    </div>
                  </div>
                  
                  {/* Runner-up Bar */}
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="font-semibold text-slate-600">Runner-up</span>
                      <span className="font-bold text-slate-600">{heci.runner_up_vote_share_pct}%</span>
                    </div>
                    <div className="h-3 w-full bg-slate-100 rounded-full overflow-hidden">
                      <div style={{ width: `${heci.runner_up_vote_share_pct}%` }} className="bg-slate-400 h-full rounded-full"></div>
                    </div>
                  </div>
                </div>
                
                <div className="mt-6 pt-4 border-t border-slate-100">
                  <p className="text-emerald-700 font-bold text-lg mb-1">+{heci.margin_pct}% margin</p>
                  <p className="text-slate-600 text-sm">Won by <strong>{heci.margin_votes.toLocaleString()}</strong> votes</p>
                </div>
              </>
            ) : (
              <div className="flex flex-col items-center justify-center h-full text-slate-400 py-10">
                <HelpCircle size={32} className="mb-2 opacity-50" />
                <p className="text-sm">Insufficient Electoral Data</p>
              </div>
            )}
          </div>

          <div className="pt-4 border-t border-slate-100 text-sm mt-auto">
            {heci && data.provenance.historical_electoral_competitiveness.source_url && (
              <a href={data.provenance.historical_electoral_competitiveness.source_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline flex items-center gap-1 font-medium">
                View source →
              </a>
            )}
          </div>
        </div>

        {/* Political Career Card */}
        <div className="p-6 flex flex-col h-full">
          <div className="flex justify-between items-start mb-6">
            <h3 className="text-slate-800 font-semibold flex items-center gap-2">
              <Landmark className="text-purple-600" size={20} />
              Political Career
            </h3>
          </div>
          
          <div className="mb-6 flex-grow">
            <p className="text-xl font-bold text-slate-900 leading-tight mb-1">
              {isi.office_title}
            </p>
            <p className="text-slate-500 text-sm font-medium mb-6">Highest office</p>

            {career.length > 1 ? (
              <div className="mt-2">
                <div className="flex flex-col gap-0 border-l-2 border-purple-400 ml-2 pl-4 py-2 relative">
                  {/* Career timeline */}
                  {[...career].sort((a, b) => parseInt(a.year) - parseInt(b.year)).map((item, idx) => (
                    <div key={idx} className="relative flex items-center min-h-[32px] my-1">
                      <div className="absolute -left-[21px] w-2 h-2 rounded-full bg-white border-2 border-purple-500"></div>
                      <div className="flex gap-3 w-full text-sm">
                        <span className="font-medium text-slate-500 w-10 shrink-0">{item.year}</span>
                        <span className="font-semibold text-slate-800 leading-tight">{item.role_title}</span>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="mt-6">
                  <p className="text-3xl font-bold text-slate-900 leading-none mb-1">{isi.total_terms}</p>
                  <p className="text-sm text-slate-500 font-medium">Total terms served</p>
                </div>
              </div>
            ) : (
              <div className="mt-6">
                <p className="text-3xl font-bold text-slate-900 leading-none mb-1">{isi.total_terms}</p>
                <p className="text-sm text-slate-500 font-medium">Total terms served</p>
              </div>
            )}
          </div>
          
          <div className="pt-4 border-t border-slate-100 text-sm mt-auto">
            <span className="text-blue-600 hover:underline flex items-center gap-1 font-medium cursor-pointer">
              View source →
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
