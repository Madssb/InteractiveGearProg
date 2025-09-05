const SCRIPT_BASE = new URL('.', document.currentScript.src);
const BANK_URL = new URL('../data/bank.json', SCRIPT_BASE);


/* Loads data/bank.json */
async function getBankJson(){
  try {
    const res = await fetch(BANK_URL);
    if (!res.ok) return null;
    const data = await res.json();
    return data;
  } catch {
    return null;
  }
}

/*
Populates the bank-header div header elements that contain relevant img srces as outlined in the
header part of bank.json
*/
async function buildBankHeader(){
    const bankHeader = document.getElementById("bank-header");
    if (!bankHeader) {
        console.error("No element with ID 'bank-header' found.");
        return Promise.reject("Bank header not found");
    }
    const bankJson = await getBankJson();
    let headerElementCornerDiv1 = document.createElement("div")
    headerElementCornerDiv1.classList.add("header-corner")
    bankHeader.appendChild(headerElementCornerDiv1);
    for (const [key, item] of Object.entries(bankJson["header"])) {
        let headerElementDiv = document.createElement("div");
        headerElementDiv.id = `header-element-${key}`
        headerElementDiv.classList.add("header-element");
        let img = document.createElement("img");
        img.src = item;
        headerElementDiv.appendChild(img);
        bankHeader.appendChild(headerElementDiv);
    }
    let headerElementCornerDiv2 = document.createElement("div")
    headerElementCornerDiv2.classList.add("header-corner")
    bankHeader.appendChild(headerElementCornerDiv2);
}

/* 
Instantiates active header element id from localStorage or the zero-th header element if none found
*/
async function initializeActiveHeaderElement(){
    if (document.getElementsByClassName("active").length > 1) {
        /* More than one active header elements is a bug*/
        console.error("more than one active header elements detected")
        localStorage.setItem("active-header-element-id")
        return;
    }
    if (document.getElementsByClassName("active").length == 1) {
        /* a single active element already exists, no need to instantiate one.*/
        console.log("active header elements detected")
        return;
    }
    /* */
    let activeHeaderElementID = localStorage.getItem("active-header-element-id");
    if (!activeHeaderElementID) {
        activeHeaderElementID = "header-element-0";
    }
    let activeHeaderElementDiv = document.getElementById(activeHeaderElementID); 
    activeHeaderElementDiv.classList.add("active")
}

/* 
Updates the active header element div by removing class from previously active
header element div, adding it to the new activeo ne, and updating the local storage too.
*/
async function updateActiveHeaderElementDiv(newActiveHeaderElementDiv){
    const bankHeader = document.getElementById("bank-header");
    if (!bankHeader) {
        console.error("No element with ID 'bank-header' found.");
        return Promise.reject("Bank header not found");
    }
    /* previously active header element is being replaced by new active */
    let oldActiveHeaderElementDiv = document.getElementsByClassName("active").item(0);
    oldActiveHeaderElementDiv.classList.remove("active");
    
    newActiveHeaderElementDiv.classList.add("active");
    localStorage.setItem("active-header-element-id", newActiveHeaderElementDiv.id);
}

async function initializeClickListening(){
    const bankHeader = document.getElementById("bank-header");
    if (!bankHeader) {
        console.error("No element with ID 'bank-header' found.");
        return Promise.reject("Bank header not found");
    }
    bankHeader.addEventListener("click", (event) => {
        let headerElementDiv = event.target.closest(".header-element");
        if (!headerElementDiv) return;
        console.log(headerElementDiv.id);
    }) 
}



async function main(){
    await buildBankHeader();
    await initializeActiveHeaderElement();
    await initializeClickListening();
}

main();