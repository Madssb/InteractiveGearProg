export function encodeProgress(milestonesComplete, milestoneSequence) {
    const flat = milestoneSequence.flat();
    if (!flat.length) return '';

    const bytes = new Uint8Array(Math.ceil(flat.length / 8));
    for (let i = 0; i < flat.length; i++) {
        if (milestonesComplete.has(flat[i])) {
            bytes[i >> 3] |= 1 << (7 - (i & 7));
        }
    }

    let binary = '';
    for (const byte of bytes) {
        binary += String.fromCharCode(byte);
    }
    return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

export function decodeProgress(encoded, milestoneSequence) {
    const flat = milestoneSequence.flat();
    if (!encoded || !flat.length) return new Set();

    const padded = encoded.replace(/-/g, '+').replace(/_/g, '/');
    const binary = atob(padded);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
        bytes[i] = binary.charCodeAt(i);
    }

    const completed = new Set();
    for (let i = 0; i < flat.length; i++) {
        if (bytes[i >> 3] & (1 << (7 - (i & 7)))) {
            completed.add(flat[i]);
        }
    }
    return completed;
}
