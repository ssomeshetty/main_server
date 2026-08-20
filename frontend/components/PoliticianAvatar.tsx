'use client';

import { useState } from 'react';
import { User } from 'lucide-react';

interface PoliticianAvatarProps {
  photoUrl?: string | null;
  name: string;
  size?: number;
  className?: string;
}

export default function PoliticianAvatar({ photoUrl, name, size = 52, className }: PoliticianAvatarProps) {
  const [hasError, setHasError] = useState(false);

  const cleanUrl = photoUrl && photoUrl.trim() !== '' ? photoUrl.trim() : null;

  if (!cleanUrl || hasError) {
    return (
      <div
        className={className}
        style={{
          width: `${size}px`,
          height: `${size}px`,
          borderRadius: '50%',
          background: '#f1f5f9',
          border: '1px solid #cbd5e1',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#64748b',
          flexShrink: 0,
          userSelect: 'none',
          boxShadow: 'inset 0 1px 2px rgba(0,0,0,0.05)',
        }}
        title={name}
      >
        <User size={Math.round(size * 0.55)} strokeWidth={1.75} />
      </div>
    );
  }

  return (
    <div
      className={className}
      style={{
        width: `${size}px`,
        height: `${size}px`,
        borderRadius: '50%',
        overflow: 'hidden',
        background: '#f1f5f9',
        border: '1px solid #cbd5e1',
        flexShrink: 0,
      }}
    >
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src={cleanUrl}
        alt=""
        onError={() => setHasError(true)}
        style={{ width: '100%', height: '100%', objectFit: 'cover' }}
      />
    </div>
  );
}
