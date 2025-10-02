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

async function buildPanel() {
    const panelDiv = document.getElementById("panel");
    if (!panelDiv) return;

    const invosJson = await getInvosJson();
    const fragment = document.createDocumentFragment();

    for (const [key, item] of Object.entries(invosJson)) {
        const div = document.createElement("div");
        div.classList.add("invocation-container");

        const img = document.createElement("img");
        img.src = item.imgUrl;
        img.loading = "lazy"; // hint to browser

        const span = document.createElement("span");
        span.textContent = key;

        div.append(img, span);

        for (const enabled of item.enabledOn) {
            div.classList.add(String(enabled));
        }

        fragment.appendChild(div);
    }

    panelDiv.appendChild(fragment);
}


/* handle raid level input, normalizing by rounding down to nearest threshold */
function raidLevelParser() {
    let raidLevel = Number(document.getElementById("raidLevel").value);
    let thresholds = [
        150, 165, 185, 200, 215, 230, 250, 265, 275, 290,
        300, 315, 325, 340, 350, 365, 380, 390, 400
    ];
    let roundedRaidLvl;
    if (thresholds.includes(raidLevel)){
        roundedRaidLvl = raidLevel;
    } else {
        for (let i = 0; i < thresholds.length; i++) { 
            if (thresholds[i] > raidLevel) {
                roundedRaidLvl = thresholds[i-1];
                document.getElementById("demo").innerHTML = `Raid level: ${roundedRaidLvl}`;
                break;
            }
        }
    }
    const elements1 = document.getElementsByClassName("invocation-container")
    for (const el1 of elements1){
        el1.classList.remove("active");
    }
    const elements = document.getElementsByClassName(String(roundedRaidLvl));
    for (const el of elements) {
        el.classList.add("active");
    }
}


async function main() {
    buildPanel();   
}
main();