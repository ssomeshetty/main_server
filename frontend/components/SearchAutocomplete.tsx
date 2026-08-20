'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Locale } from '../lib/dictionary';
import { fetchPoliticians, PoliticianSummary } from '../lib/api';
import PoliticianAvatar from './PoliticianAvatar';

interface SearchAutocompleteProps {
  lang: Locale;
  placeholder?: string;
}

export default function SearchAutocomplete({ lang, placeholder = 'Search politicians, parties...' }: SearchAutocompleteProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<PoliticianSummary[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const containerRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  // Debounced search API call
  useEffect(() => {
    const trimmed = query.trim();
    if (trimmed.length < 2) {
      setResults([]);
      setIsOpen(false);
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    const timer = setTimeout(async () => {
      try {
        const res = await fetchPoliticians({ lang, search: trimmed });
        setResults((res.results || []).slice(0, 7)); // Show top 7 suggestions
        setIsOpen(true);
        setSelectedIndex(-1);
      } catch (err) {
        console.error('Search error:', err);
      } finally {
        setIsLoading(false);
      }
    }, 200);

    return () => clearTimeout(timer);
  }, [query, lang]);

  // Click outside to close dropdown
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Keyboard navigation handler
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!isOpen || results.length === 0) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev < results.length - 1 ? prev + 1 : 0));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev > 0 ? prev - 1 : results.length - 1));
    } else if (e.key === 'Enter') {
      if (selectedIndex >= 0 && selectedIndex < results.length) {
        e.preventDefault();
        const selected = results[selectedIndex];
        router.push(`/${lang}/politicians/${selected.slug}`);
        setIsOpen(false);
        setQuery('');
      }
    } else if (e.key === 'Escape') {
      setIsOpen(false);
    }
  };

  return (
    <div className="search-autocomplete-container" ref={containerRef} style={{ position: 'relative' }}>
      <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => query.trim().length >= 2 && setIsOpen(true)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          style={{
            width: '100%',
            padding: '8px 36px 8px 34px',
            borderRadius: '6px',
            background: '#ffffff',
            border: '1px solid #cbd5e1',
            color: '#0f172a',
            fontSize: '0.85rem',
            outline: 'none',
            transition: 'border-color 0.15s ease',
          }}
          className="search-nav-input"
        />

        {/* Search Lens Icon */}
        <svg
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="none"
          stroke="#64748b"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          style={{ position: 'absolute', left: '12px', pointerEvents: 'none' }}
        >
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>

        {/* Loading Spinner or Clear Button */}
        {isLoading ? (
          <div style={{ position: 'absolute', right: '10px', width: '12px', height: '12px', border: '2px solid #cbd5e1', borderTopColor: '#1d4ed8', borderRadius: '50%', animation: 'spin 0.6s linear infinite' }} />
        ) : query ? (
            <button
              onClick={() => { setQuery(''); setResults([]); setIsOpen(false); }}
              className="search-clear-btn"
              style={{
                position: 'absolute',
                right: '10px',
              }}
            >
              ×
            </button>
        ) : null}
      </div>

      {/* Floating Auto-Complete Suggestions Dropdown */}
      {isOpen && (
        <div
          style={{
            position: 'absolute',
            top: 'calc(100% + 6px)',
            left: 0,
            right: 0,
            background: '#ffffff',
            border: '1px solid #cbd5e1',
            borderRadius: '8px',
            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
            zIndex: 9999,
            overflow: 'hidden',
            maxHeight: '380px',
            overflowY: 'auto',
          }}
        >
          {results.length > 0 ? (
            <div style={{ padding: '6px' }}>
              {results.map((pol, idx) => {
                const isSelected = idx === selectedIndex;
                return (
                  <Link
                    key={pol.id}
                    href={`/${lang}/politicians/${pol.slug}`}
                    onClick={() => { setIsOpen(false); setQuery(''); }}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '10px',
                      padding: '8px 10px',
                      borderRadius: '6px',
                      background: isSelected ? '#f1f5f9' : 'transparent',
                      textDecoration: 'none',
                      color: 'inherit',
                      transition: 'background 0.15s ease',
                    }}
                    onMouseEnter={() => setSelectedIndex(idx)}
                  >
                    <PoliticianAvatar photoUrl={pol.photo_url} name={pol.name} size={34} />

                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontWeight: 700, fontSize: '0.85rem', color: '#0f172a', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {pol.name}
                      </div>
                      <div style={{ fontSize: '0.72rem', color: '#64748b', display: 'flex', gap: '6px', alignItems: 'center' }}>
                        <span style={{ fontWeight: 600, color: '#1d4ed8' }}>{pol.party_name}</span>
                        <span>•</span>
                        <span>{pol.constituency_name || 'Karnataka'}</span>
                      </div>
                    </div>
                  </Link>
                );
              })}
            </div>
          ) : !isLoading ? (
            <div style={{ padding: '16px', textAlign: 'center', fontSize: '0.82rem', color: '#64748b' }}>
              No candidates found matching &quot;{query}&quot;
            </div>
          ) : null}
        </div>
      )}
    </div>
  );
}
