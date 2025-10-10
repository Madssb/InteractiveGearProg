import Chart from 'components/chart.jsx';
import PageCount from 'components/PageCount.jsx';
import Version from 'components/Version.jsx';

function Acknowledgements(){
    return (
        <>
            <div class="acknowledgements">
            <h2>Acknowledgements</h2>
            <p>
                A special thank you to the <a href="https://discord.gg/ironscape" target="_blank">Ironscape Discord
                    Community</a> for their support and contributions in refining the sequencing of milestones. I would like to
                acknowledge the following members for their invaluable efforts (in no particular order):
            </p>
            <ul>
                <li>
                    <strong>Parasailer</strong>: Author of <em>Parasailer's Gear Progression Chart</em> and co-author of
                    <em><a href="https://docs.google.com/document/d/1CBkFM70SnrW4hJXvHM2F1fYCuBF_fRnEXnTYgRnRkAE/edit?usp=sharing">BRUHSailer</a></em>, the comprehensive Ironman account progression guide. <br /> The current gear progression
                    sequence is largely based on the aforementioned chart, and by extension, <em>BRUHSailer</em>.
                </li>
                <li>
                    <strong>So Iron Bruh</strong>: Provided quality assurance and co-authored <em>BRUHSailer</em>.
                </li>

                <li>
                    <strong>Drøgøn</strong>: Provided quality assurance and contributed extensive theorycrafting for new metas.
                </li>

                <li>
                    <strong>Raze</strong>: Assisted with quality assurance.
                </li>
                <li>
                    <strong>Wolf</strong>: Provided insight into accounting for ancient shards.
                </li>
            </ul>
            </div>
        </>
    )
}

function FAQSection(){
    return (
        <>
            <div class="faq-section">
                <p><strong>Q:</strong> What item is this?</p>
                <p><strong>A:</strong> You can right click the item, which shows a menu displaying the name. Additionaly you can
                    navigate to the corresponding OSRS wiki page from this menu.</p>
                <p><strong>Q:</strong> How is my progress saved?</p>
                <p><strong>A:</strong> Your progress is saved using local storage in your browser. It will remain intact even if
                    you refresh or close the page.</p>
                <p><strong>Q:</strong> Does a pvm-focused version exist?</p>
                <p><strong>A:</strong> Yes! A "bare bones" version can be found <a href="pages/bare-bones.html">here</a>.</p>
                <p>For more questions, visit the <link to="faq">full FAQ page</link>.</p>
            </div>
        </>
    )
}

function Footer(){
    return (
        <>
            <footer>
                <p>
                <Version /> |
                <link to="changelog">View Changelog</link> |
                <a href="pages/privacy.html">Privacy Policy</a> |
                <a href="https://github.com/Madssb/InteractiveGearProg">Source Code</a> |
                Monthly page visits: <span id="page-count"><PageCount /></span>
                </p>
                <p>All images used in this tool are sourced from the
                    <a href="https://oldschool.runescape.wiki/" target="_blank">Old School RuneScape Wiki</a>,
                    and are licensed under the
                    <a href="https://creativecommons.org/licenses/by-nc-sa/3.0/" target="_blank">Creative Commons
                        Attribution-NonCommercial-ShareAlike 3.0 License</a>.
                    © 2013–2024 Jagex Ltd. All rights reserved.
                </p>
            </footer> 
        </>
    )
}


function ChartPage(){
    return (
        <>
            <h1>Interactive Ironman Progression Chart</h1>
            <span class="subtitle">Curated by the Ironscape community — made by Ladlor</span>  
            <Chart />
            <Acknowledgements />
            <FAQSection />
        </>
    )
}
export default ChartPage