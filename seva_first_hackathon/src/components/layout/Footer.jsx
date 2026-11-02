const FOOTER_LINKS = [
  { label: 'Gujarat State Portal',                  href: '#portal' },
  { label: 'National Disaster Management Authority', href: '#ndma' },
  { label: 'Sentinel-1 SAR Data',                    href: 'https://sentinel.esa.int/web/sentinel/missions/sentinel-1' },
  { label: 'Geotechnical Open Data',                href: '#geotechnical' },
  { label: 'Emergency Contact Protocols',           href: '#protocols' },
  { label: 'Terms of Telemetry Service',            href: '#terms' },
  { label: 'Accessibility Statement',               href: '#accessibility' },
];

export default function Footer() {
  return (
    <footer className="bg-surface-container-lowest border-t border-outline-variant/30">
      <div className="w-full px-6 py-12 max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">

        {/* Brand */}
        <div className="space-y-2 text-center md:text-left">
          <div className="text-headline-sm font-headline-sm font-bold text-on-surface flex items-center justify-center md:justify-start gap-2">
            <span className="material-symbols-outlined text-primary">radar</span>
            <span>SAR-Drishti | R&amp;B Dept, Govt of Gujarat</span>
          </div>
          <p className="text-body-sm font-body-sm text-on-surface-variant max-w-2xl">
            © 2025 Roads &amp; Buildings Department, Government of Gujarat. Satellite SAR Telemetry powered by
            Bhaskaracharya National Institute for Space Applications and Geo-informatics (BISAG-N) &amp; ISRO.
          </p>
        </div>

        {/* Links */}
        <div className="flex flex-wrap justify-center md:justify-end gap-x-6 gap-y-2 text-label-meta font-label-meta">
          {FOOTER_LINKS.map(({ label, href }) => (
            <a
              key={href}
              href={href}
              className="text-on-surface-variant hover:text-primary transition-colors duration-150"
            >
              {label}
            </a>
          ))}
        </div>

      </div>
    </footer>
  );
}
