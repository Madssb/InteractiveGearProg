import '@/styles/Annotations.css';

export type AnnotationData = {
    annotation_id: number;
    up_count: number;
    down_count: number;
    chart_version: string;
    annotation_text: string;
    user_display_name: string;
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
                <div className="annotation-footer-item">by: {annotation.user_display_name}</div>
                <div className="annotation-footer-item">date: {annotation.created_at}</div>
                <div className="annotation-footer-item">version: {annotation.chart_version}</div>
                <div className="annotation-footer-item">annotation ID: {annotation.annotation_id}</div>
            </div>
        </div>
    );
}

type AnnotationsProps = {
    annotations: AnnotationData[];
    status?: 'idle' | 'loading' | 'loaded' | 'unavailable' | 'error';
    milestone: string;
    onCloseAnnotations?: () => void;
};

export default function Annotations({
    annotations,
    status = 'idle',
    onCloseAnnotations,
    milestone
}: AnnotationsProps) {
    const showEmpty = annotations.length === 0 && (status === 'idle' || status === 'loaded');

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
            {status === 'loading' && (
                <p className="annotations-status">Loading annotations...</p>
            )}
            {status === 'unavailable' && (
                <p className="annotations-status annotations-error">
                    Annotations are unavailable because the API is not configured for this build.
                </p>
            )}
            {status === 'error' && (
                <p className="annotations-status annotations-error">
                    Could not load annotations from the API.
                </p>
            )}
            {showEmpty && (
                <p className="annotations-empty">
                    No user-submitted annotations exist for this milestone yet.
                    Request one in the <a href="https://discord.gg/MzBPph3weE" className="href">Ladlorchart Community Discord</a>.
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
