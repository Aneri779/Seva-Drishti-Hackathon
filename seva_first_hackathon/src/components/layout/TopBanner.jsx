// Shared top government authority banner
export default function TopBanner() {
  return (
    <div className="bg-surface-container-lowest border-b border-outline-variant/30 text-on-surface-variant font-label-code text-label-code py-1.5 px-6">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-2">
        <div className="flex items-center gap-2">
          <span className="inline-block w-2 h-2 rounded-full bg-tertiary animate-pulse"></span>
          <span>ગુજરાત સરકાર | Government of Gujarat • Roads &amp; Buildings (R&amp;B) Department</span>
        </div>
        <div className="flex items-center gap-4 text-outline">
          <span>SAR SATELLITE TELEMETRY NODE: BISAG-N • SAC/ISRO</span>
          <span className="text-primary font-bold">STATE EMERGENCY OPS CENTER (SEOC): ACTIVE</span>
        </div>
      </div>
    </div>
  );
}
