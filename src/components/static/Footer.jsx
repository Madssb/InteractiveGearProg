import PageCount from '@/components/PageCount'
import Version from '@/components/Version'
import { Link } from 'react-router'

export default function Footer(){
    return (
        <>
            <footer>
                <p>
                <Version /> |{" "}
                <Link to="changelog">View Changelog</Link> |{" "}
                <Link to="privacy">Privacy Policy</Link> |{" "}
                <a href="https://github.com/Madssb/InteractiveGearProg">Source Code</a> |{" "}
                Monthly page visits: <span id="page-count"><PageCount /></span> |{" "}
                <Link to="customize">Chartbuilder</Link> |{" "}
                </p>
                <p>All images used in this tool are sourced from the{" "}
                    <a href="https://oldschool.runescape.wiki/" target="_blank">Old School RuneScape Wiki</a>,
                    and are licensed under the{" "}
                    <a href="https://creativecommons.org/licenses/by-nc-sa/3.0/" target="_blank">Creative Commons
                        Attribution-NonCommercial-ShareAlike 3.0 License</a>.
                    © 2013-2024 Jagex Ltd. All rights reserved.
                </p>
            </footer> 
        </>
    )
}
