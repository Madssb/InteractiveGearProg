import '@/styles/Annotations.css';

export type AnnotationData = {
    annotation_id: number;
    up_count: number;
    down_count: number;
    chart_version: string;
    annotation_text: string;
    created_at: string;
};

type AnnotationProps = {
    annotation: AnnotationData;
};

function Annotation({ annotation }: AnnotationProps) {
    const score = annotation.up_count - annotation.down_count;

    return (
        <div className="annotation">
            <div className="annotation-text">{annotation.annotation_text}</div>
            <div className="annotation-footer">
                <div className="annotation-footer-item">upvotes: {annotation.up_count}</div>
                <div className="annotation-footer-item">downvotes: {annotation.down_count}</div>
                <div className="annotation-footer-item">date: {annotation.created_at}</div>
                <div className="annotation-footer-item">version: {annotation.chart_version}</div>
                <div className="annotation-footer-item">annotation ID: {annotation.annotation_id}</div>
            </div>
        </div>
    );
}

type AnnotationsProps = {
    annotations: AnnotationData[];
    milestone: string;
    onCloseAnnotations?: () => void;
};

export default function Annotations({ annotations, onCloseAnnotations, milestone }: AnnotationsProps) {
    return (
        <div className="annotations">
            <div className="annotations-header">
                <h2>Community submitted explanations: {milestone}</h2>
                {onCloseAnnotations && (
                    <button
                        type="button"
                        className="annotations-close"
                        aria-label="Close annotations"
                        onClick={onCloseAnnotations}
                    >
                        x
                    </button>
                )}
            </div>
            {annotations.length === 0 && (
                <p className="annotations-empty">
                    No user-submitted annotations exist for this milestone yet.
                    Request one in the Ironscape Discord.
                </p>
            )}
            {annotations.map(annotation => (
                <Annotation
                    key={annotation.annotation_id}
                    annotation={annotation}
                />
            ))}
        </div>
    );
}
