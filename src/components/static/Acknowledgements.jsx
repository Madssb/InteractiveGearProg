import '@/styles/acknowledgements.css'

export default function Acknowledgements(){
    return (
        <>
            <div className="acknowledgements">
            <h2>Acknowledgements</h2>
            <p>
                A special thank you to the <a href="https://discord.gg/ironscape" target="_blank">Ironscape Discord
                    Community</a> for their support and contributions in refining the sequencing of milestones. I would like to
                acknowledge the following members for their invaluable efforts (in no particular order):
            </p>
            <ul>
                <li>
                    <strong>Parasailer</strong>: Author of <em>Parasailer's Gear Progression Chart</em> and co-author of{" "}
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
