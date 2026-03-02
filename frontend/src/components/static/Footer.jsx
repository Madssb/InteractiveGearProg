import PageCount from '@/components/PageCount'
import Version from '@/components/Version'
import { Link, useLocation } from 'react-router'

export default function Footer({ showImageAttribution = false }){
    const location = useLocation();
    const normalizedPath = location.pathname === '/index.html' ? '/' : location.pathname;
    const navLinks = [
        { to: '/', label: 'Home' },
        { to: '/chartbuilder', label: 'Chart Builder' },
        { to: '/faq', label: 'FAQ' },
        { to: '/changelog', label: 'View Changelog' },
        { to: '/privacy', label: 'Privacy Policy' }
    ].filter(link => link.to !== normalizedPath);

    return (
        <>
            <footer>
                <p>
                <Version /> |{" "}
                {navLinks.map((link) => (
                    <span key={link.to}>
                        <Link to={link.to}>{link.label}</Link>
                        {" | "}
                    </span>
                ))}
                <a href="https://github.com/Madssb/InteractiveGearProg">Source Code</a> |{" "}
                Monthly page visits: <span id="page-count"><PageCount /></span> |{" "}
                </p>
                {showImageAttribution && (
                    <p>All images used in this tool are sourced from the{" "}
                        <a href="https://oldschool.runescape.wiki/" target="_blank">Old School RuneScape Wiki</a>,
                        and are licensed under the{" "}
                        <a href="https://creativecommons.org/licenses/by-nc-sa/3.0/" target="_blank">Creative Commons
                            Attribution-NonCommercial-ShareAlike 3.0 License</a>.
                        © 2013-2024 Jagex Ltd. All rights reserved.
                    </p>
                )}
            </footer> 
        </>
    )
}
