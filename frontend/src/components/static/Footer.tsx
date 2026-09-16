import Version from '@/components/Version';
import { Link, useLocation } from 'react-router';
import { apiUrl } from '@/utils/apiConfig';
import React from 'react';

interface FooterProps {
    /** Viewcount */
    viewCount: number;
    /** True if gives image attribution, false if not. */
    showImageAttribution: boolean;
}

// get viewcount from localstorage, or fetch from backend api once per day
async function getViewCount() {
    const VIEWCOUNT_DATE_KEY = "viewCountFetchDate"
    const VIEWCOUNT_KEY = "viewCount"
    // make date string for today
    const date = new Date()
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    const today = `${year}-${month}-${day}`;
    
    // make a maximum of one viewcount get request per day
    if (localStorage.getItem(VIEWCOUNT_DATE_KEY) === today) {
        const viewCount = localStorage.getItem(VIEWCOUNT_KEY);
        if (!viewCount) throw new Error("viewcount get request made today, but viewcount not found.")
        return viewCount;
    }
    const url = apiUrl("/milestones-completed-count?num_days=31")
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error('Response status: ${response.status}');
        const viewCount = await response.json();
        localStorage.setItem(VIEWCOUNT_KEY, viewCount);
        localStorage.setItem(VIEWCOUNT_DATE_KEY, today);
        return viewCount;
    } catch(err) {
        console.log(err);
    }
}

export default function Footer({ showImageAttribution = false }: FooterProps) {
    const location = useLocation();
    const normalizedPath = location.pathname === '/index.html' ? '/' : location.pathname;
    const navLinks = [
        { to: '/', label: 'Home' },
        { to: '/chartbuilder', label: 'Chart Builder' },
        // { to: '/bank', label: 'Bank' },
        { to: '/faq', label: 'FAQ' },
        { to: '/changelog', label: 'View Changelog' },
        { to: '/privacy', label: 'Privacy Policy' }
    ].filter(link => link.to !== normalizedPath);
    
    const [viewCount, setViewCount] = React.useState(null);
    React.useEffect(() => {
        const loadViewCount = async () => {
            const viewCount_ = await getViewCount();
            setViewCount(viewCount_);
        }
        loadViewCount();
    }, [])
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
                    <a href="https://discord.gg/MzBPph3weE" className="href">Discord</a> |{" "}
                    <a href="https://www.paypal.com/ncp/payment/3WEM322C3CG5E" target="_blank" rel="noopener noreferrer">Donate</a> |{" "}
                    <span id="page-count">{viewCount}</span> chart visits
                </p>
                {showImageAttribution && (
                    <p>Some images used in the config menu of this tool are sourced from the{" "}
                        <a href="https://oldschool.runescape.wiki/" target="_blank">Old School RuneScape Wiki</a>,
                        and are licensed under the{" "}
                        <a href="https://creativecommons.org/licenses/by-nc-sa/3.0/" target="_blank">Creative Commons
                            Attribution-NonCommercial-ShareAlike 3.0 License</a>.
                        © 2013-2026 Jagex Ltd. All rights reserved.
                    </p>
                )}
            </footer>
        </>
    )
}
