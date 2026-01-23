import count from '@data/generated/count.json'

export default function PageCount(){
    let viewCount = count["viewCountMonth"]
    return <span id="page-count">{viewCount}</span>
}
