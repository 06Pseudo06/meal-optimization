/**
 * DashboardCard.jsx — Reusable stat/metric card
 * 
 * Used in Dashboard and Home pages to display nutrition stats.
 * Props:
 *   - icon: Lucide icon component
 *   - label: Small uppercase label (e.g., "DAILY GOAL")
 *   - title: Main stat title (e.g., "Calories")
 *   - value: Large stat value (e.g., "1,842")
 *   - unit: Unit text (e.g., "/ 2,400 kcal")
 *   - accent: Optional accent color class
 *   - children: Optional extra content below the value
 */

export default function DashboardCard({ icon: Icon, label, title, value, unit, accent, children, className = '' }) {
  return (
    <div className={`dashboard-card card ${className}`}>
      {/* Header: icon + label */}
      <div className="dashboard-card__header">
        {Icon && (
          <span className={`dashboard-card__icon ${accent || ''}`}>
            <Icon size={16} />
          </span>
        )}
        {label && <span className="dashboard-card__label label-ui">{label}</span>}
      </div>

      {/* Title */}
      {title && <h3 className="dashboard-card__title">{title}</h3>}

      {/* Value + Unit */}
      <div className="dashboard-card__value-row">
        <span className="dashboard-card__value">{value}</span>
        {unit && <span className="dashboard-card__unit">{unit}</span>}
      </div>

      {/* Optional children (progress bars, charts, etc.) */}
      {children}
    </div>
  );
}
