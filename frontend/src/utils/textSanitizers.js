const pat = /\d+ (\w+)/;

export function handleLevels(input) {
  const match = input.match(pat);
  if (match) {
    return match[1];
  }
  return input;
}