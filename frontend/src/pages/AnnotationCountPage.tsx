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

export default function AnnotationCountPage(){
    const [annotationViewCounts, setAnnotationViewCounts] = useState<AnnotationViewCounts>({});
    useEffect(() => {
        getAnnotationViewCounts(setAnnotationViewCounts);
    }, []);

    const range = viewCountRange(annotationViewCounts);
    const topMilestones = Object.entries(annotationViewCounts)
        .filter(([, data]) => data.view_count > 0)
        .sort((a, b) => b[1].view_count - a[1].view_count)
        .slice(0, 12);
    const totalViews = Object.values(annotationViewCounts)
        .reduce((sum, data) => sum + data.view_count, 0);
    const viewedMilestoneCount = topMilestones.length === 12
        ? Object.values(annotationViewCounts).filter(data => data.view_count > 0).length
        : topMilestones.length;
    const rules = Object.entries(annotationViewCounts)
        .map(([milestoneName, data]) => `
    #${sanitizeId(milestoneName)} {
        background-color: ${countToColor(data.view_count, range)};
    }`)
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
                <AnnotationCountColorbar range={range} />
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
                <aside className="annotation-count-overview">
                    <div className="annotation-count-metric">
                        <span>Total views</span>
                        <strong>{totalViews}</strong>
                    </div>
                    <div className="annotation-count-metric">
                        <span>Milestones viewed</span>
                        <strong>{viewedMilestoneCount}</strong>
                    </div>
                    <div className="annotation-count-metric">
                        <span>Max count</span>
                        <strong>{range.max}</strong>
                    </div>
                    <ol className="annotation-count-top-list">
                        {topMilestones.map(([id, data]) => (
                            <li key={id}>
                                <span>{id}</span>
                                <strong>{data.view_count}</strong>
                            </li>
                        ))}
                    </ol>
                </aside>
            </div>
        </>
    )
}
