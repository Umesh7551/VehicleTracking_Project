//  counter js

// JavaScript code to increment counters with different initial values
let counters = [0, 0, 0]; // Initial values
const stopValues = [15, 30, 40]; // Values to stop counting
let counterIntervals = []; // Array to store interval IDs

// Function to update a specific counter
function updateCounter(counterIndex) {
  if (counters[counterIndex] >= stopValues[counterIndex]) {
    clearInterval(counterIntervals[counterIndex]); // Stop the counting for the specific counter
  } else {
    counters[counterIndex]++;
    document.getElementById("counter" + (counterIndex + 1)).textContent = counters[counterIndex] + " + ";
  }
}
// Update counters independently
for (let i = 0; i < counters.length; i++) {
  counterIntervals[i] = setInterval(() => updateCounter(i), 30);
}



//    iframe js

let inputCount = 2; // Start with 2 input fields

function addInput() {
  inputCount++;

  // Create two new input elements
  for (let i = 0; i < 2; i++) {
    const input = document.createElement("input");
    input.type = "text";
    input.name = "Name" + inputCount + "" + (i + 1);
    input.placeholder = "Name " + inputCount + "" + (i + 1);

    // Create a container for the input
    const container = document.createElement("div");
    container.classList.add("input-container");
    container.appendChild(input);

    // Append the container to the dynamicInputs div
    document.getElementById("dynamicInputs").appendChild(container);
  }

  // Create a submit button
  const submitButton = document.createElement("button");
  submitButton.textContent = "Submit";
  submitButton.onclick = submitForm;

  // Append the submit button to the dynamicInputs div
  document.getElementById("dynamicInputs").appendChild(submitButton);
}

function removeInput() {
  const dynamicInputs = document.getElementById("dynamicInputs");

  // Check if there are input fields to remove
  if (inputCount > 2) { // Ensure at least 2 input fields are present
    // Remove the last three children (two input fields and one submit button)
    for (let i = 0; i < 3; i++) {
      dynamicInputs.removeChild(dynamicInputs.lastChild);
    }
    inputCount--;
  }
}

function submitForm() {
  // Implement your submit logic here
  alert("Form submitted!");
}



///////////////popover//////////////



function openpopup() {
  document.getElementById("popoverModel").style.display = "block"; 
}
function closepopup() {
  document.getElementById("popoverModel").style.display = "none";
}

function showpopup(){
  closepopup()
  document.getElementById("popupmodel").style.display = "block";
}

function hidepopup() {
  document.getElementById("popupmodel").style.display = "none";
}


// var modal = document.getElementById("popover"); 
// var btn = document.getElementById("redeem_btn");
// btn.onclick = function() {
//   modal.style.display = "block";
//   console.log("click");
// }
// Function to open the popover
// function showPopover() {
//   document.getElementById("popoverModel").style.display = "block";
// }

// // Function to close the popover
// function hidePopover() {
//   var popover = document.getElementById("popover");
//   popover.style.display = "none";
// }



// // Event listener for opening the popover
// document.getElementById("popoverButton").addEventListener("click", showPopover);

// // Event listener for closing the popover
// document.getElementById("closeButton").addEventListener("click", hidePopover);


