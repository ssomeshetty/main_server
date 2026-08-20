// API Fetching Utilities for Politician Tracker
// Handles locale-aware data fetching with proper caching

import { Locale } from './dictionary';

// Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// Cache configuration
const CACHE_TTL = 60 * 60; // 1 hour (matching ISR revalidate time)

// =============================================================================
// API CLIENT WITH LOCALIZATION SUPPORT
// =============================================================================

interface ApiOptions {
  lang: Locale;
  signal?: AbortSignal;
  tags?: string[];
}

class ApiClient {
  private baseUrl: string;
  private defaultHeaders: Record<string, string>;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
    this.defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
  }

  private getHeaders(lang: Locale): Record<string, string> {
    return {
      ...this.defaultHeaders,
      'Accept-Language': lang,
      'Accept': 'application/json',
    };
  }

  async get<T>(
    endpoint: string,
    { lang = 'en', signal, tags }: ApiOptions = { lang: 'en' }
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    // Add language as query param (fallback to header)
    const separator = url.includes('?') ? '&' : '?';
    const urlWithLang = `${url}${separator}lang=${lang}`;
    
    const response = await fetch(urlWithLang, {
      method: 'GET',
      headers: this.getHeaders(lang),
      signal,
      next: {
        revalidate: CACHE_TTL,
        tags: tags || ['api'],
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }
}

export const apiClient = new ApiClient(API_BASE_URL);

// =============================================================================
// POLITICIAN API FUNCTIONS
// =============================================================================

/**
 * Fetch politician by ID with all related data
 * Cached for ISR revalidation period
 */
export async function fetchPoliticianById(
  id: string,
  lang: Locale
): Promise<PoliticianDetail | null> {
  try {
    const data = await apiClient.get<PoliticianDetail>(
      `/politicians/${id}/`,
      { lang }
    );
    return data;
  } catch (error) {
    console.error(`Error fetching politician ${id}:`, error);
    return null;
  }
}

/**
 * Fetch popular politicians for static params generation
 */
export async function fetchPopularPoliticians(limit: number = 100): Promise<PoliticianSummary[]> {
  try {
    const data = await apiClient.get<{ results: PoliticianSummary[]; next: string | null }>(
      `/politicians/`,
      { lang: 'en' }
    );
    return (data.results || []).slice(0, limit);
  } catch (error) {
    console.error('Error fetching popular politicians:', error);
    return [];
  }
}

/**
 * Fetch all politician slugs/IDs for dynamic sitemap generation and SSG
 */
export async function fetchAllPoliticianSlugs(): Promise<{ slug: string; id: number }[]> {
  try {
    const slugs: { slug: string; id: number }[] = [];
    let url = `${API_BASE_URL}/politicians/?page_size=100`;
    while (url) {
      const res = await fetch(url, { next: { revalidate: 3600 } });
      if (!res.ok) break;
      const data = await res.json();
      for (const p of data.results || []) {
        slugs.push({ slug: p.slug || String(p.id), id: p.id });
      }
      url = data.next || '';
    }
    return slugs;
  } catch (error) {
    console.error('Error fetching all politician slugs:', error);
    return [];
  }
}

/**
 * Fetch politicians with filtering
 */
export async function fetchPoliticians(
  params: {
    lang: Locale;
    district?: number;
    party?: number;
    search?: string;
    is_minister?: boolean;
    is_union_minister?: boolean;
    representative_type?: string;
    page?: number;
  }
): Promise<{ results: PoliticianSummary[]; count: number }> {
  try {
    const queryParams = new URLSearchParams();
    if (params.district) queryParams.set('district', params.district.toString());
    if (params.party) queryParams.set('party', params.party.toString());
    if (params.search) queryParams.set('search', params.search);
    if (params.is_minister !== undefined) queryParams.set('is_minister', params.is_minister.toString());
    if (params.is_union_minister !== undefined) queryParams.set('is_union_minister', params.is_union_minister.toString());
    if (params.representative_type) queryParams.set('representative_type', params.representative_type);
    if (params.page) queryParams.set('page', params.page.toString());

    const qs = queryParams.toString();
    const endpoint = `/politicians/${qs ? `?${qs}` : ''}`;
    const data = await apiClient.get<{ results: PoliticianSummary[]; count?: number }>(endpoint, { lang: params.lang });
    return { results: data.results || [], count: data.count || 0 };
  } catch (error) {
    console.error('Error fetching politicians:', error);
    return { results: [], count: 0 };
  }
}

/**
 * Fetch financial declarations for a politician
 */
export async function fetchFinancialDeclarations(
  politicianId: string,
  lang: Locale
): Promise<FinancialDeclaration[]> {
  try {
    return apiClient.get<FinancialDeclaration[]>(
      `/financial-declarations/?politician=${politicianId}`,
      { lang }
    );
  } catch (error) {
    console.error('Error fetching financial declarations:', error);
    return [];
  }
}

/**
 * Fetch legal records for a politician
 */
export async function fetchLegalRecords(
  politicianId: string,
  lang: Locale
): Promise<LegalRecord[]> {
  try {
    return apiClient.get<LegalRecord[]>(
      `/legal-records/?politician=${politicianId}`,
      { lang }
    );
  } catch (error) {
    console.error('Error fetching legal records:', error);
    return [];
  }
}

/**
 * Fetch public records (speeches, allegations) for a politician
 */
export async function fetchPublicRecords(
  politicianId: string,
  lang: Locale,
  limit: number = 20
): Promise<PublicRecord[]> {
  try {
    return apiClient.get<PublicRecord[]>(
      `/public-records/?politician=${politicianId}&limit=${limit}`,
      { lang }
    );
  } catch (error) {
    console.error('Error fetching public records:', error);
    return [];
  }
}

// =============================================================================
// DISTRICTS, CONSTITUENCIES & PARTIES
// =============================================================================

export async function fetchDistricts(lang: Locale): Promise<District[]> {
  try {
    const data = await apiClient.get<{ results?: District[] } | District[]>('/districts/', { lang });
    return Array.isArray(data) ? data : data.results || [];
  } catch (error) {
    console.error('Error fetching districts:', error);
    return [];
  }
}

export async function fetchParties(lang: Locale): Promise<PartySummary[]> {
  try {
    const data = await apiClient.get<{ results?: PartySummary[] } | PartySummary[]>('/parties/', { lang });
    return Array.isArray(data) ? data : data.results || [];
  } catch (error) {
    console.error('Error fetching parties:', error);
    return [];
  }
}

export async function fetchConstituencies(
  params: { lang: Locale; district?: number }
): Promise<Constituency[]> {
  try {
    const queryParams = params.district ? `?district=${params.district}` : '';
    const data = await apiClient.get<{ results?: Constituency[] } | Constituency[]>(`/constituencies/${queryParams}`, { lang: params.lang });
    return Array.isArray(data) ? data : data.results || [];
  } catch (error) {
    console.error('Error fetching constituencies:', error);
    return [];
  }
}

// =============================================================================
// TYPE DEFINITIONS
// =============================================================================

export interface PoliticianSummary {
  id: number;
  name: string;
  slug: string;
  photo_url: string | null;
  party_name: string | null;
  constituency_name: string | null;
  parliamentary_constituency?: string | null;
  total_terms_won: number;
  is_active: boolean;
  is_verified: boolean;
  representative_type?: 'mla' | 'mp_ls' | 'mp_rs';
  is_minister?: boolean;
  minister_type?: 'cm' | 'deputy_cm' | 'cabinet_minister' | 'minister_of_state' | null;
  minister_title?: string | null;
  portfolio?: string | null;
  is_union_minister?: boolean;
  union_title?: string | null;
  union_portfolio?: string | null;
}

export interface CareerTimelineItem {
  year: string;
  role_title: string;
  portfolio?: string;
  role_type: 'mla' | 'mp_ls' | 'mp_rs' | 'minister' | 'union_minister';
  constituency?: string;
  party?: string;
  is_current: boolean;
  badge: string;
}

export interface ElectoralPerformance {
  election_year: number;
  election_type: 'assembly' | 'lok_sabha';
  constituency_name: string;
  party_name: string;
  total_electors: number;
  total_votes_polled: number;
  votes_secured: number;
  vote_percentage: number;
  margin_votes: number;
  evm_votes: number;
  postal_votes: number;
  runner_up_name: string;
  runner_up_party: string;
  runner_up_votes: number;
  runner_up_vote_pct: number;
}

export interface AreaDemographics {
  constituency_name: string;
  constituency_type: 'general' | 'sc' | 'st';
  district_name: string;
  population: number;
  literacy_rate: number;
  sex_ratio: number;
  religion_composition: {
    hindu_pct: number;
    muslim_pct: number;
    christian_pct: number;
    jain_pct: number;
    buddhist_pct: number;
    sikh_pct: number;
  };
  category_composition: {
    sc_pct: number;
    st_pct: number;
    general_pct: number;
  };
}

export interface PoliticianDetail extends PoliticianSummary {
  full_name_en: string;
  full_name_kn: string;
  date_of_birth: string | null;
  age: number | null;
  gender: string | null;
  email: string | null;
  phone: string | null;
  party: PartySummary | null;
  party_name: string | null;
  constituency: ConstituencySummary | null;
  district_name: string | null;
  total_terms_contested: number;
  terms_as_mla: number;
  terms_as_mlna: number;
  terms_as_mp: number;
  terms_as_minister: number;
  biography: string;
  social_media: SocialMedia;
  ec_candidate_id: string | null;
  is_verified: boolean;
  latest_financial_year: number | null;
  net_worth: number | null;
  latest_declaration: FinancialDeclaration | null;
  financial_declarations?: FinancialDeclaration[];
  legal_records?: LegalRecord[];
  public_records?: PublicRecord[];
  career_timeline?: CareerTimelineItem[];
  electoral_performance?: ElectoralPerformance | null;
  area_demographics?: AreaDemographics | null;
}

export interface PartySummary {
  id: number;
  name: string;
  short_name: string;
  party_symbol_url: string | null;
  party_type: string;
}

export interface ConstituencySummary {
  id: number;
  name: string;
  number: number;
  type: string;
  district_id: number;
}

export interface SocialMedia {
  facebook: string | null;
  twitter: string | null;
  instagram: string | null;
  youtube: string | null;
  linkedin: string | null;
  website: string | null;
}

export interface FinancialDeclaration {
  id: number;
  politician: number;
  politician_name: string;
  party_name: string;
  declaration_year: number;
  declaration_type: string;
  declaration_date: string | null;
  declaration_url: string | null;
  total_assets: number;
  total_liabilities: number;
  net_worth: number;
  residential_property_value: number;
  commercial_property_value: number;
  agricultural_land_value: number;
  bank_deposits: number;
  shares_and_securities: number;
  vehicles_value: number;
  jewelry_value: number;
  is_verified: boolean;
}

export interface LegalRecord {
  id: number;
  politician: number;
  politician_name: string;
  case_number: string;
  police_station: string;
  district: string;
  fir_date: string | null;
  case_status: string;
  case_status_display: string;
  ipc_sections: string[];
  other_sections: string[];
  description_en: string;
  description_kn: string;
  court_name: string;
  case_type: string;
  case_url: string | null;
  next_hearing_date: string | null;
  is_verified: boolean;
}

export interface PublicRecord {
  id: number;
  politician: number;
  politician_name: string;
  record_type: string;
  record_type_display: string;
  title_en: string;
  title_kn: string;
  content_en: string;
  content_kn: string;
  summary_en: string;
  summary_kn: string;
  categories: string[];
  tags: string[];
  event_name: string;
  event_date: string | null;
  location: string;
  verification_status: string;
  verification_status_display: string;
  verified_by: string | null;
  verification_date: string | null;
  sentiment_score: number | null;
  word_count: number;
  language: string;
  source_url: string;
  source_organization: string | null;
  is_verified: boolean;
}

export interface District {
  id: number;
  name: string;
  district_code: string;
  region: string;
  population_2011: number | null;
}

export interface Constituency {
  id: number;
  name: string;
  constituency_number: number;
  district: number;
  district_name: string;
  constituency_type: string;
  population_2011: number | null;
}

export interface LeaderboardItem {
  rank: number;
  id: number;
  slug: string;
  name: string;
  photo_url: string;
  party: string;
  constituency: string;
  total_assets_cr: number;
  total_liabilities_cr: number;
}

export interface PartyDistributionItem {
  party_code: string;
  party_name: string;
  seats: number;
  percentage: number;
  color: string;
}

export interface DemographicItem {
  bracket?: string;
  level?: string;
  count: number;
  percentage: number;
}

export interface AnalyticsData {
  summary: {
    total_mlas: number;
    total_assembly_assets_cr: number;
    total_assembly_liabilities_cr: number;
    average_age: number;
    total_legal_cases: number;
  };
  top_richest: LeaderboardItem[];
  top_indebted: LeaderboardItem[];
  party_distribution: PartyDistributionItem[];
  age_demographics: DemographicItem[];
  education_demographics: DemographicItem[];
}

export async function fetchAnalyticsData(lang: Locale = 'en'): Promise<AnalyticsData | null> {
  try {
    return await apiClient.get<AnalyticsData>('/analytics/', { lang });
  } catch (error) {
    console.error('Error fetching analytics data:', error);
    return null;
  }
}

export interface GraphNode {
  id: string;
  label: string;
  type: 'POLITICIAN' | 'PARTY' | 'CONSTITUENCY' | 'FINANCIAL' | 'COMPETITOR' | 'LEGAL';
  size: number;
  color: string;
  photo_url?: string | null;
  subtitle?: string;
}

export interface GraphLink {
  source: string;
  target: string;
  relation: string;
  label: string;
}

export interface KnowledgeGraphData {
  nodes: GraphNode[];
  links: GraphLink[];
  meta: {
    total_nodes: number;
    total_links: number;
    graph_density: number;
  };
}

export interface IntelligenceReport {
  politician_id: number;
  slug: string;
  name: string;
  overall_intelligence_score: number;
  financial_analysis: {
    has_data: boolean;
    current_net_worth: number;
    total_assets?: number;
    total_liabilities?: number;
    cagr_pct: number;
    asset_growth_factor: string;
    leverage_ratio_pct: number;
    anomaly_rating: 'LOW' | 'MODERATE' | 'ELEVATED' | 'HIGH';
    anomaly_confidence: string;
    risk_badge_color: string;
    insight_text: string;
  };
  electoral_vulnerability: {
    vulnerability_score: number;
    margin_pct: number;
    votes_secured?: number;
    margin_votes?: number;
    swing_category: 'SECURE_HOLD' | 'COMPETITIVE_SEAT' | 'HIGH_VULNERABILITY' | 'CRITICAL_SWING_SEAT';
    category_label: string;
    badge_color: string;
    evm_dominance_pct: number;
    competitor_pressure_ratio: number;
    insight_text: string;
  };
  legislative_influence: {
    influence_score: number;
    seniority_score: number;
    office_weight: number;
    office_title: string;
    governance_tier: string;
    tier_label: string;
    badge_color: string;
    total_terms: number;
  };
  knowledge_graph: KnowledgeGraphData;
}

export async function fetchPoliticianIntelligence(slug: string, lang: Locale = 'en'): Promise<IntelligenceReport | null> {
  try {
    return await apiClient.get<IntelligenceReport>(`/intelligence/politician/${slug}/`, { lang });
  } catch (error) {
    console.error('Error fetching politician intelligence:', error);
    return null;
  }
}