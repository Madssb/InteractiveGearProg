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
          icon="https://oldschool.runescape.wiki/images/Collection_log.png"
        />
        <ToggleButton
          id="bare-bones-toggle"
          value={showBareBones}
          onToggle={setShowBareBones}
          label="Enable bare bones mode"
          icon="https://oldschool.runescape.wiki/images/Bones.png"
        />
        <ToggleButton
          id="hide-skill"
          value={hide.skill}
          onToggle={v => setHide(prev => ({ ...prev, skill: v }))}
          label="Hide levels"
          icon="https://oldschool.runescape.wiki/images/Stats_icon.png"
        />
        <ToggleButton
          id="hide-construction"
          value={hide.construction}
          onToggle={v => setHide(prev => ({ ...prev, construction: v }))}
          label="Hide Construction milestones"
          icon="https://oldschool.runescape.wiki/images/Construction_icon.png"
        />
        <ToggleButton
          id="hide-slayer"
          value={hide.slayer}
          onToggle={v => setHide(prev => ({ ...prev, slayer: v }))}
          label="Hide slayer rewards"
          icon="https://oldschool.runescape.wiki/images/Slayer_icon.png"
        />
        <ToggleButton
          id="theme-toggle"
          value={themePreference !== 'system'}
          onToggle={() => setThemePreference(nextThemePreference)}
          label={`Theme: ${themeLabel}`}
          icon="https://oldschool.runescape.wiki/images/Light_orb.png"
        />
      </div>
    </div>
  );
}
