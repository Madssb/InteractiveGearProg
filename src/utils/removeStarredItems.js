export default function removeStarredItems(sequence) {
  return sequence.map(group =>
    group.filter(item => !item.startsWith('*'))
  );
}