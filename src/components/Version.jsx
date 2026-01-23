import count from '@data/contents/changelog.json';
import semver from 'semver';

export default function Version(){
    const latest = Object.keys(count).sort(semver.rcompare)[0];
    return <span id="page-count">{latest}</span>
}
