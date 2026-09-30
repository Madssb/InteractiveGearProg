/**
 * Chartbuilder requests to backend live here.
 */
import { apiUrl } from '@/utils/apiConfig';

export type MetadataRecord = {
    imgUrl: string;
    wikiUrl: string;
};
export type ChartbuilderMetadata = Record<string, MetadataRecord>;

export type ChartbuilderMetadataResponse = {
    resolved: ChartbuilderMetadata;
    unresolved: Set<string>;
};

type ChartbuilderMetadataResponseRaw = {
    resolved: ChartbuilderMetadata;
    unresolved: string[];
}

/**
 * Fetch Metadata for specified milestones from backend, if any.
 * @param milestones Set of milestones for which to fetch metadata for.
 * @returns Resolved metadata and unresolved milestones, or undefined if empty set provided.
 * @throws {Error} If request failed.
 */
export async function fetchMetadata(milestones: Set<string>): Promise<ChartbuilderMetadataResponse | undefined >  {
    const url = apiUrl("/chartbuilder-metadata");
    if (!(milestones instanceof Set)) {
        throw new Error("milestones must be a Set");
    }
    // Don't make redundant requests.
    if (milestones.size === 0) return;

    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(Array.from(milestones))
    });

    if (!response.ok){
        throw new Error(`Request failed; response status: ${response.status}`);
    }

    const res = await response.json() as ChartbuilderMetadataResponseRaw;
    // coerce into expected shape
    const out: ChartbuilderMetadataResponse = {"resolved": res.resolved, "unresolved": new Set(res.unresolved)}
    
    return out;

}

/**
 * Submit chartbuilder share record if sequence exists.
 * @param milestoneSequence User-submitted milestone sequence.
 * @param completedMilestones Set of milestones marked complete.
 * @returns Chartbuilder share-token if exists, or undefined.
 * @throws {Error} If request failed.
 */
export async function postShare(milestoneSequence: string[][]): Promise<string | undefined> {
    // Don't make redundant requests.
    if (!milestoneSequence) return;

    const url = apiUrl("/share/");

    const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(milestoneSequence)
    });

    if (!response.ok) throw new Error(`Request failed; Response status: ${response.status}`);

    return await response.json();
}

/**
 * Fetch user-submitted milestone sequence if exists.
 * @param token Chartbuilder share-token
 * @returns Shared chartbuilder milestone sequence if exists, or undefined.
 * @throws {Error} if request failed.
 */
export async function getShare(
    token: string,
): Promise<string[][] | undefined> {
    if (!token) return;
    const url = apiUrl(`/share/?token=${token}`);

    const response = await fetch(url);
    const data = await response.json();  

    if (!response.ok) throw new Error(`Response status: ${response.status}, ${data.detail}`);
    
    return await data;
}
