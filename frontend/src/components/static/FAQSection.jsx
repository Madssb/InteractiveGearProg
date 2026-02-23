import { Link } from 'react-router'

export default function FAQSection(){
    return (
        <>
            <div className="faq-section">
                <p><strong>Q:</strong> What item is this?</p>
                <p><strong>A:</strong> You can right click the item, which shows a menu displaying the name. Additionaly you can
                    navigate to the corresponding OSRS wiki page from this menu.</p>
                <p><strong>Q:</strong> How is my progress saved?</p>
                <p><strong>A:</strong> Your progress is saved using local storage in your browser. It will remain intact even if
                    you refresh or close the page.</p>
                <p>For more questions, visit the <Link to="/faq">full FAQ page</Link>.</p>
            </div>
        </>
    )
}
