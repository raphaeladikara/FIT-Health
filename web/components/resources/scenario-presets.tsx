import {
  RESOURCE_PRESETS,
  RESOURCE_PRESET_ORDER,
  type ResourcePresetKey,
} from "@/lib/resource-presets";

export function ScenarioPresets({
  active,
  onSelect,
  onReset,
}: {
  active: ResourcePresetKey;
  onSelect: (key: ResourcePresetKey) => void;
  onReset: () => void;
}) {
  return (
    <div className="scenario-presets">
      <div className="chip-row" role="group" aria-label="Capacity presets">
        {RESOURCE_PRESET_ORDER.map((key) => {
          const preset = RESOURCE_PRESETS[key];
          return (
            <button
              key={key}
              type="button"
              className="chip"
              aria-pressed={active === key}
              title={preset.description}
              onClick={() => onSelect(key)}
            >
              {preset.label}
            </button>
          );
        })}
      </div>
      <button type="button" className="chip scenario-reset" onClick={onReset}>
        Reset to {RESOURCE_PRESETS[active].label}
      </button>
    </div>
  );
}
