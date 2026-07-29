import Chart from "@/components/Chart";
import "@/styles/chart.css";
import "@/styles/ChartPage.css";
import milestoneMetadata from '@data/generated/milestone-metadata.json';
import milestoneSequenceMainRaw from '@data/logic/milestone-sequence-main.json';
import removeStarredItems from '@/utils/removeStarredItems.js';
import { apiUrl } from "../utils/apiConfig";
import { useState, useEffect } from "react";
import { sanitizeId } from "../utils/textSanitizers";

type SkipRateData = {
    skip_rate: number | null;
};

type SkipRates = Record<string, SkipRateData>;

function pctToColor(pct: number | null) {
    if (pct === null) return "transparent";
    const hue = (1 - pct) * 120;
    return `hsl(${hue} 70% 50%)`;
}

function Colorbar() {
    return (
        <div className="completion-pct-colorbar" aria-label="Skip percentage color scale">
            <span className="completion-pct-colorbar-label">100%</span>
            <div className="completion-pct-colorbar-gradient skip-pct-colorbar-gradient" />
            <span className="completion-pct-colorbar-label">0%</span>
        </div>
    );
}

async function getSkipPcts(setSkipPcts: (skipPcts: SkipRates) => void){
    const url = apiUrl("/skip-pcts");
    if (!url) return;
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`Response status: ${response.status}`);
        const skipPcts: SkipRates = await response.json();
        const sanitized = Object.fromEntries(
            Object.entries(skipPcts).map(([key, value]) => [
                sanitizeId(key),
                value,
            ])
        );
        setSkipPcts(sanitized);
    } catch (err) {
            console.error(err);
    }
}

export default function SkipPctPage(){
    const [skipPcts, setSkipPcts] = useState<SkipRates>({});
    useEffect(() => {
        getSkipPcts(setSkipPcts);
    }, []);
    const rules = Object.entries(skipPcts)
        .map(([id, data]) => `
    #${id} {
        background-color: ${pctToColor(data.skip_rate)};
    }`)
        .join("\n");
    let milestoneSequenceMain = removeStarredItems(milestoneSequenceMainRaw);
    return (
        <>
            <div className="chart-page-title">
                <h1>Ironman Progression Chart Skip Percentages</h1>
            </div>
            <style>{rules}</style>
            <div className="completion-pct-chart-layout">
                <Colorbar />
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
            </div>
        </>
    )
}
