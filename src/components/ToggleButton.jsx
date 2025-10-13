export default function ToggleButton({ id, value, label, icon, onToggle }) {
  return (
    <button
      id={id}
      className={`toggle-btn ${value ? 'active' : ''}`}
      onClick={() => onToggle(!value)}
    >
      {icon && <img src={icon} alt="" aria-hidden="true" />}
      {!icon && label}
    </button>
  );
}
