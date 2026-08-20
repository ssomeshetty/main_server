import React from 'react';

export default function LoadingDirectory() {
  return (
    <div className="container" style={{ padding: '32px 20px 60px' }}>
      {/* Directory Title Header Skeleton */}
      <div style={{ marginBottom: '28px' }}>
        <div className="skeleton skeleton-text" style={{ width: '120px', height: '14px', marginBottom: '16px' }}></div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap', marginBottom: '8px' }}>
          <div className="skeleton skeleton-text" style={{ width: '380px', height: '34px', marginBottom: '0' }}></div>
          <div className="skeleton" style={{ width: '140px', height: '24px', borderRadius: '4px' }}></div>
        </div>
        <div className="skeleton skeleton-text" style={{ width: '260px', height: '18px', marginTop: '8px' }}></div>
      </div>

      {/* Directory Category Pills Skeleton */}
      <div style={{ display: 'flex', gap: '8px', overflowX: 'auto', paddingBottom: '12px', marginBottom: '20px' }}>
        {[...Array(5)].map((_, i) => (
          <div key={i} className="skeleton" style={{ width: i === 0 ? '160px' : '140px', height: '36px', borderRadius: '4px' }}></div>
        ))}
      </div>

      {/* Clean Filter Controls Skeleton */}
      <div className="filter-bar skeleton" style={{ marginBottom: '32px', height: '72px', borderRadius: '8px' }}></div>

      {/* Candidate Grid Skeleton */}
      <div className="grid">
        {[...Array(12)].map((_, i) => (
          <div key={i} className="card" style={{ display: 'flex', flexDirection: 'column' }}>
            <div className="card-header">
              <div className="skeleton skeleton-avatar" style={{ width: '52px', height: '52px', flexShrink: 0 }}></div>
              <div style={{ flex: 1 }}>
                <div className="skeleton skeleton-text" style={{ width: '70%', height: '18px', marginBottom: '6px' }}></div>
                <div className="skeleton skeleton-text" style={{ width: '40%', height: '12px', marginBottom: '0' }}></div>
              </div>
            </div>
            
            <div style={{ marginTop: 'auto', paddingTop: '10px', display: 'flex', gap: '6px' }}>
              <div className="skeleton" style={{ width: '90px', height: '22px', borderRadius: '4px' }}></div>
              <div className="skeleton" style={{ width: '70px', height: '22px', borderRadius: '4px' }}></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
