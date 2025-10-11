import count from 'data/generated/count.json'

function PageCount(){
    let viewCount = count["viewCountMonth"]
    return <span id="page-count">{viewCount}</span>
}

export default PageCount