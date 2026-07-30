import Chart from "@/components/Chart";
import "@/styles/chart.css";
import "@/styles/ChartPage.css";
import milestoneMetadata from '@data/generated/milestone-metadata.json';
import milestoneSequenceMainRaw from '@data/logic/milestone-sequence-main.json';
import removeStarredItems from '@/utils/removeStarredItems.js';
import { apiUrl } from "../utils/apiConfig";
import { useState, useEffect } from "react";
import { sanitizeId } from "../utils/textSanitizers";

type AnnotationViewCountData = {
    view_count: number;
};

type AnnotationViewCounts = Record<string, AnnotationViewCountData>;

type AnnotationStatusData = {
    has_annotation: boolean;
};

type AnnotationStatuses = Record<string, AnnotationStatusData>;

type CountRange = {
    min: number;
    max: number;
};

const LOW_COLOR = [232, 239, 247];
const HIGH_COLOR = [219, 66, 72];

function interpolateColor(low: number[], high: number[], ratio: number) {
    const channels = low.map((value, index) => {
        return Math.round(value + (high[index] - value) * ratio);
    });
    return `rgb(${channels[0]} ${channels[1]} ${channels[2]})`;
}

function countToColor(count: number, range: CountRange) {
    if (count <= 0) return "transparent";
    if (range.max === range.min) return interpolateColor(LOW_COLOR, HIGH_COLOR, 1);
    const ratio = (count - range.min) / (range.max - range.min);
    return interpolateColor(LOW_COLOR, HIGH_COLOR, Math.max(0, Math.min(1, ratio)));
}

function viewCountRange(annotationViewCounts: AnnotationViewCounts): CountRange {
    const counts = Object.values(annotationViewCounts)
        .map(data => data.view_count)
        .filter(count => count > 0);

    if (counts.length === 0) return { min: 0, max: 0 };
    return {
        min: Math.min(...counts),
        max: Math.max(...counts),
    };
}

function AnnotationCountColorbar({ range }: { range: CountRange }) {
    return (
        <div className="completion-pct-colorbar" aria-label="Annotation view count color scale">
            <span className="completion-pct-colorbar-label">{range.max}</span>
            <div className="completion-pct-colorbar-gradient annotation-count-colorbar-gradient" />
            <span className="completion-pct-colorbar-label">{range.min}</span>
        </div>
    );
}

async function getAnnotationViewCounts(
    setAnnotationViewCounts: (annotationViewCounts: AnnotationViewCounts) => void,
) {
    const url = apiUrl("/annotation-view-counts");
    if (!url) return;
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`Response status: ${response.status}`);
        const annotationViewCounts: AnnotationViewCounts = await response.json();
        setAnnotationViewCounts(annotationViewCounts);
    } catch (err) {
        console.error(err);
    }
}

async function getAnnotationStatuses(
    setAnnotationStatuses: (annotationStatuses: AnnotationStatuses) => void,
) {
    const url = apiUrl("/annotation-statuses");
    if (!url) return;
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`Response status: ${response.status}`);
        const annotationStatuses: AnnotationStatuses = await response.json();
        setAnnotationStatuses(annotationStatuses);
    } catch (err) {
        console.error(err);
    }
}

export default function AnnotationCountPage(){
    const [annotationViewCounts, setAnnotationViewCounts] = useState<AnnotationViewCounts>({});
    const [annotationStatuses, setAnnotationStatuses] = useState<AnnotationStatuses>({});
    useEffect(() => {
        getAnnotationViewCounts(setAnnotationViewCounts);
        getAnnotationStatuses(setAnnotationStatuses);
    }, []);

    const range = viewCountRange(annotationViewCounts);
    const rules = Object.entries(annotationViewCounts)
        .map(([milestoneName, data]) => {
            const hasAnnotation = annotationStatuses[milestoneName]?.has_annotation;
            const missingQueriedAnnotation = data.view_count > 0 && hasAnnotation === false;
            return `
    #${sanitizeId(milestoneName)} {
        background-color: ${countToColor(data.view_count, range)};
        ${missingQueriedAnnotation ? "border-color: rgb(220 38 38);" : ""}
    }`;
        })
        .join("\n");
    let milestoneSequenceMain = removeStarredItems(milestoneSequenceMainRaw);

    return (
        <>
            <div className="chart-page-title">
                <h1>Annotation View Counts</h1>
                <span className="subtitle">Last 7 days</span>
            </div>
            <style>{rules}</style>
            <div className="completion-pct-chart-layout annotation-count-layout">
                <Chart
                    milestoneSequence={milestoneSequenceMain}
                    milestoneMetadata={milestoneMetadata}
                    milestonesComplete={new Set<string>()}
                    milestonesHidden={new Set<string>()}
                    hide={{} as Record<string, boolean>}
                    handleNodeContextMenu={() => {}}
                    handleNodeTouchStart={() => {}}
                    handleNodeTouchEnd={() => {}}
                    handleNodeClick={() => {}}
                    readOnly
                />
                <AnnotationCountColorbar range={range} />
            </div>
        </>
    )
}
