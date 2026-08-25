"""
Political Analytics & Fact-Based Intelligence Engine
=========================================================
Executes strict, explainable analytical dimensions over official government datasets:
1. Financial Asset Trajectory Analysis
2. Historical Electoral Competitiveness Index (HECI)
3. Institutional Seniority Index (ISI)
4. Entity Network Graph Topology
"""

from decimal import Decimal
import math
from typing import Dict, List, Any
from politicians_tracker.apps.core.models import Politician, FinancialDeclaration, ElectionResult, LegalRecord, PublicRecord


class PoliticalAnalyticsEngine:
    def __init__(self, politician: Any):
        if isinstance(politician, str):
            try:
                self.politician = Politician.objects.get(slug=politician)
            except Politician.DoesNotExist:
                self.politician = Politician.objects.get(id=int(politician))
        elif isinstance(politician, int):
            self.politician = Politician.objects.get(id=politician)
        else:
            self.politician = politician

    def analyze_financial_trajectory(self) -> Dict[str, Any]:
        """
        Calculates verified CAGR only if sufficient historical declarations exist.
        Supports 3 strict states: NO_DATA, SINGLE_DECLARATION, MULTI_YEAR_DATA.
        """
        declarations = list(FinancialDeclaration.objects.filter(politician=self.politician).order_by('declaration_year'))

        if not declarations:
            return {
                'state': 'NO_DATA',
                'current_net_worth': float(getattr(self.politician, 'net_worth', 0) or 0),
                'total_assets': None,
                'total_liabilities': None,
                'cagr_pct': None,
                'asset_growth_factor': None,
                'leverage_ratio_pct': None,
                'has_multi_year_history': False,
                'insight_text': 'No verified financial declarations available for analysis.',
                'declaration_count': 0
            }

        # list is ordered by declaration_year (ascending), so [0] is the oldest, [-1] is newest
        latest = declarations[-1]
        latest_assets = float(latest.total_assets or 0)
        latest_liabilities = float(latest.total_liabilities or 0)
        leverage_ratio = (latest_liabilities / latest_assets * 100.0) if latest_assets > 0 else 0.0

        if len(declarations) == 1:
            return {
                'state': 'SINGLE_DECLARATION',
                'current_net_worth': float(latest.net_worth or (latest_assets - latest_liabilities)),
                'total_assets': latest_assets,
                'total_liabilities': latest_liabilities,
                'cagr_pct': None,
                'asset_growth_factor': None,
                'leverage_ratio_pct': round(leverage_ratio, 1),
                'has_multi_year_history': False,
                'insight_text': 'Only a single verified declaration is available. Historical trajectory cannot be calculated.',
                'declaration_count': 1
            }

        earliest = declarations[0]

        cagr = None
        growth_factor = None

        if earliest.declaration_year and latest.declaration_year and latest.declaration_year > earliest.declaration_year:
            earliest_assets = float(earliest.total_assets or 0)
            latest_assets = float(latest.total_assets or 0)
            years_diff = latest.declaration_year - earliest.declaration_year
            if earliest_assets > 0 and latest_assets >= earliest_assets:
                cagr = round((math.pow(latest_assets / earliest_assets, 1.0 / years_diff) - 1.0) * 100.0, 1)
                growth_factor = round(latest_assets / earliest_assets, 1)

        insight = f'Based on {len(declarations)} declarations.'
        if cagr is not None:
            insight = f'Asset trajectory evaluated over {latest.declaration_year - earliest.declaration_year} years.'
        else:
            insight = 'Insufficient verified interval to calculate precise historical trajectory.'

        return {
            'state': 'MULTI_YEAR_DATA',
            'current_net_worth': float(latest.net_worth or (float(latest.total_assets or 0) - latest_liabilities)),
            'total_assets': float(latest.total_assets or 0),
            'total_liabilities': latest_liabilities,
            'cagr_pct': cagr,
            'asset_growth_factor': f'{growth_factor}x' if growth_factor else None,
            'leverage_ratio_pct': round(leverage_ratio, 1) if float(latest.total_assets or 0) > 0 else 0.0,
            'has_multi_year_history': True,
            'insight_text': insight,
            'declaration_count': len(declarations)
        }

    def analyze_electoral_competitiveness(self) -> Dict[str, Any]:
        """
        HECI: Historical Electoral Competitiveness Index
        Describes past margin safety. Descriptive only, not predictive.
        """
        result = ElectionResult.objects.filter(politician=self.politician).first()

        if not result or not result.is_winner or not result.votes_secured or not result.runner_up_votes or result.total_votes_polled <= 0:
            return None

        winner_votes = float(result.votes_secured)
        runner_up_votes = float(result.runner_up_votes)
        total_votes = float(result.total_votes_polled)

        margin_pct = ((winner_votes - runner_up_votes) / total_votes) * 100.0
        margin_penalty = min(100.0, margin_pct * 4.0)
        heci_score = max(0, min(100, round(100.0 - margin_penalty)))

        vote_pct = (winner_votes / total_votes) * 100.0
        runner_pct = (runner_up_votes / total_votes) * 100.0

        if heci_score >= 80:
            category = 'CRITICAL_SWING'
            label = 'Critical Swing / Narrow Victory'
        elif heci_score >= 50:
            category = 'COMPETITIVE'
            label = 'Competitive Seat'
        elif heci_score >= 20:
            category = 'MODERATE_HOLD'
            label = 'Moderate Hold'
        else:
            category = 'STRONGHOLD'
            label = 'Electoral Stronghold'

        return {
            'competitiveness_score': heci_score,
            'margin_pct': round(margin_pct, 1),
            'winner_vote_share_pct': round(vote_pct, 1),
            'runner_up_vote_share_pct': round(runner_pct, 1),
            'margin_votes': result.margin_votes,
            'election_year': getattr(result, 'election_year', 2023), # Fallback to 2023 if missing
            'competitiveness_category': category,
            'category_label': label,
            'insight_text': f'Historical electoral competitiveness based on a {round(margin_pct, 1)}% victory margin.'
        }

    def analyze_institutional_seniority(self) -> Dict[str, Any]:
        """
        ISI: Institutional Seniority Index
        Measures executive/legislative office rank and historical tenure.
        """
        terms_won = self.politician.total_terms_won or (self.politician.terms_as_mla + self.politician.terms_as_mp) or 1

        if self.politician.minister_type == 'cm':
            office_weight = 100
            office_title = 'Chief Minister of Karnataka'
        elif self.politician.minister_type == 'deputy_cm':
            office_weight = 90
            office_title = 'Deputy Chief Minister'
        elif self.politician.is_union_minister:
            office_weight = 85
            office_title = self.politician.union_title_en or 'Union Cabinet Minister'
        elif self.politician.is_minister:
            office_weight = 75
            office_title = self.politician.minister_title_en or 'State Cabinet Minister'
        elif self.politician.representative_type == 'mp_ls':
            office_weight = 65
            office_title = 'Lok Sabha Member of Parliament'
        elif self.politician.representative_type == 'mp_rs':
            office_weight = 60
            office_title = 'Rajya Sabha Member of Parliament'
        else:
            office_weight = 45
            office_title = 'State Legislative Assembly MLA'

        seniority_score = min(100, terms_won * 20)
        isi_score = round(0.60 * office_weight + 0.40 * seniority_score)

        return {
            'seniority_score': isi_score,
            'executive_weight': office_weight,
            'office_title': office_title,
            'total_terms': terms_won,
            'insight_text': 'Index based strictly on highest held office and total legislative terms.'
        }

    def generate_entity_network(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Entity Network Graph Topology
        Generates dynamic network nodes & directed edges for relationships.
        """
        pol = self.politician
        nodes = []
        links = []

        pol_id = f"pol_{pol.id}"
        nodes.append({
            'id': pol_id,
            'label': pol.full_name_en,
            'type': 'POLITICIAN',
            'size': 28,
            'color': '#2563eb',
            'photo_url': pol.photo_url,
            'subtitle': pol.representative_type.upper() if pol.representative_type else 'MLA'
        })

        if pol.current_party:
            party_id = f"party_{pol.current_party.id}"
            nodes.append({
                'id': party_id,
                'label': pol.current_party.party_short_name_en or pol.current_party.party_name_en,
                'type': 'PARTY',
                'size': 20,
                'color': '#16a34a',
                'subtitle': 'Political Party'
            })
            links.append({
                'source': pol_id,
                'target': party_id,
                'relation': 'AFFILIATED_WITH',
                'label': 'Member'
            })

        const_name = pol.parliamentary_constituency_en or (pol.current_constituency.constituency_name_en if pol.current_constituency else None)
        if const_name:
            const_id = "node_constituency"
            nodes.append({
                'id': const_id,
                'label': const_name,
                'type': 'CONSTITUENCY',
                'size': 22,
                'color': '#d97706',
                'subtitle': 'Electoral Area'
            })
            links.append({
                'source': pol_id,
                'target': const_id,
                'relation': 'REPRESENTS',
                'label': 'Elected In'
            })

        fin_id = "node_financial"
        subtitle_str = f"CAGR: {financial_data['cagr_pct']}%" if financial_data.get('cagr_pct') is not None else "Financial Declarations"
        nodes.append({
            'id': fin_id,
            'label': f"₹{round(financial_data['current_net_worth']/10000000, 1)} Cr Assets" if financial_data.get('current_net_worth') else "No Asset Data",
            'type': 'FINANCIAL',
            'size': 18,
            'color': '#059669',
            'subtitle': subtitle_str
        })
        links.append({
            'source': pol_id,
            'target': fin_id,
            'relation': 'FILED_AFFIDAVIT',
            'label': 'Affidavit'
        })

        result = ElectionResult.objects.filter(politician=pol).first()
        if result and result.runner_up_name:
            runner_id = "node_runner_up"
            nodes.append({
                'id': runner_id,
                'label': result.runner_up_name,
                'type': 'COMPETITOR',
                'size': 16,
                'color': '#64748b',
                'subtitle': f"Opponent ({result.runner_up_party})"
            })
            links.append({
                'source': pol_id,
                'target': runner_id,
                'relation': 'DEFEATED_OPPONENT',
                'label': f"+{result.margin_votes:,} Margin" if result.margin_votes else 'Defeated'
            })

        legal_count = LegalRecord.objects.filter(politician=pol).count()
        legal_id = "node_legal"
        nodes.append({
            'id': legal_id,
            'label': f"{legal_count} Pending Cases" if legal_count > 0 else "Clean Record (0 Cases)",
            'type': 'LEGAL',
            'size': 16,
            'color': '#dc2626' if legal_count > 0 else '#059669',
            'subtitle': 'Affidavit Legal Records'
        })
        links.append({
            'source': pol_id,
            'target': legal_id,
            'relation': 'LEGAL_STATUS',
            'label': 'Affidavit Verification'
        })

        return {
            'nodes': nodes,
            'links': links,
            'meta': {
                'total_nodes': len(nodes),
                'total_links': len(links),
                'graph_density': round(len(links) / max(1, len(nodes)), 2)
            }
        }

    def _get_data_confidence(self, decl_count: int, heci_data: Any) -> Dict[str, str]:
        if decl_count == 0:
            fin_conf = 'INSUFFICIENT'
        elif decl_count == 1:
            fin_conf = 'LOW'
        elif decl_count == 2:
            fin_conf = 'MEDIUM'
        else:
            fin_conf = 'HIGH'

        return {
            'financial_history': fin_conf,
            'electoral_history': 'HIGH' if heci_data else 'INSUFFICIENT',
            'institutional_history': 'HIGH'
        }

    def _get_coverage(self) -> Dict[str, Any]:
        from politicians_tracker.apps.core.models import ElectionResult, FinancialDeclaration, LegalRecord, PublicRecord, OfficeTenure, PartyMembership

        has_current_office = OfficeTenure.objects.filter(politician=self.politician, is_current=True).exists()
        has_historical_office = OfficeTenure.objects.filter(politician=self.politician, is_current=False).exists()

        has_current_party = PartyMembership.objects.filter(politician=self.politician, is_current=True).exists()
        has_historical_party = PartyMembership.objects.filter(politician=self.politician, is_current=False).exists()

        return {
            'election_results': ElectionResult.objects.filter(politician=self.politician).exists(),
            'financial_declarations': FinancialDeclaration.objects.filter(politician=self.politician).count(),
            'legal_records': LegalRecord.objects.filter(politician=self.politician).count(),
            'public_records': PublicRecord.objects.filter(politician=self.politician).count(),
            'office_current': has_current_office,
            'office_history': has_historical_office,
            'party_current': has_current_party,
            'party_history': has_historical_party
        }

    def _get_provenance(self) -> Dict[str, Any]:
        """
        Extracts granular data provenance without fabricating timestamps or source URLs.
        """
        from politicians_tracker.apps.core.models import ElectionResult, FinancialDeclaration, LegalRecord, OfficeTenure, PartyMembership

        # Financial Provenance
        fin_decls = FinancialDeclaration.objects.filter(politician=self.politician).order_by('declaration_year')
        fin_prov = {}
        if fin_decls.exists():
            earliest = fin_decls.first()
            latest = fin_decls.last()
            fin_prov = {
                'earliest_declaration_year': earliest.declaration_year,
                'latest_declaration_year': latest.declaration_year,
                'earliest_source_url': earliest.declaration_url,
                'latest_source_url': latest.declaration_url,
                'verification_status': 'VERIFIED' if (earliest.is_verified and latest.is_verified) else 'UNVERIFIED',
                'retrieved_at': None,
                'last_verified': None
            }

        # HECI Provenance
        latest_election = ElectionResult.objects.filter(politician=self.politician).order_by('-election_year').first()
        heci_prov = {}
        if latest_election:
            heci_prov = {
                'based_on_election': latest_election.election_year,
                'source_url': latest_election.source_url,
                'verification_status': 'VERIFIED' if latest_election.is_verified else 'UNVERIFIED'
            }

        # Legal Provenance
        legal_prov = []
        for lr in LegalRecord.objects.filter(politician=self.politician):
            legal_prov.append({
                'case_number': lr.case_number,
                'source_url': lr.source_url,
                'source_organization': lr.source_organization,
                'verification_status': 'VERIFIED' if lr.is_verified else 'UNVERIFIED'
            })

        # Temporal Provenance
        office_prov = []
        for ot in OfficeTenure.objects.filter(politician=self.politician):
            office_prov.append({
                'office_title': ot.office_title,
                'source_url': ot.source_url,
                'verification_status': 'VERIFIED' if ot.is_verified else 'UNVERIFIED'
            })

        party_prov = []
        for pm in PartyMembership.objects.filter(politician=self.politician):
            party_prov.append({
                'party_name': pm.party.party_short_name_en,
                'source_url': pm.source_url,
                'verification_status': 'VERIFIED' if pm.is_verified else 'UNVERIFIED'
            })

        return {
            'financial_trajectory': fin_prov,
            'historical_electoral_competitiveness': heci_prov,
            'legal_records': legal_prov,
            'temporal_history': {
                'office_tenures': office_prov,
                'party_memberships': party_prov
            }
        }

    def analyze_legal_records(self) -> Dict[str, int]:
        """
        Provides a deterministic summary of declared legal cases based on exact stored status.
        Does not infer guilt or conviction.
        """
        records = LegalRecord.objects.filter(politician=self.politician)
        total_cases = records.count()

        # We must carefully map the exact case_status strings in the database.
        # Assuming typical choices: 'pending', 'convicted', 'acquitted', 'quashed', etc.
        pending = 0
        convictions = 0
        acquittals = 0

        for r in records:
            status = (r.case_status or '').lower()
            if 'convict' in status or 'guilt' in status:
                convictions += 1
            elif 'acquit' in status or 'quash' in status or 'dismiss' in status:
                acquittals += 1
            else:
                # FIRs, chargesheets, and open cases default to pending unless explicitly resolved
                pending += 1

        return {
            'total_cases': total_cases,
            'pending_cases': pending,
            'convictions': convictions,
            'acquittals': acquittals
        }

    def get_full_report(self) -> Dict[str, Any]:
        """
        Aggregates verifiable analytical dimensions into a unified payload.
        """
        financial = self.analyze_financial_trajectory()
        heci = self.analyze_electoral_competitiveness()
        isi = self.analyze_institutional_seniority()
        legal = self.analyze_legal_records()
        graph = self.generate_entity_network(financial)

        return {
            'politician_id': self.politician.id,
            'slug': self.politician.slug,
            'name': self.politician.full_name_en,
            'analytics': {
                'financial_trajectory': financial,
                'historical_electoral_competitiveness': heci,
                'institutional_seniority': isi,
            },
            'legal_summary': legal,
            'entity_network': graph,
            'data_confidence': self._get_data_confidence(financial['declaration_count'], heci),
            'coverage': self._get_coverage(),
            'provenance': self._get_provenance()
        }
