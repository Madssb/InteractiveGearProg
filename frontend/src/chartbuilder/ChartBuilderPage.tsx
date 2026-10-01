import {
  fetchMissingMetadata,
  fetchShareUrl,
} from "@/chartbuilder/ChartBuilder";
import { getShare } from "@/chartbuilder/chartBuilderRequests";
import Chart from "@/components/Chart";
import ContextMenu from "@/components/ContextMenu.jsx";
import SequenceForm from "@/chartbuilder/SequenceForm";
import Footer from "@/components/static/Footer.jsx";
import { decodeProgress } from "@/utils/progressEncoding";
import {
  useLocalStorageSet,
  useLocalStorageState,
} from "@/utils/useLocalStorageState";
import milestoneSequenceMainRaw from "@data/logic/milestone-sequence-main.json";
import React, { useState } from "react";
import { useLocation } from "react-router";
import { ChartbuilderMetadata } from "@/chartbuilder/chartBuilderRequests";



const milestoneSequenceMain = milestoneSequenceMainRaw as string[][];

/**
 * Copy rendered milestone sequence to clipboard in json form.
 * @param {*} milestoneSequence Rendered milestone sequence.
 * @returns Milestone sequence to clipboard.
 */
function extractSequence(milestoneSequence: string[][]) {
  if (!milestoneSequence) return;
  const json = JSON.stringify(milestoneSequence);
  navigator.clipboard.writeText(json);
}

/**
 * Submit chartbuiler share record and copy to clipboard
 * @param {*} milestoneSequence User-submitted chartbuilder milestone sequence.
 * @param {*} completedMilestones Set of milestones marked completed by user.
 */
async function onShareClick(
  milestoneSequence: string[][],
  completedMilestones: Set<string>,
) {
  // Submit chartbuilder share-record.
  const shareUrl = await fetchShareUrl(milestoneSequence, completedMilestones);
  navigator.clipboard.writeText(shareUrl);
}

const EMPTY_NODES_COMPLETE = new Set<string>();

export default function ChartBuilderPage() {
  const initSequence: string[][] = [];
  const initMetadata : ChartbuilderMetadata = {};
  const [milestoneSequenceChartBuilder, setMilestoneSequenceChartBuilder] =
    useLocalStorageState(
      "milestoneSequenceChartBuilder",
      initSequence,
      ["inputSequenceState"],
    );
  const [milestoneMetadata, setMilestoneMetadata] = useLocalStorageState(
    "chartbuilderMetadata",
    initMetadata,
  );
  // old metadata for backwards compatability?.
  const [completedMilestones, setNodesCompleteState] = useLocalStorageSet(
    "nodesCompleteState",
    new Set<string>(),
  );

  // Persistent unresolveds avoid repeated known bad searches.
  const [unresolved, setUnresolved] = useLocalStorageSet(
    "unresolved",
    new Set<string>()
  );

  const [latestUnresolved, setLatestUnresolved] = useState<Set<string>>(new Set());

  const [sharedNodesComplete, setSharedNodesComplete] = useState<Set<string>>(
    new Set(),
  );
  const [loadingLadlorChart, setLoadingLadlorChart] = useState(false);
  const [loadError, setLoadError] = useState("");
  // initialize from Share-URL
  const location = useLocation();
  const isProgressShareView = new URLSearchParams(location.search).has(
    "progress",
  );

  // update sequence on loaded chartbuilder share url.
  React.useEffect(() => {
    const params = new URLSearchParams(location.search);
    const token = params.get("token");

    if (token) {
      const updateSequence = async () => {
        const milestoneSequence = await getShare(token);
        if (milestoneSequence) setMilestoneSequenceChartBuilder(milestoneSequence);
      };
      updateSequence();
    }
  }, [location.search]);

  // load progress
  React.useEffect(() => {
    const params = new URLSearchParams(location.search);
    const progressParam = params.get("progress");
    if (!progressParam) {
      setSharedNodesComplete(new Set<string>());
      return;
    }
    if (milestoneSequenceChartBuilder) {
      setSharedNodesComplete(
        decodeProgress(progressParam, milestoneSequenceChartBuilder),
      );
    }
  }, [location.search, milestoneSequenceChartBuilder]);

  // load metadata
  React.useEffect(() => {
    const updateMetadata = async () => {
      // Fetch only missing metadata records
      const result = await fetchMissingMetadata(
        milestoneSequenceChartBuilder,
        milestoneMetadata,
        unresolved,
      );
      
      const milestones = new Set(milestoneSequenceChartBuilder.flat());
      setLatestUnresolved(new Set(
          [...unresolved].filter((milestone) => milestones.has(milestone)),
      ));
      // Expand existing metadata records.
      if (result !== undefined) {
        // only update metadata when there is something to update.
        setMilestoneMetadata((prev) => ({
          ...prev,
          ...result.resolved,
        }));

        // Cache unresolveds.
        setUnresolved((prev) => new Set([...prev, ...result.unresolved]));
      }
    };
    updateMetadata();
  }, [milestoneSequenceChartBuilder]);

  const [showInput, setShowInput] = useState(false);
  function handleInputClick() {
    setShowInput(!showInput);
  }

  async function handleLoadLadlorChart() {
    setLoadError("");
    const hasExisting = Boolean(
      milestoneSequenceChartBuilder && milestoneSequenceChartBuilder.length,
    );
    if (hasExisting) {
      const shouldReplace = window.confirm(
        "Replace your current chart with Ladlor's chart?",
      );
      if (!shouldReplace) return;
    }

    setMilestoneSequenceChartBuilder(milestoneSequenceMain);
    try {
      setLoadingLadlorChart(true);
    } catch (error) {
      console.error(error);
      setLoadError(
        "Could not load Ladlor chart milestone metadata. Please try again.",
      );
    } finally {
      setLoadingLadlorChart(false);
    }
  }

  // Click milestone to turn background green
  function handleNodeClick(milestone: string) {
    if (isProgressShareView) return;
    setNodesCompleteState((prev) => {
      const next = new Set(prev);
      if (next.has(milestone)) next.delete(milestone);
      else next.add(milestone);
      return next;
    });
  }

  type ContextMenuState = {
      visible: boolean;
      x: number;
      y: number;
      milestone: string | null;
  };

  // Context menu
  const [menu, setMenu] = useState<ContextMenuState>({
    visible: false,
    x: 0,
    y: 0,
    milestone: null,
  });

  function openNodeContextMenu(x: number, y: number, milestone: string) {
    if (isProgressShareView) return;

    setMenu({
      visible: true,
      x,
      y,
      milestone,
    });
  }

  function handleNodeContextMenu(
    e: React.MouseEvent<HTMLElement>,
    milestone: string,
  ) {
    e.preventDefault();
    openNodeContextMenu(e.pageX, e.pageY, milestone);
  }

  // long press behaves like right click
  function handleNodeTouchStart(
    e: React.TouchEvent<HTMLElement>,
    milestone: string,
  ) {
    if (isProgressShareView) return;

    const touch = e.touches[0];
    const { pageX, pageY } = touch;

    e.persist?.(); // keep event for later
    const timeoutId = setTimeout(() => {
      openNodeContextMenu(pageX, pageY, milestone);
    }, 600); // long-press threshold
    e.currentTarget.dataset.longPressTimeout = String(timeoutId);
  }

  function handleNodeTouchEnd(e: React.TouchEvent<HTMLElement>) {
    const timeoutId = e.currentTarget.dataset.longPressTimeout;
    if (timeoutId) clearTimeout(Number(timeoutId));
  }

  function handleCloseMenu() {
    setMenu({ ...menu, visible: false });
  }

  function handleDelete(milestoneToDelete: string) {
    if (isProgressShareView) return;
    setMilestoneSequenceChartBuilder((seq) =>
      seq
        .map((milestoneGroup) =>
          milestoneGroup.filter((milestone) => milestone !== milestoneToDelete),
        )
        .filter((milestoneGroup) => milestoneGroup.length > 0),
    );
  }

  React.useEffect(() => {
    function handleClickOutside() {
      setMenu((prev) => (prev.visible ? { ...prev, visible: false } : prev));
    }
    document.addEventListener("click", handleClickOutside);
    return () => document.removeEventListener("click", handleClickOutside);
  }, []);
  const buttonStyle = { backgroundColor: "gray" };

  const actions = [
    { handler: handleInputClick, label: "Show input" },
    {
      handler: () =>
        onShareClick(milestoneSequenceChartBuilder, completedMilestones),
      label: "Share",
    },
    {
      handler: () => extractSequence(milestoneSequenceChartBuilder),
      label: "Extract",
    },
    {
      handler: handleLoadLadlorChart,
      label: loadingLadlorChart ? "Loading..." : "Load Main Chart",
      disabled: loadingLadlorChart,
    },
  ];
  const displayedNodesComplete = isProgressShareView
    ? (sharedNodesComplete ?? EMPTY_NODES_COMPLETE)
    : completedMilestones;
    return (
    <>
      <div id="titleBar" style={{ position: "relative", height: "80px" }}>
        <div
          style={{
            position: "absolute",
            left: "50%",
            top: "50%",
            transform: "translate(-50%, -50%)",
            textAlign: "center",
          }}
        >
          <h1>Chart Builder</h1>
          <span className="subtitle">Made by Ladlor</span>
        </div>
        <div
          style={{
            position: "absolute",
            right: "0",
            top: "50%",
            transform: "translateY(-50%)",
            display: "flex",
            gap: "8px",
          }}
        >
          {actions.map((a) => (
            <button
              key={a.label}
              onClick={a.handler}
              disabled={Boolean(a.disabled)}
              style={buttonStyle}
            >
              {a.label}
            </button>
          ))}
        </div>
      </div>

      {showInput && (
        <SequenceForm
          setMilestoneSequence={setMilestoneSequenceChartBuilder}
          initialSequence={milestoneSequenceChartBuilder}
        />
      )}
      {latestUnresolved.size > 0 && (
        <p>
          Couldnt resolve the following: {Array.from(latestUnresolved).join(", ")}
        </p>
      )}
      {milestoneSequenceChartBuilder && milestoneMetadata && (
        <Chart
          milestoneSequence={milestoneSequenceChartBuilder}
          milestoneMetadata={milestoneMetadata}
          milestonesComplete={displayedNodesComplete}
          handleNodeContextMenu={handleNodeContextMenu}
          handleNodeTouchStart={handleNodeTouchStart}
          handleNodeTouchEnd={handleNodeTouchEnd}
          handleNodeClick={handleNodeClick}
          readOnly={isProgressShareView}
          arrows={true}
        />
      )}
      {menu.visible && menu.milestone !== null && (
        <ContextMenu
          milestone={menu.milestone}
          milestoneMetadata={milestoneMetadata}
          onClose={handleCloseMenu}
          onDelete={handleDelete}
          x={menu.x}
          y={menu.y}
        />
      )}
      {loadError && <p style={{ color: "crimson" }}>{loadError}</p>}
      <Footer showImageAttribution={true} />
    </>
  );
}
