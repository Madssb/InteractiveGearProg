import Chart from "@/components/Chart";
import ConfigMenu from "@/components/ConfigMenu";
import ContextMenu from '@/components/ContextMenu.jsx';
import Acknowledgements from '@/components/static/Acknowledgements.jsx';
import FAQSection from '@/components/static/FAQSection.jsx';
import Footer from '@/components/static/Footer.jsx';
import '@/styles/ChartPage.css';
import { apiUrl } from '@/utils/apiConfig';
import migrateLegacySharedNodeStates from '@/utils/migrateState';
import { applyThemePreference, THEME_PREFERENCE_KEY } from '@/utils/themePreference';
import { useLocalStorageSet, useLocalStorageState } from '@/utils/useLocalStorageState';
import milestoneMetadata from '@data/generated/milestone-metadata.json';
import milestoneSequenceBarebones from '@data/generated/milestone-sequence-barebones.json';
import milestoneSequenceRetirement from '@data/logic/milestone-sequence-retirement.json';
import milestoneSequenceMain from '@data/logic/milestone-sequence-main.json';
import { encodeProgress, decodeProgress } from '@/utils/progressEncoding';
import React from 'react';
import { useLocation } from 'react-router';
import Annotations from "../components/Annotations";

const PROGRESS_SNAPSHOT_DATE_KEY = "progressSnapshotSubmittedDate";
const HIDDEN_MILESTONES_SNAPSHOT_DATE_KEY = "hiddenMilestonesSnapshotSubmittedDate";

function localDateKey(date = new Date()) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
}

async function submitProgressSnapshot(milestonesComplete) {
    const url = apiUrl("/submit-progress-snapshot");
    if (!url) return;

    // make submission a maximum of once per day, per session
    const today = localDateKey();
    if (localStorage.getItem(PROGRESS_SNAPSHOT_DATE_KEY) === today) return;
    localStorage.setItem(PROGRESS_SNAPSHOT_DATE_KEY, today);

    try {
        const response = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify([...milestonesComplete]),
        });

        if (!response.ok) throw new Error(`Response status: ${response.status}`);
    } catch (err) {
        if (localStorage.getItem(PROGRESS_SNAPSHOT_DATE_KEY) === today) {
            localStorage.removeItem(PROGRESS_SNAPSHOT_DATE_KEY);
        }
        console.error("Failed to submit progress snapshot", err);
    }
}

async function submitHiddenMilestonesSnapshot(milestonesHidden) {
    // do nothing if set of user-hidden milestones is zero
    if (!milestonesHidden.size) return;
    const url = apiUrl("/submit-hidden-milestones-snapshot");
    if (!url) return;
    
    // make submission a maximum of once per day, per session
    const today = localDateKey();
    if (localStorage.getItem(HIDDEN_MILESTONES_SNAPSHOT_DATE_KEY) === today) return;
    localStorage.setItem(HIDDEN_MILESTONES_SNAPSHOT_DATE_KEY, today);

    try {
        const response = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify([...milestonesHidden]),
        });

        if (!response.ok) throw new Error(`Response status: ${response.status}`);
    } catch (err) {
        if (localStorage.getItem(HIDDEN_MILESTONES_SNAPSHOT_DATE_KEY) === today) {
            localStorage.removeItem(HIDDEN_MILESTONES_SNAPSHOT_DATE_KEY);
        }
        console.error("Failed to submit hidden milestones snapshot", err);
    }
}

async function submitAnnotationViewEvent(milestone) {
    if (!milestone) return;
    const url = apiUrl("/submit-annotation-view-event");
    if (!url) return;

    try {
        const response = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ milestone_name: milestone }),
        });

        if (!response.ok) throw new Error(`Response status: ${response.status}`);
    } catch (err) {
        console.error("Failed to submit annotation view event", err);
    }
}

async function getMilestoneAnnotations(milestone){
    if (!milestone) return { annotations: [], status: 'idle' };
    const milestoneId = milestoneMetadata[milestone]?.id;
    if (!milestoneId) return { annotations: [], status: 'loaded' };
    const url = apiUrl(`/annotations?milestone_id=${milestoneId}`)
    if (!url) return { annotations: [], status: 'unavailable' };
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`Response status: ${response.status}`);
        const annotations = await response.json();
        return { annotations, status: 'loaded' };
    } catch (err) {
        console.error(err);
        return { annotations: [], status: 'error' };
    }
}

const canonicalSequence = [
    ...milestoneSequenceMain,
    ...milestoneSequenceRetirement,
];
const EMPTY_MILESTONES = new Set();

export default function ChartPage(){

    const location = useLocation();
    const isProgressShareView = new URLSearchParams(location.search).has("progress");

    const progressSnapshotAttempted = React.useRef(false);
    
    const [shareStatus, setShareStatus] = React.useState(null);

    const [milestonesHidden, setMilestonesHidden] = useLocalStorageSet('milestonesHidden', new Set(), ['nodesHiddenState']);
    // set of milestones marked as complete by user
    const [milestonesComplete, setMilestonesComplete] = useLocalStorageSet('milestonesComplete', new Set(), ['nodesCompleteState']);
    const [hide, setHide] = useLocalStorageState('hide', {
        item: false,
        prayer: false,
        construction: false,
        slayer: false,
        spell: false,
        skill: false,
    });

    // Annotation management
    const [annotations, setAnnotations] = React.useState([]);
    const [annotationStatus, setAnnotationStatus] = React.useState('idle');
    const [annotatedMilestone, setAnnotatedMilestone] = React.useState();

    async function handleShowAnnotations(milestone){
        setAnnotatedMilestone(milestone);
        setAnnotations([]);
        setAnnotationStatus('loading');
        submitAnnotationViewEvent(milestone);
        const result = await getMilestoneAnnotations(milestone);
        setAnnotations(result.annotations);
        setAnnotationStatus(result.status);
    }
    async function handleCloseAnnotations(){
        setAnnotations([]);
        setAnnotationStatus('idle');
        setAnnotatedMilestone();
    }

    function handleHideClick(milestone){
        // disabled in shareview
        if (isProgressShareView) return; 
        setMilestonesHidden(prev => {
            const next = new Set(prev);
            if (next.has(milestone)) next.delete(milestone);
            else next.add(milestone);
            return next;
        });
    }
    function handleShowClick(){
        // disabled in shareview
        if (isProgressShareView) return;
        setMilestonesHidden(new Set());
    }
    function handleNodeClick(milestone) {
        // disabled in shareview
        if (isProgressShareView) return;
        setMilestonesComplete(prev => {
            const next = new Set(prev);
            if (next.has(milestone)) next.delete(milestone);
            else next.add(milestone);
            return next;
        });
    }
    // Context menu
    const [menu, setMenu] = React.useState({
        visible: false,
        /** Pixel coordinates */
        x: 0,
        y: 0,
        /** Milestone for which the menu is open */
        milestone: null,
    });
    function handleNodeContextMenu(e, milestone) {
        e.preventDefault();
        // disabled in shareview
        if (isProgressShareView) return;
        const touch = e.touches?.[0] || e.changedTouches?.[0];
        const x = touch?.pageX ?? e.pageX;
        const y = touch?.pageY ?? e.pageY;
        setMenu({
            visible: true,
            x,
            y,
            milestone,
        });
    }

    // long press behaves like right click
    function handleNodeTouchStart(e, milestone) {
        // disabled in shareview
        if (isProgressShareView) return;
        e.persist?.(); // keep event for later
        const timeoutId = setTimeout(() => {
            handleNodeContextMenu(e, milestone); // trigger context menu
        }, 600); // long-press threshold
        e.target.dataset.longPressTimeout = timeoutId;
    }

    function handleNodeTouchEnd(e) {
        const timeoutId = e.target.dataset.longPressTimeout;
        if (timeoutId) clearTimeout(timeoutId);
    }
    
    // clicks not on a milestone close the menu
    function handleCloseMenu() {
        setMenu({ ...menu, visible: false });
    }
    React.useEffect(() => {
        function handleClickOutside() {
            setMenu(prev => (prev.visible ? { ...prev, visible: false } : prev));
        }
        document.addEventListener("click", handleClickOutside);
        return () => document.removeEventListener("click", handleClickOutside);
    }, []);

    // localstorage migration stuff
    const [progressSnapshotReady, setProgressSnapshotReady] = React.useState(false);
    React.useEffect(() => {
        migrateLegacySharedNodeStates(setMilestonesComplete);
        setProgressSnapshotReady(true);
    }, [setMilestonesComplete]);

    // === Load things
    // load theme preferences
    const [themePreference, setThemePreference] = useLocalStorageState(THEME_PREFERENCE_KEY, 'system');
    React.useEffect(() => {
        applyThemePreference(themePreference);
    }, [themePreference]);

    // Load share state from encoded url param
    const [sharedMilestones, setSharedMilestones] = React.useState(null);
    React.useEffect(() => {
        const params = new URLSearchParams(location.search);
        const progressParam = params.get("progress");
        if (!progressParam) {
            setSharedMilestones(null);
            return;
        }
        setSharedMilestones(decodeProgress(progressParam, canonicalSequence));
    }, [location.search]);

    // === Submit things
    // submit set of milestones marked complete
    React.useEffect(() => {
        if (!progressSnapshotReady) return;
        if (progressSnapshotAttempted.current) return;
        progressSnapshotAttempted.current = true;
        submitProgressSnapshot(milestonesComplete);
    }, [progressSnapshotReady, milestonesComplete]);

    // submit set of milestones hidden by player
    React.useEffect(() => {
        if (!progressSnapshotReady) return;
        submitHiddenMilestonesSnapshot(milestonesHidden);
    }, [progressSnapshotReady, milestonesHidden]);

    // on click func for copying share url to clipboard
    async function handleShareProgress() {
        const base = window.location.origin + window.location.pathname;
        let shareUrl;
        // dont redo url construction if already in shareview
        if (isProgressShareView) {
            shareUrl = `${base}#/${location.search}`;
        } else {
            const encoded = encodeProgress(milestonesComplete, canonicalSequence);
            if (!encoded) return;
            shareUrl = `${base}#/?progress=${encoded}`;
        }
        try {
            await navigator.clipboard.writeText(shareUrl);
            setShareStatus('copied');
        } catch {
            setShareStatus('error');
        }
        setTimeout(() => setShareStatus(null), 2000);
    }

    // set of completed milestones from shares
    const displayedMilestonesComplete = isProgressShareView
        ? sharedMilestones ?? EMPTY_MILESTONES
        : milestonesComplete;

    // === Local storage states
    const [showRetirement, setShowRetirement] = useLocalStorageState('showRetirement', false);
    const [showBareBones, setShowBareBones] = useLocalStorageState('showBareBones', false);
    
    // Non-local states
    const [showOptions, setShowOptions] = React.useState(false);
    
        return (
        <>
            <div className="chart-page-header">
                    <div className="chart-page-title">
                        <h1>Interactive Ironman Progression Chart</h1>
                        <span className="subtitle">Curated by the Ironscape community — made by Ladlor</span>
                    </div>
                    <button
                        onClick={handleShareProgress}
                        disabled={displayedMilestonesComplete.size === 0 || shareStatus === 'copied'}
                        className="chart-page-share-button"
                        aria-label="Share progress"
                        title={shareStatus === 'copied' ? 'Link copied!' : 'Share your progress'}
                    >
                        {shareStatus === 'copied' ? '✓' : '🔗'}
                    </button>
                    <button
                        className={`chart-page-options-button ${showOptions ? "active": ""}`}
                        onClick={() => setShowOptions(!showOptions)}
                        id="options-button"
                        aria-label="Show settings"
                    >
                        <img src="https://oldschool.runescape.wiki/images/Settings.png"/>
                    </button>
            </div>
            {showOptions && (
                <ConfigMenu
                    showRetirement={showRetirement}
                    setShowRetirement={setShowRetirement}
                    showBareBones={showBareBones}
                    setShowBareBones={setShowBareBones}
                    themePreference={themePreference}
                    setThemePreference={setThemePreference}
                    hide={hide}
                    setHide={setHide}
                />
            )}
            {showBareBones && (
                <Chart
                    milestoneSequence={milestoneSequenceBarebones}
                    milestoneMetadata={milestoneMetadata}
                    milestonesComplete={displayedMilestonesComplete}
                    milestonesHidden={milestonesHidden}
                    hide={hide}
                    handleNodeContextMenu={handleNodeContextMenu}
                    handleNodeTouchStart={handleNodeTouchStart}
                    handleNodeTouchEnd={handleNodeTouchEnd}
                    handleNodeClick={handleNodeClick}
                    readOnly={isProgressShareView}
                    arrows={true}
                    annotatedMilestone={annotatedMilestone}
                    annotations={annotations}
                    annotationStatus={annotationStatus}
                    onCloseAnnotations={handleCloseAnnotations}
                />
            )}
            {!showBareBones && (
                <Chart
                    milestoneSequence={milestoneSequenceMain}
                    milestoneMetadata={milestoneMetadata}
                    milestonesComplete={displayedMilestonesComplete}
                    milestonesHidden={milestonesHidden}
                    hide={hide}
                    handleNodeContextMenu={handleNodeContextMenu}
                    handleNodeTouchStart={handleNodeTouchStart}
                    handleNodeTouchEnd={handleNodeTouchEnd}
                    handleNodeClick={handleNodeClick}
                    readOnly={isProgressShareView}
                    arrows={true}
                    annotatedMilestone={annotatedMilestone}
                    annotations={annotations}
                    annotationStatus={annotationStatus}
                    onCloseAnnotations={handleCloseAnnotations}
                />
            )}
            {showRetirement && (
                <>
                    <div style={{ /*  */
                        "height":"40px"
                    }}/>
                    <Chart
                        milestoneSequence={milestoneSequenceRetirement}
                        milestoneMetadata={milestoneMetadata}
                        milestonesComplete={displayedMilestonesComplete}
                        milestonesHidden={milestonesHidden}
                        hide={hide}
                        handleNodeContextMenu={handleNodeContextMenu}
                        handleNodeTouchStart={handleNodeTouchStart}
                        handleNodeTouchEnd={handleNodeTouchEnd}
                        handleNodeClick={handleNodeClick}
                        readOnly={isProgressShareView}
                        arrows={false}
                        annotatedMilestone={annotatedMilestone}
                        annotations={annotations}
                        annotationStatus={annotationStatus}
                        onCloseAnnotations={handleCloseAnnotations}
                    />
                </>
            )}
            {!isProgressShareView && milestonesHidden.size > 0 && (
                <button
                    id="show-button"
                    onClick={handleShowClick}
                >
                    Show hidden items
                </button>
            )}
            {annotatedMilestone && (
                <div className="chart-page-annotations">
                    <Annotations
                        annotations={annotations}
                        status={annotationStatus}
                        onCloseAnnotations={handleCloseAnnotations}
                        milestone={annotatedMilestone}
                    />
                </div>
            )}
            {menu.visible && (
                <ContextMenu
                    milestone={menu.milestone}
                    milestoneMetadata={milestoneMetadata}
                    onClose={handleCloseMenu}
                    onHide={handleHideClick}
                    onShowAnnotations={handleShowAnnotations}
                    x={menu.x}
                    y={menu.y}
                />
            )}
            <Acknowledgements />
            <FAQSection />
            <Footer showImageAttribution={true}/>
        </>
    )
}
