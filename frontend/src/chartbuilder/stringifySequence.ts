/**
 * Stringify user-submitted milesotne sequence.
 * @param sequence User-submitted milestone sequence to stringify.
 * @param quotes Stringify with quotes if true.
 * @param multiline Stringify with linebreaks if true.
 * @returns Stringified sequence.
 */
export default function getStringifiedSequence(
    sequence: string[][],
    quotes: boolean,
    multiline: boolean,
): string {
    let output: string = "[";
    const groupStrings: string[] = [];
    for (const seqGroup of sequence) {
        const milestoneStrings: string[] = [];
        for (const milestone of seqGroup) {
            milestoneStrings.push(quotes ? JSON.stringify(milestone) : milestone);
        }
        groupStrings.push(`[${milestoneStrings.join(", ")}]`);
    }
    if (multiline) {
        output += "\n\t";
    }
    output += groupStrings.join(multiline ? ",\n\t": ", ");
    if (multiline) {
        output += "\n";
    }
    output += "]";
    return output;
    
}
