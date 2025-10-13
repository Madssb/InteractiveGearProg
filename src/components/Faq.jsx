import '@/styles/faq.css';
import faq from '@data/faq.json';

export default function Faq(){
    let questions = Object.keys(faq);
    return (
        <>
        <dl className="faq">
            {questions.map(
                (question) => (
                    <>
                    <dt className='question'>{question}</dt>
                    <dd className='answer'>{faq[question]}</dd>
                    </>
                )
            )}
        </dl>
        </>
    )
}
