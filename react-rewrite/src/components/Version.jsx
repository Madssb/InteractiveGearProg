import count from 'data/changelog.json';
import semver from 'semver';

function Version(){
    const latest = Object.keys(count).sort(semver.rcompare)[0];
    return <span id="page-count">{latest}</span>
}

export default Version