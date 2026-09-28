import Annotations, { type AnnotationData } from "@/components/Annotations";
import { questNameInitials } from "@/utils/questNameInitials";
import React, { useMemo } from "react";
import { ChartbuilderMetadata } from "@/chartbuilder/chartBuilderRequests";

type MainMetadataRecord = {
  imgUrl: string;
  wikiUrl: string;
  id: string;
  type: string;
}

export type MilestoneMetadata = Record<string, MainMetadataRecord>;

type ChartProps = {
  // All chart types.
  milestoneSequence: string[][];
  milestoneMetadata: MilestoneMetadata | ChartbuilderMetadata;
  milestonesComplete?: Set<string>;
  handleNodeContextMenu: (
    event: React.MouseEvent<HTMLDivElement>,
    milestone: string,
  ) => void;
  handleNodeTouchStart: (
    event: React.TouchEvent<HTMLDivElement>,
    milestone: string,
  ) => void;
  handleNodeTouchEnd: React.TouchEventHandler<HTMLDivElement>;
  handleNodeClick: (milestone: string) => void;
  
  // Main-chart & retirement home,
  annotations?: AnnotationData[];
  annotatedMilestone?: string;
  onCloseAnnotations?: () => void;
  hide?: Record<string, boolean>;
  milestonesHidden?: Set<string>;
  readOnly?: boolean;
  annotationStatus?: "idle" | "loading" | "loaded" | "unavailable" | "error";
  
  // Retirement home exclusive.
  arrows?: boolean;
};

type NodeProps = {
  milestone: string;
  milestoneMetadata: MilestoneMetadata | ChartbuilderMetadata;
  milestoneComplete?: boolean;
  milestoneHidden?: boolean;
  onContextMenu: (
    event: React.MouseEvent<HTMLDivElement>,
    milestone: string,
  ) => void;
  onTouchStart: (
    event: React.TouchEvent<HTMLDivElement>,
    milestone: string,
  ) => void;
  onTouchEnd: React.TouchEventHandler<HTMLDivElement>;
  onClick: (milestone: string) => void;
  readOnly?: boolean;
};

type NodeGroupProps = {
  milestoneGroup: string[];
  milestoneMetadata: MilestoneMetadata | ChartbuilderMetadata;
  milestonesComplete?: Set<string>;
  milestonesHidden?: Set<string>;
  onContextMenu: NodeProps["onContextMenu"];
  onTouchStart: NodeProps["onTouchStart"];
  onTouchEnd: NodeProps["onTouchEnd"];
  onClick: NodeProps["onClick"];
  readOnly?: boolean;
};

/**
 * Renders a node with milestone, behavior dependent on if type is skill or non-skill.
 *
 */
function Node({
  milestone,
  milestoneMetadata,
  onContextMenu,
  onTouchStart,
  onTouchEnd,
  onClick,
  readOnly,
  milestoneComplete,
  milestoneHidden,
}: NodeProps) {
  let metadata = milestoneMetadata[milestone];
  let imgUrl = metadata.imgUrl;
  let wikiUrl = metadata.wikiUrl;
  
  const isMainMetadata = "type" in metadata;

  const id = isMainMetadata
      ? `milestone-${metadata.id}`
      : undefined;

  const type = isMainMetadata
      ? metadata.type
      : undefined;

  if (type == "skill") {
    let lvlNum = milestone.split(" ")[0];
    return (
      <>
        <div
          className={`node ${milestoneComplete ? "complete" : ""} ${milestoneHidden && "hidden"} ${type}`}
          title={milestone}
          id={id}
          data-wiki-url={wikiUrl}
          aria-label={milestone}
          onContextMenu={
            readOnly ? undefined : (e) => onContextMenu(e, milestone)
          }
          onTouchStart={
            readOnly ? undefined : (e) => onTouchStart(e, milestone)
          }
          onTouchEnd={readOnly ? undefined : onTouchEnd}
          onClick={readOnly ? undefined : () => onClick(milestone)}
        >
          <div className="skill">
            <img src={imgUrl} alt="" draggable="false" />
            <span>{lvlNum}</span>
          </div>
        </div>
      </>
    );
  }
  if (type == "quest") {
    const questInitials = questNameInitials(milestone);
    return (
      <>
        <div
          className={`node ${milestoneComplete && "complete"} ${milestoneHidden && "hidden"} ${type}`}
          title={milestone}
          id={id}
          data-wiki-url={wikiUrl}
          onContextMenu={
            readOnly ? undefined : (e) => onContextMenu(e, milestone)
          }
          onTouchStart={
            readOnly ? undefined : (e) => onTouchStart(e, milestone)
          }
          onTouchEnd={readOnly ? undefined : onTouchEnd}
          onClick={readOnly ? undefined : () => onClick(milestone)}
        >
          <div className="skill">
            <img src={imgUrl} alt={milestone} draggable="false" />
            <span>{questInitials}</span>
          </div>
        </div>
      </>
    );
  }
  return (
    <>
      <div
        className={`node ${milestoneComplete ? "complete" : ""} ${milestoneHidden && "hidden"} ${type}`}
        title={milestone}
        id={id}
        data-wiki-url={wikiUrl}
        onContextMenu={
          readOnly ? undefined : (e) => onContextMenu(e, milestone)
        }
        onTouchStart={readOnly ? undefined : (e) => onTouchStart(e, milestone)}
        onTouchEnd={readOnly ? undefined : onTouchEnd}
        onClick={readOnly ? undefined : () => onClick(milestone)}
      >
        <img src={imgUrl} alt={milestone} draggable="false" />
      </div>
    </>
  );
}

/**
 * Renders a group of nodes
 *
 */
function NodeGroup({
  milestoneGroup,
  milestoneMetadata,
  onContextMenu,
  onTouchStart,
  onTouchEnd,
  onClick,
  readOnly,
  milestonesComplete,
  milestonesHidden,
}: NodeGroupProps) {
  return (
    <div className={"node-group"}>
      {milestoneGroup.map((milestone) => (
        <Node
          key={milestone}
          milestone={milestone}
          milestoneMetadata={milestoneMetadata}
          milestoneComplete={milestonesComplete?.has(milestone)}
          milestoneHidden={milestonesHidden?.has(milestone)}
          onContextMenu={onContextMenu}
          onTouchStart={onTouchStart}
          onTouchEnd={onTouchEnd}
          onClick={onClick}
          readOnly={readOnly}
        />
      ))}
    </div>
  );
}

/**
 * Renders a chart composed of grouped nodes.
 * Handles context menu logic and node state (complete, skipped, etc.).
 */
export default function Chart({
  milestoneSequence,
  milestoneMetadata,
  milestonesComplete,
  milestonesHidden,
  hide,
  handleNodeContextMenu,
  handleNodeTouchStart,
  handleNodeTouchEnd,
  handleNodeClick,
  readOnly = false,
  arrows = true,
  annotatedMilestone,
  annotations = [],
  annotationStatus = "idle",
  onCloseAnnotations,
}: ChartProps) {
  const visibleMilestoneSequence = useMemo(() => {
    return milestoneSequence
      .map((group) =>
        group.filter((milestone) => {
          // Dont show user-hidden milestones. skip if milestonesHidden is undefined.
          if (milestonesHidden?.has(milestone)) return false;

          const metadata = milestoneMetadata[milestone];
          // Milestones with no metadata cannot be shown.
          if (!metadata) return false;

          if ("type" in metadata && hide?.[metadata.type]) return false;
          return true;
        }),
      )
      .filter((group) => group.length > 0); // Dont render empty groups.
  }, [milestoneSequence, milestoneMetadata, milestonesHidden, hide]);

  const annotatedGroupIndex = annotatedMilestone
    ? visibleMilestoneSequence.findIndex((group) =>
        group.includes(annotatedMilestone),
      )
    : -1;

  return (
    <div className={"chart"}>
      {visibleMilestoneSequence.map((milestoneGroup, i) => (
        <React.Fragment key={i}>
          <NodeGroup
            milestoneGroup={milestoneGroup}
            milestoneMetadata={milestoneMetadata}
            milestonesComplete={milestonesComplete}
            milestonesHidden={milestonesHidden}
            onContextMenu={handleNodeContextMenu}
            onTouchStart={handleNodeTouchStart}
            onTouchEnd={handleNodeTouchEnd}
            onClick={handleNodeClick}
            readOnly={readOnly}
          />
          {annotatedMilestone && i === annotatedGroupIndex && (
            <div className="chart-mobile-annotations">
              <Annotations
                annotations={annotations}
                status={annotationStatus}
                onCloseAnnotations={onCloseAnnotations}
                milestone={annotatedMilestone}
              />
            </div>
          )}
          {arrows && i < visibleMilestoneSequence.length - 1 && (
            <div className="arrow">→</div>
          )}
        </React.Fragment>
      ))}
    </div>
  );
}
