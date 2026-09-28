import Chart from "@/components/Chart";
import "@/styles/chart.css";
import "@/styles/ChartPage.css";
import milestoneMetadataRaw from '@data/generated/milestone-metadata.json';
import mainMilestoneSequence from '@data/logic/milestone-sequence-main.json';
import { MilestoneMetadata } from "@/components/Chart";
import { apiUrl } from "../utils/apiConfig";
import { useState, useEffect } from "react";

const milestoneMetadata = milestoneMetadataRaw as MilestoneMetadata;

type CompletionRateData = {
    completion_rate: number | null;
};

type CompletionRates = Record<string, CompletionRateData>;

function pctToColor(pct: number | null) {
    if (pct === null) return "transparent";
    const hue = pct * 120;
    return `hsl(${hue} 70% 50%)`;
}

function Colorbar() {
    return (
        <div className="completion-pct-colorbar" aria-label="Completion percentage color scale">
            <span className="completion-pct-colorbar-label">100%</span>
            <div className="completion-pct-colorbar-gradient" />
            <span className="completion-pct-colorbar-label">0%</span>
        </div>
    );
}

async function getCompletionPcts(setCompletionPcts: (completionPcts: CompletionRates) => void){
    const url = apiUrl("/completion-pcts");
    if (!url) return;
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`Response status: ${response.status}`);
        const completionPcts: CompletionRates = await response.json();
        setCompletionPcts(completionPcts);
    } catch (err) {
            console.error(err);
    }
}

export default function ComplectionPctPage(){
    const [completionPcts, setCompletionPcts] = useState<CompletionRates>({});
    useEffect(() => {
        getCompletionPcts(setCompletionPcts);
    }, []);
    const rules = Object.entries(completionPcts)
        .map(([milestoneName, data]) => {
            const id = milestoneMetadata[milestoneName]?.id;
            if (id == null) return "";
            return `
    #milestone-${id} {
        background-color: ${pctToColor(data.completion_rate)};
    }`;
        })
        .join("\n");
    return (
        <>
            <div className="chart-page-title">
                <h1>Ironman Progression Chart Completion Percentages</h1>
            </div>
            <style>{rules}</style>
            <div className="completion-pct-chart-layout">
                <Chart 
                    milestoneSequence={mainMilestoneSequence}
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
                <Colorbar />
            </div>
        </>
    )
}
