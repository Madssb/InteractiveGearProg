const SCRIPT_BASE = new URL('.', document.currentScript.src);
const INVOS_URL = new URL('../data/invocations.json', SCRIPT_BASE);


/* Loads data/bank.json */
async function getInvosJson(){
  try {
    const res = await fetch(INVOS_URL);
    if (!res.ok) return null;
    const data = await res.json();
    return data;
  } catch {
    return null;
  }
}

async function buildPanel(){
    const panelDiv = document.getElementById("panel");
    if (!panelDiv) {
        console.error("No element with ID 'panel' found.");
        return Promise.reject("Bank header not found");
    }
    let invosJson = await getInvosJson();
    for (const [key, item] of Object.entries(invosJson)){
        /* Instantiate invocation container*/
        let invocationContainerDiv = document.createElement("div");
        invocationContainerDiv.classList.add("invocation-container")
        let img = document.createElement("img");
        img.src = item["imgUrl"];
        let span =  document.createElement("span");
        span.textContent = key;
        invocationContainerDiv.appendChild(img);
        invocationContainerDiv.appendChild(span);
        panelDiv.appendChild(invocationContainerDiv);
    }
}


/* handle raid level input, normalizing by rounding down to nearest threshold */
function raidLevelParser() {
    // Get the value of the input field with id="numb"
    let raidLevel = document.getElementById("raidLevel").value;
    // If raidLevel is Not a Number or less than one or greater than 10
    let text;
    if (isNaN(raidLevel) || raidLevel < 150 || raidLevel > 400) {
        text = "Input not valid";
        } else {
        text = "Input OK";
    }
    let thresholds = [
        150, 165, 185, 200, 215, 230, 250, 265, 275, 290,
        300, 300, 315, 325, 340, 350, 350, 365, 365, 380,
        390, 400
    ];
    if (thresholds.includes(raidLevel)){
        roundedRaidLvl = raidLevel;
    } else {
        
    }
    document.getElementById("demo").innerHTML = text;
}


async function main() {
    buildPanel();
    raidLevelParser();
}
main();