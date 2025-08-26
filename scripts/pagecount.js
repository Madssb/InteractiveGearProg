
async function initalizePageCount() {
try {
    const response = await(fetch('../data/generated/count.json'))
    if (!response.ok) {
      throw new Error(`Response status: ${response.status}`);
    }
    const result = await response.json();
    console.log(result);
    let pageCountDiv = document.getElementById("page-count");
    pageCountDiv.textContent = result["viewcountMonth"];
  } catch (error) {
    console.error(error.message);
  }
}
initalizePageCount();