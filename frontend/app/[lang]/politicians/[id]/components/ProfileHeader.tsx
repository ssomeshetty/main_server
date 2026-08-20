'use client';

import { useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { Locale } from '@/lib/dictionary';

interface ProfileHeaderProps {
  politician: any;
  lang: Locale;
  dictionary: any;
}

export default function ProfileHeader({ politician, lang, dictionary }: ProfileHeaderProps) {
  const [imageError, setImageError] = useState(false);

  const name = politician.name || politician.full_name_en || 'Unknown';
  const photoUrl = politician.photo_url;
  const party = politician.party;
  const constituency = politician.constituency;
  const districtName = politician.district_name;
  const socialMedia = politician.social_media || {};

  const hasSocialLinks = Object.values(socialMedia).some(Boolean);

  return (
    <header className="bg-white shadow-sm">
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="flex flex-col md:flex-row gap-8">
          {/* Profile Photo */}
          <div className="flex-shrink-0">
            <div className="relative w-48 h-48 md:w-64 md:h-64 rounded-lg overflow-hidden bg-gray-100">
              {!imageError && photoUrl ? (
                <Image
                  src={photoUrl}
                  alt={name}
                  fill
                  className="object-cover"
                  sizes="(max-width: 768px) 192px, 256px"
                  onError={() => setImageError(true)}
                  priority
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center bg-blue-50 text-blue-300">
                  <svg 
                    className="w-24 h-24" 
                    fill="currentColor" 
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                  >
                    <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                  </svg>
                </div>
              )}
            </div>
          </div>

          {/* Profile Info */}
          <div className="flex-grow">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                {/* Name */}
                <h1 className="text-3xl md:text-4xl font-bold text-gray-900">
                  {name}
                </h1>

                {/* Party & Constituency */}
                <div className="mt-2 flex flex-wrap items-center gap-3 text-lg text-gray-600">
                  {party && (
                    <span className="inline-flex items-center gap-2">
                      <span className="w-6 h-6 bg-gray-200 rounded-full flex items-center justify-center text-xs">
                        {party.short_name?.[0] || party.name?.[0]}
                      </span>
                      {lang === 'kn' ? party.name_kn : party.name}
                    </span>
                  )}
                  {constituency && (
                    <span className="text-gray-400">
                      <svg className="inline w-4 h-4 mx-1" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd"/>
                      </svg>
                      {lang === 'kn' ? constituency.name_kn : constituency.name}
                      {constituency.number && ` (#${constituency.number})`}
                    </span>
                  )}
                </div>

                {/* District */}
                {districtName && (
                  <p className="mt-1 text-gray-500">
                    {dictionary.districtLabel}: {districtName}
                  </p>
                )}
              </div>

              {/* Verification Badge */}
              {politician.is_verified && (
                <div className="flex items-center gap-1 text-green-600 bg-green-50 px-3 py-1 rounded-full">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                    <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
                  </svg>
                  <span className="text-sm font-medium">{dictionary.verified}</span>
                </div>
              )}
            </div>

            {/* Biography */}
            {politician.biography_en && (
              <p className="mt-4 text-gray-700 line-clamp-3">
                {lang === 'kn' ? politician.biography_kn : politician.biography_en}
              </p>
            )}

            {/* Contact Info */}
            {(politician.email || politician.phone) && (
              <div className="mt-4 flex flex-wrap gap-4 text-sm text-gray-600">
                {politician.email && (
                  <a 
                    href={`mailto:${politician.email}`}
                    className="flex items-center gap-2 hover:text-blue-600 transition-colors"
                    aria-label={`Email: ${politician.email}`}
                  >
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                      <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z"/>
                      <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z"/>
                    </svg>
                    {politician.email}
                  </a>
                )}
                {politician.phone && (
                  <a 
                    href={`tel:${politician.phone}`}
                    className="flex items-center gap-2 hover:text-blue-600 transition-colors"
                    aria-label={`Phone: ${politician.phone}`}
                  >
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                      <path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z"/>
                    </svg>
                    {politician.phone}
                  </a>
                )}
              </div>
            )}

            {/* Social Media Links */}
            {hasSocialLinks && (
              <div className="mt-4 flex flex-wrap gap-3" role="list" aria-label="Social media links">
                {socialMedia.facebook && (
                  <a
                    href={socialMedia.facebook}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-2 bg-gray-100 rounded-full hover:bg-blue-100 text-gray-600 hover:text-blue-600 transition-colors"
                    aria-label="Facebook"
                  >
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                      <path fillRule="evenodd" d="M22 12c0-5.523-4.477-10-10-10S2 6.477 2 12c0 4.991 3.657 9.128 8.438 9.878v-6.987h-2.54V12h2.54V9.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V12h2.773l-.443 2.89h-2.33v6.988C18.343 21.128 22 16.991 22 12z" clipRule="evenodd"/>
                    </svg>
                  </a>
                )}
                {socialMedia.twitter && (
                  <a
                    href={socialMedia.twitter}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-2 bg-gray-100 rounded-full hover:bg-gray-200 transition-colors"
                    aria-label="Twitter"
                  >
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                      <path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84"/>
                    </svg>
                  </a>
                )}
                {socialMedia.instagram && (
                  <a
                    href={socialMedia.instagram}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-2 bg-gray-100 rounded-full hover:bg-pink-100 text-gray-600 hover:text-pink-600 transition-colors"
                    aria-label="Instagram"
                  >
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                      <path fillRule="evenodd" d="M12.315 2c2.43 0 2.784.013 3.808.06 1.064.049 1.791.218 2.427.465a4.902 4.902 0 011.772 1.153 4.902 4.902 0 011.153 1.772c.247.636.416 1.363.465 2.427.048 1.067.06 1.407.06 4.123v.08c0 2.643-.012 2.987-.06 4.043-.049 1.064-.218 1.791-.465 2.427a4.902 4.902 0 01-1.153 1.772 4.902 4.902 0 01-1.772 1.153c-.636.247-1.363.416-2.427.465-1.067.048-1.407.06-4.123.06h-.08c-2.643 0-2.987-.012-4.043-.06-1.064-.049-1.791-.218-2.427-.465a4.902 4.902 0 01-1.772-1.153 4.902 4.902 0 01-1.153-1.772c-.247-.636-.416-1.363-.465-2.427-.047-1.024-.06-1.379-.06-3.808v-.63c0-2.43.013-2.784.06-3.808.049-1.064.218-1.791.465-2.427a4.902 4.902 0 011.153-1.772A4.902 4.902 0 015.45 2.525c.636-.247 1.363-.416 2.427-.465C8.901 2.013 9.256 2 11.685 2h.63zm-.081 1.802h-.468c-2.456 0-2.784.011-3.807.058-.975.045-1.504.207-1.857.344-.467.182-.8.398-1.15.748-.35.35-.566.683-.748 1.15-.137.353-.3.882-.344 1.857-.047 1.023-.058 1.351-.058 3.807v.468c0 2.456.011 2.784.058 3.807.045.975.207 1.504.344 1.857.182.466.399.8.748 1.15.35.35.683.566 1.15.748.353.137.882.3 1.857.344 1.054.048 1.37.058 4.041.058h.08c2.597 0 2.917-.01 3.96-.058.976-.045 1.505-.207 1.858-.344.466-.182.8-.398 1.15-.748.35-.35.566-.683.748-1.15.137-.353.3-.882.344-1.857.048-1.055.058-1.37.058-4.041v-.08c0-2.597-.01-2.917-.058-3.96-.045-.976-.207-1.505-.344-1.858a3.097 3.097 0 00-.748-1.15 3.098 3.098 0 00-1.15-.748c-.353-.137-.882-.3-1.857-.344-1.023-.047-1.351-.058-3.807-.058zM12 6.865a5.135 5.135 0 110 10.27 5.135 5.135 0 010-10.27zm0 1.802a3.333 3.333 0 100 6.666 3.333 3.333 0 000-6.666zm5.338-3.205a1.2 1.2 0 110 2.4 1.2 1.2 0 010-2.4z" clipRule="evenodd"/>
                    </svg>
                  </a>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Terms Served Summary */}
        {politician.terms_as_mla > 0 || politician.terms_as_mp > 0 && (
          <div className="mt-6 pt-6 border-t border-gray-100">
            <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
              {dictionary.termsServed}
            </h2>
            <div className="flex flex-wrap gap-4">
              {politician.terms_as_mla > 0 && (
                <div className="bg-blue-50 px-4 py-2 rounded-lg">
                  <span className="block text-2xl font-bold text-blue-600">
                    {politician.terms_as_mla}
                  </span>
                  <span className="text-sm text-blue-800">
                    {politician.terms_as_mla === 1 ? dictionary.terms.asMLA : dictionary.terms.asMLAs}
                  </span>
                </div>
              )}
              {politician.terms_as_mlna > 0 && (
                <div className="bg-purple-50 px-4 py-2 rounded-lg">
                  <span className="block text-2xl font-bold text-purple-600">
                    {politician.terms_as_mlna}
                  </span>
                  <span className="text-sm text-purple-800">
                    {politician.terms_as_mlna === 1 ? dictionary.terms.asMLNA : dictionary.terms.asMLNAs}
                  </span>
                </div>
              )}
              {politician.terms_as_mp > 0 && (
                <div className="bg-green-50 px-4 py-2 rounded-lg">
                  <span className="block text-2xl font-bold text-green-600">
                    {politician.terms_as_mp}
                  </span>
                  <span className="text-sm text-green-800">
                    {politician.terms_as_mp === 1 ? dictionary.terms.asMP : dictionary.terms.asMPs}
                  </span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </header>
  );
}