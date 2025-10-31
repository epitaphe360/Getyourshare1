import React from 'react';
import { Helmet } from 'react-helmet-async';

/**
 * SEO Component for managing meta tags
 * Supports Open Graph, Twitter Cards, and Schema.org
 */
const SEO = ({
  title = 'ShareYourSales - Plateforme d\'Affiliation #1 au Maroc',
  description = 'Connectez influenceurs et marchands pour créer des partenariats gagnant-gagnant. Commissions attractives, publication automatique sur réseaux sociaux, paiements garantis.',
  keywords = 'affiliation maroc, influenceurs maroc, marketing affiliation, commissions, instagram maroc, facebook maroc, marketplace maroc, deals maroc, groupon maroc',
  author = 'ShareYourSales',
  image = 'https://shareyoursales.ma/og-image.jpg',
  url = 'https://shareyoursales.ma',
  type = 'website',
  twitterHandle = '@shareyoursales',
  publishedTime,
  modifiedTime,
  section,
  tags = []
}) => {
  const siteTitle = 'ShareYourSales';
  const fullTitle = title === siteTitle ? title : `${title} | ${siteTitle}`;

  return (
    <Helmet>
      {/* Basic Meta Tags */}
      <title>{fullTitle}</title>
      <meta name="description" content={description} />
      <meta name="keywords" content={keywords} />
      <meta name="author" content={author} />

      {/* Open Graph / Facebook */}
      <meta property="og:type" content={type} />
      <meta property="og:url" content={url} />
      <meta property="og:title" content={fullTitle} />
      <meta property="og:description" content={description} />
      <meta property="og:image" content={image} />
      <meta property="og:site_name" content={siteTitle} />
      <meta property="og:locale" content="fr_MA" />

      {/* Article specific */}
      {type === 'article' && publishedTime && (
        <meta property="article:published_time" content={publishedTime} />
      )}
      {type === 'article' && modifiedTime && (
        <meta property="article:modified_time" content={modifiedTime} />
      )}
      {type === 'article' && section && (
        <meta property="article:section" content={section} />
      )}
      {type === 'article' && tags.length > 0 &&
        tags.map((tag, index) => (
          <meta key={index} property="article:tag" content={tag} />
        ))
      }

      {/* Twitter */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:url" content={url} />
      <meta name="twitter:title" content={fullTitle} />
      <meta name="twitter:description" content={description} />
      <meta name="twitter:image" content={image} />
      <meta name="twitter:creator" content={twitterHandle} />
      <meta name="twitter:site" content={twitterHandle} />

      {/* Additional Meta Tags */}
      <meta name="robots" content="index, follow" />
      <meta name="googlebot" content="index, follow" />
      <meta name="language" content="French" />
      <meta name="revisit-after" content="7 days" />

      {/* Mobile */}
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <meta name="theme-color" content="#9333EA" />

      {/* Canonical URL */}
      <link rel="canonical" href={url} />

      {/* Structured Data - Organization */}
      <script type="application/ld+json">
        {JSON.stringify({
          "@context": "https://schema.org",
          "@type": "Organization",
          "name": "ShareYourSales",
          "url": "https://shareyoursales.ma",
          "logo": "https://shareyoursales.ma/logo.png",
          "description": description,
          "sameAs": [
            "https://www.facebook.com/shareyoursales",
            "https://www.instagram.com/shareyoursales",
            "https://www.linkedin.com/company/shareyoursales"
          ],
          "contactPoint": {
            "@type": "ContactPoint",
            "telephone": "+212-522-XXXXXX",
            "contactType": "Customer Service",
            "areaServed": "MA",
            "availableLanguage": ["French", "Arabic"]
          }
        })}
      </script>

      {/* Structured Data - WebSite */}
      <script type="application/ld+json">
        {JSON.stringify({
          "@context": "https://schema.org",
          "@type": "WebSite",
          "url": "https://shareyoursales.ma",
          "name": "ShareYourSales",
          "description": description,
          "potentialAction": {
            "@type": "SearchAction",
            "target": "https://shareyoursales.ma/marketplace?search={search_term_string}",
            "query-input": "required name=search_term_string"
          }
        })}
      </script>
    </Helmet>
  );
};

export default SEO;

/**
 * Usage Examples:
 *
 * // Homepage
 * <SEO />
 *
 * // Product Page
 * <SEO
 *   title="Product Name - Special Deal"
 *   description="Product description..."
 *   image="https://shareyoursales.ma/products/product-image.jpg"
 *   url="https://shareyoursales.ma/marketplace/product/123"
 *   type="product"
 * />
 *
 * // Blog Post
 * <SEO
 *   title="Blog Post Title"
 *   description="Blog post excerpt..."
 *   type="article"
 *   publishedTime="2025-01-01T00:00:00Z"
 *   modifiedTime="2025-01-02T00:00:00Z"
 *   section="Marketing"
 *   tags={['Affiliation', 'Influenceurs', 'Marketing']}
 * />
 */
