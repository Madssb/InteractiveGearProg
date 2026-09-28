/**
 * Chartbuilder request wrappers live here.
 */
import { fetchMetadata, ChartbuilderMetadata, MetadataRecord, ChartbuilderMetadataResponse, postShare } from '@/chartbuilder/chartBuilderRequests';
import { apiUrl } from '@/utils/apiConfig';
import { encodeProgress } from '@/utils/progressEncoding';

/**
 * Fetch missing metadata records, i.e. present in seq, but not in existing metadata.
 * @param milestoneSequence User-submitted chartbuilder milestone sequence.
 * @param metadata Existing chartbuilder metadata.
 * @param unresolvedMilestones Milestones known to not have metadata records.
 * @returns Retrieved metadata records and set of unresolved milestones if exists, or undefined.
 */
export async function fetchMissingMetadata(
    milestoneSequence: string[][],
    metadata: ChartbuilderMetadata,
    unresolvedMilestones: Set<string>,
): Promise<ChartbuilderMetadataResponse | undefined> {
    // Infer what milestone metadata records are not cached.
    const cachedMilestones = new Set([
        ...Object.keys(metadata),
        ...unresolvedMilestones,
    ]);
    const milestones = new Set(milestoneSequence.flat());
    const missing = new Set(
        [...milestones].filter(milestone => !cachedMilestones.has(milestone))
    );
    if (missing.size == 0){
        return;
    }
    const result = await fetchMetadata(missing);
    if (!result) return;
    Object.values(result.resolved).forEach((record: MetadataRecord) => {
        record.imgUrl = apiUrl(record.imgUrl);
    });
    return result;
}

/**
 * Submit chartbuilder-share-record and get corresponding share URL.
 * @param milestoneSequence User-submitted chartbuilder milestone sequence.
 * @param completedMilestones Set of milestones marked complete by the submitter.
 * @returns Share URL.
 */
export async function fetchShareUrl(milestoneSequence: string[][], completedMilestones: Set<string>): Promise<string> {
    const token = await postShare(milestoneSequence)
    
    // Not to be confused with the api subdomain.
    const base = window.location.origin + window.location.pathname;
    let shareUrl = `${base}#/chartbuilder?token=${token}`;
    
    if (completedMilestones && completedMilestones.size > 0) {
        const encoded = encodeProgress(completedMilestones, milestoneSequence);
        if (encoded) shareUrl += `&progress=${encoded}`;
    }
    return shareUrl
}
