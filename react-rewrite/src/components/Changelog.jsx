import changelog from 'data/changelog.json';
import React from 'react';
function Changelog(){
    let versions = Object.keys(changelog)
    return(
        <>
            <div id='changelog'>
                <h1>Changelog</h1>
                {
                    versions.map(
                        (version) => (
                            <ChangelogEntry
                                version={version}
                                key={version}
                                />
                        )
                    )
                }
            </div>
        </>
    )
}

function ChangelogEntry( {version} ){
    let changes = changelog[version];
    return(
        <>
            <h2>Version {version}</h2>
            <ul>
                {changes.map(
                    (change) => (
                        <React.Fragment
                            key={change}
                        >
                            <li>{change}</li>
                        </React.Fragment>
                    )
                )}
            </ul>
        </>
    )
}

export default Changelog