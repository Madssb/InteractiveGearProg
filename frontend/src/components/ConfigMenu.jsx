import '@/styles/config-menu.css';

function ToggleButton({ id, value, label, icon, onToggle }) {
  return (
    <button
      id={id}
      type="button"
      className={`toggle-btn ${value ? 'active' : ''}`}
      onClick={() => onToggle(!value)}
    >
      {label && <span className="btn-text">{label}</span>}
      {icon && <img className="btn-icon" src={icon} alt="" aria-hidden="true" />}
    </button>
  );
}

export default function ConfigMenu({
  showRetirement,
  setShowRetirement,
  showBareBones,
  setShowBareBones,
  themePreference,
  setThemePreference,
  hide,
  setHide
}) {
  const nextThemePreference = {
    system: 'light',
    light: 'dark',
    dark: 'system',
  }[themePreference] ?? 'system';
  const themeLabel = {
    system: 'System',
    light: 'Light',
    dark: 'Dark',
  }[themePreference] ?? 'System';

  return (
    <div className="config-menu-container">
      <div className="config-menu"> 
        <ToggleButton
          id="retirement-toggle"
          value={showRetirement}
          onToggle={setShowRetirement}
          label="Enable retirement home items"
          icon="/images/misc_icons/Collection_log.png"
        />
        <ToggleButton
          id="bare-bones-toggle"
          value={showBareBones}
          onToggle={setShowBareBones}
          label="Enable bare bones mode"
          icon="/images/misc_icons/Bones.png"
        />
        <ToggleButton
          id="hide-skill"
          value={hide.skill}
          onToggle={v => setHide(prev => ({ ...prev, skill: v }))}
          label="Hide levels"
          icon="/images/misc_icons/Stats_icon.png"
        />
        <ToggleButton
          id="hide-slayer"
          value={hide.slayer}
          onToggle={v => setHide(prev => ({ ...prev, slayer: v }))}
          label="Hide slayer rewards"
          icon="/images/skill_icons/Slayer_icon.webp"
        />
        <ToggleButton
          id="theme-toggle"
          value={themePreference !== 'system'}
          onToggle={() => setThemePreference(nextThemePreference)}
          label={`Theme: ${themeLabel}`}
          icon="/images/misc_icons/Light_orb.png"
        />
      </div>
    </div>
  );
}
