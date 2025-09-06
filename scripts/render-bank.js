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
Populates the bank-tabs-section div header elements that contain relevant img srces as outlined in the
header part of bank.json
*/
async function buildBankTabsSection(){
    const bankTabsSectionDiv = document.getElementById("bank-tabs-section");
    if (!bankTabsSectionDiv) {
        console.error("No element with ID 'bank-tabs-section' found.");
        return Promise.reject("Bank header not found");
    }
    const bankJson = await getBankJson();
    let bankTabsCornerDiv1 = document.createElement("div")
    bankTabsCornerDiv1.classList.add("bank-tabs-corner")
    bankTabsSectionDiv.appendChild(bankTabsCornerDiv1);
    for (const [key, item] of Object.entries(bankJson["header"])) {
        /* Instantiate bank tab button div */ 
        let bankTabButtonDiv = document.createElement("div");
        bankTabButtonDiv.classList.add("bank-tab-button");
        /* Instantiate img element */
        let img = document.createElement("img");
        img.src = item;
        bankTabButtonDiv.appendChild(img);
        bankTabButtonDiv.id = `bank-tab-${key}`;
        bankTabsSectionDiv.appendChild(bankTabButtonDiv);
    }
    let bankTabsCornerDiv2 = document.createElement("div")
    bankTabsCornerDiv2.classList.add("bank-tabs-corner")
    bankTabsSectionDiv.appendChild(bankTabsCornerDiv2);
}

/* 
Instantiates active header element id from localStorage or the zero-th header element if none found
*/
async function initializeActiveHeaderElement(){
    if (document.getElementsByClassName("active").length > 2) {
        /* More than one active header elements is a bug*/
        console.error("more than one active header elements detected")
        localStorage.setItem("active-bank-tab-id", "0")
        return;
    }
    if (document.getElementsByClassName("active").length == 2) {
        /* a single active element already exists, no need to instantiate one.*/
        console.log("active header elements detected")
        return;
    }
    /* */
    let activeBankTabID = localStorage.getItem("active-bank-tab-id");
    if (!activeBankTabID) {
        activeBankTabID = "0";
    }
    let activeBankTabButtonDiv = document.getElementById(`bank-tab-${activeBankTabID}`);
    activeBankTabButtonDiv.classList.add("active");
}

/* 
Updates the active header element div by removing class from previously active
header element div, adding it to the new activeo ne, and updating the local storage too.
*/
async function updateActiveHeaderElementDiv(newActiveHeaderElementDiv){
    const bankHeader = document.getElementById("bank-tabs-section");
    if (!bankHeader) {
        console.error("No element with ID 'bank-tabs-section' found.");
        return Promise.reject("Bank header not found");
    }
    /* previously active header element is being replaced by new active */
    let oldActiveHeaderElementDiv = document.getElementsByClassName("active").item(0);
    oldActiveHeaderElementDiv.classList.remove("active");
    
    newActiveHeaderElementDiv.classList.add("active");
    localStorage.setItem("active-bank-tag-id", newActiveHeaderElementDiv.id);
}

async function initializeClickListening(){
    const bankHeader = document.getElementById("bank-tabs-section");
    if (!bankHeader) {
        console.error("No element with ID 'bank-tabs-section' found.");
        return Promise.reject("Bank header not found");
    }
    bankHeader.addEventListener("click", (event) => {
        let headerElementDiv = event.target.closest(".header-element");
        if (!headerElementDiv) return;
        console.log(headerElementDiv.id);
        updateActiveHeaderElementDiv(headerElementDiv);
    }) 
}


async function main(){
    await buildBankTabsSection();
    await initializeActiveHeaderElement();
    await initializeClickListening();
}

main();