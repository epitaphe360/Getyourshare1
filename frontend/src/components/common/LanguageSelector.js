/**
 * Sélecteur de Langue
 * Permet à l'utilisateur de changer la langue de l'interface
 */

import React, { useState } from 'react';
import { useI18n } from '../../i18n/i18n';

const LanguageSelector = ({ className = '' }) => {
  const { language, changeLanguage, languages, languageNames, languageFlags } = useI18n();
  const [isOpen, setIsOpen] = useState(false);

  const handleLanguageChange = (newLang) => {
    changeLanguage(newLang);
    setIsOpen(false);
  };

  return (
    <div className={`relative ${className}`}>
      {/* Bouton déclencheur */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500"
      >
        <span className="text-2xl">{languageFlags[language]}</span>
        <span className="font-medium text-gray-700">
          {languageNames[language]}
        </span>
        <svg
          className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </button>

      {/* Dropdown menu */}
      {isOpen && (
        <>
          {/* Overlay pour fermer en cliquant dehors */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />

          {/* Menu */}
          <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 z-20">
            <div className="py-1">
              {Object.values(languages).map((lang) => (
                <button
                  key={lang}
                  onClick={() => handleLanguageChange(lang)}
                  className={`
                    w-full flex items-center gap-3 px-4 py-3
                    hover:bg-gray-100 transition-colors
                    ${language === lang ? 'bg-indigo-50 text-indigo-600' : 'text-gray-700'}
                  `}
                >
                  <span className="text-2xl">{languageFlags[lang]}</span>
                  <span className="flex-1 text-left font-medium">
                    {languageNames[lang]}
                  </span>
                  {language === lang && (
                    <svg
                      className="w-5 h-5 text-indigo-600"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                  )}
                </button>
              ))}
            </div>

            {/* Description */}
            <div className="border-t border-gray-200 px-4 py-3 bg-gray-50">
              <p className="text-xs text-gray-500 text-center">
                {language === languages.FR && 'Interface adaptée à votre langue'}
                {language === languages.AR && 'واجهة مكيفة مع لغتك'}
                {language === languages.DARIJA && 'الواجهة متكيفة مع لغتك'}
                {language === languages.EN && 'Interface adapted to your language'}
              </p>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default LanguageSelector;
