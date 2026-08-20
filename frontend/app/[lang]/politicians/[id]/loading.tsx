import React from 'react';

export default function LoadingProfile() {
  return (
    <div>
      {/* Profile Header Skeleton */}
      <div className="profile-header">
        <div className="container">
          <div className="skeleton skeleton-text" style={{ width: '120px', height: '14px', marginBottom: '24px' }}></div>
          
          <div className="profile-info">
            <div className="skeleton skeleton-avatar profile-avatar" style={{ border: 'none' }}></div>
            <div style={{ flex: 1 }}>
              <div className="skeleton skeleton-text" style={{ width: '40%', height: '36px', marginBottom: '12px' }}></div>
              <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
                <div className="skeleton" style={{ width: '100px', height: '24px', borderRadius: '4px' }}></div>
                <div className="skeleton" style={{ width: '120px', height: '24px', borderRadius: '4px' }}></div>
              </div>
            </div>
          </div>
          
          <div className="stat-grid">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="stat-box skeleton" style={{ height: '80px', border: 'none' }}></div>
            ))}
          </div>
        </div>
      </div>

      {/* Profile Content Skeleton */}
      <div className="container profile-content">
        <div className="main-column">
          <div className="glass-panel skeleton" style={{ height: '300px', border: 'none' }}></div>
          <div className="glass-panel skeleton" style={{ height: '250px', border: 'none' }}></div>
        </div>
        
        <div className="sidebar-column">
          <div className="glass-panel skeleton" style={{ height: '180px', border: 'none' }}></div>
          <div className="glass-panel skeleton" style={{ height: '220px', border: 'none' }}></div>
        </div>
      </div>
    </div>
  );
}
