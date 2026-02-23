export default function updateSequenceLanceRule(nodesHiddenState, sequenceState) {
  const scytheHidden = nodesHiddenState.has("Scythe of vitur");

  return sequenceState.map(group => {
    const hasLance = group.includes("Dragon hunter lance");
    const isLanceGroup = group.includes("Ferocious gloves");

    if (isLanceGroup) {
      // Add lance if Scythe is hidden, remove if visible
      if (scytheHidden && !hasLance) {
        return [...group, "Dragon hunter lance"];
      }
      if (!scytheHidden && hasLance) {
        return group.filter(item => item !== "Dragon hunter lance");
      }
    }

    return group;
  });
}