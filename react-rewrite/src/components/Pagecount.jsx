import count from 'data/generated/count.json'

function PageCount(){
    return <span id="page-count">{count["viewCountMonth"]}</span>
}