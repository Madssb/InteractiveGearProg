import { handleLevels, sanitizeId } from '@/utils/textSanitizers';
import { questNameInitials } from '@/utils/questNameInitials';
import React, { useMemo } from 'react';
import Annotations, { type AnnotationData } from '@/components/Annotations';

type MilestoneMetadata = Record<string, {
  id?: number | string;
  imgUrl: string;
  wikiUrl: string;
  type: string;
}>;

type ChartProps = {
  milestoneSequence: string[][];
  milestoneMetadata: MilestoneMetadata;
  milestonesComplete?: Set<string>;
  milestonesHidden?: Set<string>;
  hide?: Record<string, boolean>;
  handleNodeContextMenu: (event: React.MouseEvent<HTMLDivElement>, milestone: string) => void;
  handleNodeTouchStart: (event: React.TouchEvent<HTMLDivElement>, milestone: string) => void;
  handleNodeTouchEnd: React.TouchEventHandler<HTMLDivElement>;
  handleNodeClick: (milestone: string) => void;
  arrows?: boolean;
  annotatedMilestone?: string;
  annotations?: AnnotationData[];
  onCloseAnnotations?: () => void;
};

type NodeProps = {
  milestone: string;
  milestoneMetadata: MilestoneMetadata;
  milestoneComplete?: boolean;
  milestoneHidden?: boolean;
  onContextMenu: (event: React.MouseEvent<HTMLDivElement>, milestone: string) => void;
  onTouchStart: (event: React.TouchEvent<HTMLDivElement>, milestone: string) => void;
  onTouchEnd: React.TouchEventHandler<HTMLDivElement>;
  onClick: (milestone: string) => void;
};

type NodeGroupProps = {
  milestoneGroup: string[];
  milestoneMetadata: MilestoneMetadata;
  milestonesComplete?: Set<string>;
  milestonesHidden?: Set<string>;
  onContextMenu: NodeProps['onContextMenu'];
  onTouchStart: NodeProps['onTouchStart'];
  onTouchEnd: NodeProps['onTouchEnd'];
  onClick: NodeProps['onClick'];
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
  milestoneComplete,
  milestoneHidden
}: NodeProps) {


  let metadata = milestoneMetadata[handleLevels(milestone)];
  let imgUrl = metadata.imgUrl;
  let wikiUrl = metadata.wikiUrl;
  let id = sanitizeId(milestone)
  let type = metadata.type;

  if (type == "skill") {
    let lvlNum = milestone.split(" ")[0];
    return (
      <>
        <div
          className={`node ${milestoneComplete && "complete"}`}
          title={milestone}
          id={id}
          data-wiki-url={wikiUrl}
          aria-label={milestone}
          onContextMenu={(e) => onContextMenu(e, milestone)}
          onTouchStart={(e) => onTouchStart(e, milestone)}
          onTouchEnd={onTouchEnd}
          onClick={() => onClick(milestone)}
        >
          <div className='skill'>
            <img
              src={imgUrl}
              alt=""
              draggable="false"
            />
            <span>{lvlNum}</span>
          </div>
        </div>
      </>
    )
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
          onContextMenu={(e) => onContextMenu(e, milestone)}
          onTouchStart={(e) => onTouchStart(e, milestone)}
          onTouchEnd={onTouchEnd}
          onClick={() => onClick(milestone)}
        >
          <div className='skill'>
            <img
              src={imgUrl}
              alt={milestone}
              draggable="false"
            />
            <span>{questInitials}</span>
          </div>
        </div>
      </>
    )
  }
  return (
    <>
      <div
        className={`node ${milestoneComplete && "complete"} ${milestoneHidden && "hidden"} ${type}`}
        title={milestone}
        id={id}
        data-wiki-url={wikiUrl}
        onContextMenu={(e) => onContextMenu(e, milestone)}
        onTouchStart={(e) => onTouchStart(e, milestone)}
        onTouchEnd={onTouchEnd}
        onClick={() => onClick(milestone)}
      >
        <img
          src={imgUrl}
          alt={milestone}
          draggable="false"
        />
      </div>
    </>
  )
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
  milestonesComplete,
  milestonesHidden
}: NodeGroupProps) {
  return (
    <div className={"node-group"}>
      {
        milestoneGroup.map(milestone => (
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
          />
        ))
      }
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
  arrows,
  annotatedMilestone,
  annotations = [],
  onCloseAnnotations
}: ChartProps) {
  const visibleMilestoneSequence = useMemo(() => {
    return milestoneSequence
      .map(group =>
        group.filter(milestone => {
          if (milestonesHidden?.has(milestone)) return false;

          const metadata = milestoneMetadata[handleLevels(milestone)]
          if (!metadata) return false;
          if (hide && hide[metadata.type]) return false;
          return true;
        })
      ).filter(group => group.length > 0);
  }, [milestoneSequence, milestoneMetadata, milestonesHidden, hide])

  const annotatedGroupIndex = annotatedMilestone
    ? visibleMilestoneSequence.findIndex(group => group.includes(annotatedMilestone))
    : -1;

  return (
    <div
      className={"chart"}
    >
      {
        visibleMilestoneSequence.map(
          (milestoneGroup, i) => (
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
              />
              {annotatedMilestone && i === annotatedGroupIndex && (
                <div className="chart-mobile-annotations">
                  <Annotations
                    annotations={annotations}
                    onCloseAnnotations={onCloseAnnotations}
                    milestone={annotatedMilestone}
                  />
                </div>
              )}
              {arrows && i < visibleMilestoneSequence.length - 1 && (
                <div className='arrow'>→</div>
              )}
            </React.Fragment>
          )
        )
      }
    </div>
  )
}
