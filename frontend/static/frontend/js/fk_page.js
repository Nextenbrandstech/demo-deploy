
// Track sorting order for each column
const sortOrder = {};

let dynamicPlots = {}; // Store all plots globally

document.addEventListener("DOMContentLoaded", function () {
  const defaultStartDate = "2025-01-01";
  const defaultEndDate = "2025-01-03";

  document.getElementById("start-date").value = defaultStartDate;
  document.getElementById("end-date").value = defaultEndDate;

  document.getElementById("pnl-start-date").value = defaultStartDate;
  document.getElementById("pnl-end-date").value = defaultEndDate;
  document.getElementById("pnl-time-slicer").value = "week";

  const seller = "TRI"; // Default seller was "All Seller"
  const brand = "";
  document.getElementById("seller-slicer").value = seller;

  // Ensure brand dropdown is populated before setting value
  updateBrands();
  setTimeout(() => {
    document.getElementById("brand-slicer").value = brand;
  }, 100);  // Small delay ensures dropdown is populated

  const gmvCheckbox = document.querySelector(".dropdown-menu input[value='gmv']");
  if (gmvCheckbox) gmvCheckbox.checked = true;

  fetchInsights(defaultStartDate, defaultEndDate, seller, brand);
  fetchPnLData();
  updatePlots(["gmv"]);

  attachDropdownEventListeners();
});


// Existing sorting function (unchanged)
function sortTable(columnIndex, columnName, tableName) {
  sortOrder[columnName] = !sortOrder[columnName];
  const table = document.getElementById(tableName);
  const rows = Array.from(
    table.getElementsByTagName("tbody")[0].getElementsByTagName("tr")
  );

  rows.sort((a, b) => {
    const cellA = a.getElementsByTagName("td")[columnIndex].textContent || "";
    const cellB = b.getElementsByTagName("td")[columnIndex].textContent || "";

    const valueA = isNaN(parseFloat(cellA))
      ? cellA.toLowerCase()
      : parseFloat(cellA);
    const valueB = isNaN(parseFloat(cellB))
      ? cellB.toLowerCase()
      : parseFloat(cellB);

    if (valueA < valueB) return sortOrder[columnName] ? -1 : 1;
    if (valueA > valueB) return sortOrder[columnName] ? 1 : -1;
    return 0;
  });

  const tbody = table.getElementsByTagName("tbody")[0];
  tbody.innerHTML = "";
  rows.forEach((row) => tbody.appendChild(row));

  highlightActiveArrow(columnName, sortOrder[columnName]);
}

function highlightActiveArrow(activeColumn, isAscending) {
  document.querySelectorAll(".sort-icons span").forEach((arrow) => {
    arrow.classList.remove("active");
  });

  const activeArrow = document.getElementById(
    isAscending ? `${activeColumn}-up` : `${activeColumn}-down`
  );
  if (activeArrow) {
    activeArrow.classList.add("active");
  }
}

function searchTable(tableId, inputId) {
  const searchInput = document.getElementById(inputId).value.toLowerCase();
  const table = document.getElementById(tableId);
  const rows = table
    .getElementsByTagName("tbody")[0]
    .getElementsByTagName("tr");

  for (let i = 0; i < rows.length; i++) {
    const productTitleCell = rows[i].getElementsByTagName("td")[1];
    if (productTitleCell) {
      const productTitle =
        productTitleCell.textContent || productTitleCell.innerText;

      if (productTitle.toLowerCase().indexOf(searchInput) > -1) {
        rows[i].style.display = "";
      } else {
        rows[i].style.display = "none";
      }
    }
  }
}


function applyReturnFilter() {
  const filter = document.getElementById("return-category-slicer").value;
  const returnTableBody = document.querySelector("#return-consolidated-data-table tbody");
  returnTableBody.innerHTML = ""; // Clear existing rows

  // Get data for the second table
  const data = window.secondTableData || {}; // Assuming `secondTableData` is global

  if (filter === "return_product" && data.hasOwnProperty("sales_by_title") &&
    data.hasOwnProperty("return_by_title") &&
    data.hasOwnProperty("cancellation_by_title") &&
    data.hasOwnProperty("net_sales_by_title")) {

    // Club data by product_sku
    const clubbedData = {};
    const keys = ['sales_by_title', 'return_by_title', 'cancellation_by_title', 'net_sales_by_title'];

    keys.forEach((key) => {
      if (Array.isArray(data[key])) {
        data[key].forEach((item) => {
          const sku = item.sku || "Unknown";
          if (!clubbedData[sku]) {
            clubbedData[sku] = {
              sku: sku,
              consolidated_product_title: item.consolidated_product_title || "N/A",
              gmv: 0,
              qty: 0,
              returned_gmv: 0,
              returned_qty: 0,
              cancelled_gmv: 0,
              cancelled_qty: 0,
              net_gmv: 0,
              net_qty: 0
            };
          }
          if (key === 'sales_by_title') {
            clubbedData[sku].gmv += item.gmv || 0;
            clubbedData[sku].qty += item.qty || 0;
          } else if (key === 'return_by_title') {
            clubbedData[sku].returned_gmv += item.returned_gmv || 0;
            clubbedData[sku].returned_qty += item.returned_qty || 0;
          } else if (key === 'cancellation_by_title') {
            clubbedData[sku].cancelled_gmv += item.cancelled_gmv || 0;
            clubbedData[sku].cancelled_qty += item.cancelled_qty || 0;
          } else if (key == 'net_sales_by_title') {
            clubbedData[sku].net_gmv += item.net_gmv || 0;
            clubbedData[sku].net_qty += item.net_qty || 0;
          }
        });
      }
    });

    // Populate table
    Object.values(clubbedData).forEach((product) => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${product.sku}</td>
        <td>${product.consolidated_product_title}</td>
        <td>${product.gmv}</td>
        <td>${product.qty}</td>
        <td>${product.returned_gmv}</td>
        <td>${product.returned_qty}</td>
        <td>${product.cancelled_gmv}</td>
        <td>${product.cancelled_qty}</td>
        <td>${product.net_gmv}</td>
        <td>${product.net_qty}</td>
      `;
      returnTableBody.appendChild(row);
    });

  } else if (filter === "return_vertical" && data.hasOwnProperty("sales_by_vertical") &&
    data.hasOwnProperty("return_by_vertical") &&
    data.hasOwnProperty("cancellation_by_vertical") &&
    data.hasOwnProperty("net_sales_by_vertical")) {

    // Club data by vertical
    const clubbedData = {};
    const keys = ['sales_by_vertical', 'return_by_vertical', 'cancellation_by_vertical', 'net_sales_by_vertical'];

    keys.forEach((key) => {
      if (Array.isArray(data[key])) {
        data[key].forEach((item) => {
          const vertical = item.vertical || "Unknown";
          if (!clubbedData[vertical]) {
            clubbedData[vertical] = {
              vertical: vertical,
              vertical_gmv: 0,
              vertical_qty: 0,
              returned_vertical_gmv: 0,
              returned_vertical_qty: 0,
              cancelled_vertical_gmv: 0,
              cancelled_vertical_qty: 0,
              net_vertical_gmv: 0,
              net_vertical_qty: 0
            };
          }
          if (key === 'sales_by_vertical') {
            clubbedData[vertical].vertical_gmv += item.vertical_gmv || 0;
            clubbedData[vertical].vertical_qty += item.vertical_qty || 0;
          } else if (key === 'return_by_vertical') {
            clubbedData[vertical].returned_vertical_gmv += item.returned_vertical_gmv || 0;
            clubbedData[vertical].returned_vertical_qty += item.returned_vertical_qty || 0;
          } else if (key === 'cancellation_by_vertical') {
            clubbedData[vertical].cancelled_vertical_gmv += item.cancelled_vertical_gmv || 0;
            clubbedData[vertical].cancelled_vertical_qty += item.cancelled_vertical_qty || 0;
          } else if (key == 'net_sales_by_vertical') {
            clubbedData[vertical].net_vertical_gmv += item.net_vertical_gmv || 0;
            clubbedData[vertical].net_vertical_qty += item.net_vertical_qty || 0;
          }
        });
      }
    });

    // Populate table
    Object.values(clubbedData).forEach((vertical) => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>N/A</td>
        <td>${vertical.vertical}</td>
        <td>${vertical.vertical_gmv}</td>
        <td>${vertical.vertical_qty}</td>
        <td>${vertical.returned_vertical_gmv}</td>
        <td>${vertical.returned_vertical_qty}</td>
        <td>${vertical.cancelled_vertical_gmv}</td>
        <td>${vertical.cancelled_vertical_qty}</td>
        <td>${vertical.net_vertical_gmv}</td>
        <td>${vertical.net_vertical_qty}</td>
      `;
      returnTableBody.appendChild(row);
    });

  } else {
    // No data available case
    const row = document.createElement("tr");
    row.innerHTML = `<td colspan="8" class="text-center">No data available</td>`;
    returnTableBody.appendChild(row);
  }
}


// This function is for the predefined dates selection
function updateDateRangeAndFetch() {

  const selector = document.getElementById("date-range-selector").value;
  const today = new Date();
  const startDateInput = document.getElementById("start-date");
  const endDateInput = document.getElementById("end-date");

  let startDate, endDate;

  if (selector === 'today') {
    startDate = new Date(today);
    endDate = new Date(today);
  }
  else if (selector == 'yesterday') {
    startDate = new Date(today);
    endDate = new Date(today);

    startDate.setDate(today.getDate() - 1);
    endDate.setDate(today.getDate() - 1);
  }
  else if (selector === "last7days") {
    endDate = new Date(today);
    startDate = new Date(today);
    startDate.setDate(today.getDate() - 7);
  }
  else if (selector === "last15days") {
    endDate = new Date(today);
    startDate = new Date(today);
    startDate.setDate(today.getDate() - 15);
  }
  else if (selector === "last30days") {
    endDate = new Date(today);
    startDate = new Date(today);
    startDate.setMonth(today.getMonth() - 1);
  }
  else if (selector === "last90days") {
    endDate = new Date(today);
    startDate = new Date(today);
    startDate.setDate(today.getDate() - 90);
  }
  else {
    console.log("No valid selection");
    return;
  }

  const formatDate = (date) => date.toISOString().split("T")[0];
  startDateInput.value = formatDate(startDate);
  endDateInput.value = formatDate(endDate);

  // Trigger fetch to backend
  fetchInsightsFromInputs();
}

function fetchInsightsFromInputs() {
  const startDate = document.getElementById("start-date").value;
  const endDate = document.getElementById("end-date").value;
  const seller = document.getElementById("seller-slicer").value;
  const brand = document.getElementById("brand-slicer").value;
  console.log("brand slicer is triggered by the change of pre-defined date: ", brand);

  console.log("Fetching insights for:", { startDate, endDate, seller, brand });

  if (startDate && endDate) {
    fetchInsights(startDate, endDate, seller, brand);
  } else {
    alert("Please select both start and end dates.");
  }
}

// ────────────────────────────────────────────────────────────
// MAIN fetchInsights: Now also sends current_date_range + previous_date_range
// ────────────────────────────────────────────────────────────
function fetchInsights(startDate, endDate, seller, brand) {

  // Attach them to the existing URL
  const url = `/backend/api/fk_insights/?start_date=${startDate}` +
    `&end_date=${endDate}&seller=${seller}&brand=${brand}`;


  fetch(url)
    .then((response) => response.json())
    .then((data) => {

      // console.log("The link has been fetched !!!", data)

      const container = document.getElementById("insights-cards");
      container.innerHTML = "";

      // Define which keys should have a "%" appended.
      const percentKeys = new Set([
        "shopsy_contribution",
        "fbf_contribution",
        "rto_percent",
        "rtv_percent",
        "misc_return_percent"
      ]);

      // Keys for individual cards (excluding the return summary keys)
      const keysToDisplayInCards = [
        "gross_revenue",
        "gross_units",
        "ads_spend",
        "cancellation_amt",
        "cancellation_units",
        "cpc",
        "returned_amt",
        "returned_units",
        "cvr",
        "net_revenue",
        "net_units",
        "roas",
        "shopsy_contribution",
        "fbf_contribution"
      ];

      keysToDisplayInCards.forEach((key) => {
        const displayKey = `display_${key}`;
        const percentageChangeKey = `percent_change_${key}`;
        let cardValue = data[displayKey];
        const percentageChange = data[percentageChangeKey];

        if (cardValue !== undefined) {
          // Append "%" only if the key is in the allowed list.
          if (percentKeys.has(key)) {
            cardValue = `${cardValue}%`;
          }

          const card = document.createElement("div");
          card.classList.add("col-md-4");

          let percentageHTML = "";
          // Only add percent change if available for these cards.
          if (percentageChange !== undefined && percentageChange !== null) {
            const isIncrease = percentageChange > 0;
            const changeColor = isIncrease ? "text-success" : "text-danger";
            const changeSymbol = isIncrease ? "↑" : "↓";
            percentageHTML = `
        <span class="${changeColor}" style="font-size: 0.9rem; font-weight: bold;">
          ${changeSymbol} ${Math.abs(percentageChange).toFixed(2)}%
        </span>
      `;
          }

          card.innerHTML = `
      <div class="card shadow-sm">
        <div class="card-body">
          <h5 class="card-title">${key.replace("_", " ").toUpperCase()}</h5>
          <p class="card-text d-flex align-items-center" style="gap: 8px; margin: 0;">
            <span>${cardValue}</span>
            ${percentageHTML}
          </p>
        </div>
      </div>
    `;
          container.appendChild(card);
        }
      });

      // Build a single "Return Summary" card for rto, rtv, and miscellaneous_return.

      const returnKeys = [
        "rto_percent",
        "rtv_percent",
        "misc_return_percent",
        "rto_return",
        "rtv_return",
        "misc_return"
      ];

      let column1HTML = "";
      let column2HTML = "";

      // Loop through each return key and split into two columns
      returnKeys.forEach((key, index) => {
        const displayKey = `display_${key}`;
        let cardValue = data[displayKey];

        if (cardValue !== undefined) {
          // Add % sign for percent keys
          if (key.includes("percent")) {
            cardValue = `${cardValue}%`;
          }

          const itemHTML = `
        <div style="display: flex; justify-content: space-between; margin-bottom: -5px; font-size: 0.75rem;">
          <span style="font-weight: bold; margin-right: 8px;">${key.toUpperCase()}</span>
          <span>${cardValue}</span>
        </div>
      `;

          if (index < 3) {
            column1HTML += itemHTML;
          } else {
            column2HTML += itemHTML;
          }
        }
      });

      // Combine into a single returnCardHTML
      const returnCardHTML = `
    <div style="display: flex; justify-content: space-between; gap: 30px; padding-top: 3px;">
      <div style="flex: 1;">
        ${column1HTML}
      </div>
      <div style="flex: 1;">
        ${column2HTML}
      </div>
    </div>
  `;

      // Add to card if anything exists
      if (column1HTML || column2HTML) {
        const card = document.createElement("div");
        card.classList.add("col-md-4");

        card.innerHTML = `
      <div class="card shadow-sm">
        <div class="card-body">
          <h5 class="card-title">RETURN SUMMARY</h5>
          <div class="card-text">
            ${returnCardHTML}
          </div>
        </div>
      </div>
    `;

        container.appendChild(card);
      }



      // Store all plots globally
      dynamicPlots = data.dynamic_plot?.dynamic_plot || {};

      // Get selected metrics from checkboxes and update plots (This is for trend lines in the plots)
      const selectedMetrics = Array.from(
        document.querySelectorAll(".dropdown-menu input[type='checkbox']:checked")
      ).map((checkbox) => checkbox.value);

      updatePlots(selectedMetrics); // Render plots for selected metrics


      // Populate the demographic plot
      const demographicplot = JSON.parse(data.demographic_plot);
      Plotly.newPlot("demographic-plot", demographicplot.data, demographicplot.layout);


      // Populate the pie chart in the website
      const plotData = JSON.parse(data.pie_chart);
      Plotly.newPlot("pie-chart-plot", plotData.data, plotData.layout);

      // For your second table (Return table)
      window.secondTableData = {
        sales_by_title: data.sales_details_title,
        sales_by_vertical: data.sales_details_vertical,
        return_by_title: data.return_details_title,
        return_by_vertical: data.return_details_vertical,
        cancellation_by_title: data.cancelled_details_title,
        cancellation_by_vertical: data.cancelled_details_vertical,
        net_sales_by_title: data.net_sales_details_title,
        net_sales_by_vertical: data.net_sales_details_vertical
      };

      applyReturnFilter(); // existing function

      // initiate the PnL Table
      fetchPnLData()

    })
    .catch((error) => {
      console.error("Error fetching insights:", error);
      alert("Failed to fetch insights. Please try again later.");
    });
}



// Existing event listener for "fetch-insights" button (unchanged)
document.getElementById("fetch-insights").addEventListener("click", function () {
  const startDate = document.getElementById("start-date").value;
  const endDate = document.getElementById("end-date").value;
  const seller = document.getElementById("seller-slicer").value;
  const brand = document.getElementById("brand-slicer").value;
  console.log("brand slicer is triggered from fetch-insights function: ", brand);


  if (startDate && endDate) {
    fetchInsights(startDate, endDate, seller, brand);
  } else {
    alert("Please select both start and end dates.");
  }
});

// Event listener for seller filter (unchanged)
document.getElementById("seller-slicer").addEventListener("change", function () {
  console.log("seller filter is triggered");

  const startDate = document.getElementById("start-date").value;
  const endDate = document.getElementById("end-date").value;
  const seller = document.getElementById("seller-slicer").value;
  const brand = document.getElementById("brand-slicer").value;
  console.log("brand slicer is triggered from brand-slicer: ", brand);


  if (startDate && endDate) {
    fetchInsights(startDate, endDate, seller, brand);
  }
});


// This is the event listener for the graph selector
function attachDropdownEventListeners() {
  const checkboxes = document.querySelectorAll(".dropdown-menu input[type='checkbox']");
  checkboxes.forEach((checkbox) => {
    checkbox.addEventListener("change", function () {
      const selectedMetrics = Array.from(
        document.querySelectorAll(".dropdown-menu input[type='checkbox']:checked")
      ).map((checkbox) => checkbox.value);

      // Update the displayed plots dynamically based on selected metrics
      updatePlots(selectedMetrics);
    });
  });
}



function updatePlots(selectedMetrics) {
  console.log("graph selector is triggered!!!")
  const plotContainer = document.getElementById("plot-container");
  plotContainer.innerHTML = ""; // Clear existing plots

  // Single div for combined plots
  const combinedPlotDiv = document.createElement("div");
  combinedPlotDiv.id = "combined-plot";
  plotContainer.appendChild(combinedPlotDiv);

  let combinedTraces = []; // To store all selected plot traces
  let layout = {
    title: `Combined Graph: ${selectedMetrics.join(", ").toUpperCase()}`,
    xaxis: { title: "Date" },
    yaxis: { title: "" }, // Main y-axis (will apply to the first plot)
    margin: { l: 50, r: 70, t: 50, b: 50 },

    gridshow: false,
  };

  selectedMetrics.forEach((metric, index) => {

    if (dynamicPlots[metric]) {
      const plotData = JSON.parse(dynamicPlots[metric]);

      // Update trace to associate with the correct y-axis
      const yAxisId = index === 0 ? "y" : `y${index + 1}`;
      plotData.data.forEach((trace) => {
        trace.yaxis = yAxisId; // Associate trace with its specific y-axis
      });

      // Add the new y-axis configuration to the layout
      if (index > 0) {
        layout[`yaxis${index + 1}`] = {
          title: metric.toUpperCase(),
          showgrid: false, // Hide the grid of secondary y-axes to avoid overlap
          overlaying: "y", // Overlay with the main y-axis
          side: index % 2 === 0 ? "left" : "right", // Alternate sides
          // position: index % 2 === 0 ? leftYPosition + (yAxisOffset * (Math.floor(index / 2))) : rightYPosition - (yAxisOffset * Math.ceil(index / 2)), // Adjust position to keep y-axes outside
        };
      } else {
        layout.yaxis.title = metric.toUpperCase();
      }

      combinedTraces = combinedTraces.concat(plotData.data);
    }
  });


  // Render the combined plot in the same canvas
  Plotly.newPlot(combinedPlotDiv.id, combinedTraces, layout);
}



// ------------------ Global Variables & Setup ------------------ //

// Array to hold custom parameters objects: { name: <string>, value: <number> }.
let customParameters = [];

// Original keys from the backend in order.
const currentKeys = [
  "gross_revenue", "gross_units", "cancelled_amt", "cancelled_units", "returned_amt", "returned_units", "total_bank_discount",
  "net_revenue_with_tax", "net_units", "tax", "net_revenue_without_tax", "cogs", "product_margin", "codb",
  "shipping_fee", "reverse_shipping_fee", "sdd_fee", "fixed_fee",
  "commission_fee", "pick_pack_fee", "recall_fee", "sellable",
  "unsellable", "wallet_redeem", "collection_fee", "cancellation_fee", "cm_1", "warehouse_cost", "cm_2", "ads_spend", "cm3",
  "profit_percentage"
];

// Keys that should be collapsible under "codb"
const collapsibleKeys = [
  "shipping_fee", "reverse_shipping_fee", "sdd_fee", "fixed_fee",
  "commission_fee", "pick_pack_fee", "recall_fee", "sellable",
  "unsellable", "wallet_redeem", "collection_fee", "cancellation_fee"
];

let isCodbExpanded = false;

// ------------------ Modal Popup Logic for Custom Parameters ------------------ //

// Open the custom parameter modal
document.getElementById("open-custom-param-popup").addEventListener("click", function () {
  document.getElementById("custom-param-modal").style.display = "block";
});

// Close the custom parameter modal
document.getElementById("close-custom-param-modal").addEventListener("click", function () {
  document.getElementById("custom-param-modal").style.display = "none";
});

// Add a new row in the custom parameter modal
document.getElementById("add-custom-param-row").addEventListener("click", function () {
  const tbody = document.getElementById("custom-param-table").querySelector("tbody");
  const row = document.createElement("tr");

  row.innerHTML = `
    <td><input type="text" class="custom-param-name" placeholder="Parameter Name"></td>
    <td><input type="number" class="custom-param-value" placeholder="Value"></td>
    <td><button class="btn btn-danger btn-sm remove-custom-row">Remove</button></td>
  `;
  tbody.appendChild(row);

  // Add event listener to remove button
  row.querySelector(".remove-custom-row").addEventListener("click", function () {
    row.remove();
  });
});

// Save custom parameters from the modal
document.getElementById("save-custom-params").addEventListener("click", function () {
  const rows = document.querySelectorAll("#custom-param-table tbody tr");
  customParameters = []; // reset the array
  rows.forEach(row => {
    const name = row.querySelector(".custom-param-name").value.trim();
    const value = parseFloat(row.querySelector(".custom-param-value").value);
    if (name && !isNaN(value)) {
      customParameters.push({ name, value });
    }
  });
  // Optionally, log and/or send customParameters to the backend if needed.
  console.log("Saved Custom Parameters:", customParameters);

  // Close the modal
  document.getElementById("custom-param-modal").style.display = "none";

  // Now automatically re-fetch the PnL data to update the table
  fetchPnLData();

});

// ------------------ PnL Table Fetching & Rendering ------------------ //
document.getElementById("pnl-fetch-data").addEventListener("click", fetchPnLData);

function fetchPnLData() {
  const timeFormat = document.getElementById("pnl-time-slicer").value;
  const startDate = document.getElementById("pnl-start-date").value;
  const endDate = document.getElementById("pnl-end-date").value;
  const seller = document.getElementById("seller-slicer")?.value || "";
  const brand = document.getElementById("brand-slicer")?.value || "";

  if (!startDate || !endDate) {
    alert("Please select start and end dates.");
    return;
  }

  const url = `/backend/api/fk_pnl_details/?pnl_start_date=${startDate}&pnl_end_date=${endDate}&time_stamp=${timeFormat}&seller=${seller}&brand=${brand}`;

  fetch(url)
    .then(response => response.json())
    .then(data => {
      if (Object.keys(data).length === 0) {
        alert("No data available for the selected time range.");
        return;
      }
      updatePnLTable(data);
    })
    .catch(error => console.error("Error fetching data:", error));
}



function updatePnLTable(pnlData) {
  const tableHeader = document.getElementById("table-header");
  const tableBody = document.getElementById("table-body");

  tableHeader.innerHTML = "<th>PnL Parameters</th>";
  tableBody.innerHTML = "";

  const dataKeys = Object.keys(pnlData);
  if (dataKeys.length === 0) {
    alert("No data available for the selected time format.");
    return;
  }

  // Build table header using dataKeys (typically dates)
  dataKeys.forEach(colKey => {
    tableHeader.innerHTML += `<th>${colKey}</th>`;
  });

  // Number of columns (for dividing custom parameter values)
  const numColumns = dataKeys.length;

  // Map each predefined key (from the backend) to its index.
  const paramToIndex = {};
  currentKeys.forEach((param, idx) => {
    paramToIndex[param] = idx;
  });

  // Build the final row order:
  // Copy all predefined keys except "cm3" and "profit_percentage" and insert custom parameters after "ads_spend"
  let finalKeys = [];
  currentKeys.forEach(param => {
    if (param === "cm3" || param === "profit_percentage") return;
    finalKeys.push(param);
    if (param === "ads_spend") {
      // Insert each custom parameter name here (if any)
      if (customParameters.length > 0) {
        customParameters.forEach(cp => {
          console.log("Adding custom param:", cp.name);
          finalKeys.push(cp.name);
        });
      }
    }
  });
  // Append computed rows at the end.
  finalKeys.push("cm3");
  finalKeys.push("profit_percentage");

  console.log("Final row order:", finalKeys);

  // Precompute the distributed value for each custom parameter for one column.
  // (i.e. each custom parameter's value divided by the number of columns)
  const customParamMap = {};
  customParameters.forEach(cp => {
    customParamMap[cp.name] = cp.value / numColumns;
    console.log("Distributed value for", cp.name, ":", customParamMap[cp.name]);
  });

  // When recalculating cm3, we need to subtract the distributed custom parameter values for each column.
  // Note: We subtract each column's distributed value (which may be different from subtracting the total after division)
  const totalCustomPerColumn = Object.values(customParamMap).reduce((acc, val) => acc + val, 0);

  // Build table rows using finalKeys
  finalKeys.forEach(param => {
    const safeParam = param.replace(/\s+/g, "-");
    let rowHTML = `<tr id="${safeParam}-row" ${param === "codb" ? 'onclick="toggleCodb()" style="cursor:pointer; font-weight:bold;"' : ''}>`;

    // Parameter label cell.
    if (param === "codb") {
      rowHTML += `<td><strong><span id="codb-toggle">➕</span> ${param.replace(/_/g, " ").toUpperCase()}</strong></td>`;
    } else {
      rowHTML += `<td><strong>${param.replace(/_/g, " ").toUpperCase()}</strong></td>`;
    }

    // For each column (date)...
    dataKeys.forEach(colKey => {
      let cellValue = 0;

      // 1. For standard parameters provided by the backend:
      if (paramToIndex.hasOwnProperty(param)) {
        const idx = paramToIndex[param];
        const arr = pnlData[colKey];
        cellValue = arr[idx] !== undefined ? arr[idx] : 0;
      }
      // 2. For custom parameters:
      else if (customParamMap.hasOwnProperty(param)) {
        cellValue = customParamMap[param];
      }

      // 3. Recalculate cm3 and profit_percentage:
      if (param === "cm3") {
        // Instead of using backend's cm3 directly, recalc:
        // cm3 = (backend's cm3 value) - (sum of distributed custom parameter values)
        const arr = pnlData[colKey];
        const backendCM3 = arr[paramToIndex["cm3"]] !== undefined ? arr[paramToIndex["cm3"]] : 0;
        // Below you have to specifiy whether the added parameter is a cost (negative value) or benefits (positive value)
        cellValue = backendCM3 + totalCustomPerColumn;
        // cellValue = backendCM3 - totalCustomPerColumn;
      } else if (param === "profit_percentage") {
        // profit_percentage = (updated cm3 * 100) / net_revenue_without_tax
        const arr = pnlData[colKey];
        const netRevVal = arr[paramToIndex["net_revenue_without_tax"]] || 0;
        const backendCM3 = arr[paramToIndex["cm3"]] !== undefined ? arr[paramToIndex["cm3"]] : 0;
        const updatedCM3 = backendCM3 - totalCustomPerColumn;
        cellValue = netRevVal !== 0 ? (updatedCM3 * 100) / netRevVal : 0;
      }

      rowHTML += `<td>${roundToTwoDecimals(cellValue)}</td>`;
    });

    rowHTML += "</tr>";
    tableBody.innerHTML += rowHTML;
  });

  // Initially hide collapsible rows (e.g. for CODB)
  collapsibleKeys.forEach(key => {
    const row = document.getElementById(key.replace(/\s+/g, "-") + "-row");
    if (row) {
      row.style.display = "none";
    }
  });
}


// ------------------ Collapsible CODB Logic ------------------ //
function toggleCodb() {
  isCodbExpanded = !isCodbExpanded;
  const toggleIcon = document.getElementById("codb-toggle");

  collapsibleKeys.forEach(key => {
    const row = document.getElementById(key.replace(/\s+/g, "-") + "-row");
    if (row) row.style.display = isCodbExpanded ? "table-row" : "none";
  });

  toggleIcon.textContent = isCodbExpanded ? "➖" : "➕";
}

// ------------------ Utility Function ------------------ //
function roundToTwoDecimals(value) {
  return Math.round(value * 100) / 100;
}





// For downloading the PnL table as CSV file
function downloadTableAsCSV() {
  let table = document.getElementById("insights-table");
  let rows = table.querySelectorAll("tr");
  let csvContent = [];

  rows.forEach(row => {
    let cols = row.querySelectorAll("th, td");
    let rowData = [];
    cols.forEach(col => rowData.push(col.innerText));
    csvContent.push(rowData.join(","));
  });

  let csvString = csvContent.join("\n");
  let blob = new Blob([csvString], { type: "text/csv" });
  let link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "insights_table.csv";
  link.click();
}


// This is for dynamically loading the su-brands when a particular brand is selected in the main-stream
const SellerBrandMap = {

  "TRI": [""],
  "Amour Hygiene": [""],
  "NexTen Brands": ["Duggu", "KiddySoft", "Absorbia", "Alpas", "Champs", "Eldry", "JoyFix", "KiddleCare", "PomeeBuzz", "SeniorCare"],
  "All Seller": [""]

};

const sellerSlicer = document.getElementById("seller-slicer");
const BrandSlicer = document.getElementById("brand-slicer");

// Function to update sub-brand dropdown based on selected brand
function updateBrands() {
  const selectedSeller = sellerSlicer.value;

  // Clear existing options
  BrandSlicer.innerHTML = `<option value="">Brand</option>`;

  // Show sub-brand categories if "All Brand" is selected
  if (selectedSeller === "All Seller") {
    SellerBrandMap["All Seller"].forEach(Brand => {
      addBrandOption(Brand);
    });
  }

  // Otherwise, show specific sub-brands
  else if (SellerBrandMap[selectedSeller]) {
    SellerBrandMap[selectedSeller].forEach(Brand => {
      addBrandOption(Brand);
    });
  }
}

// Helper function to add sub-brand options
function addBrandOption(Brand) {
  const option = document.createElement("option");
  option.value = Brand;
  option.textContent = Brand;
  BrandSlicer.appendChild(option);
}

// Function to handle sub-brand selection
function handleBrandSelection() {

  const brand = BrandSlicer.value;
  const startDate = document.getElementById("start-date").value;
  const endDate = document.getElementById("end-date").value;
  const seller = document.getElementById("seller-slicer").value;
  console.log("brand slicer is triggered from brand-slicer: ", brand);

  if (startDate && endDate) {
    fetchInsights(startDate, endDate, seller, brand);
  }

}

// Event listener for brand selection change
sellerSlicer.addEventListener("change", updateBrands);

// Event listener for sub-brand selection change
BrandSlicer.addEventListener("change", handleBrandSelection);


// Making the Product table downloadable as an excel file
document.getElementById('download-table').addEventListener('click', function () {
  const table = document.getElementById('return-consolidated-data-table');
  let tableHtml = table.outerHTML.replace(/ /g, '%20');

  // Create a temporary link to trigger download
  const downloadLink = document.createElement('a');
  downloadLink.href = 'data:application/vnd.ms-excel,' + tableHtml;
  downloadLink.download = 'Product_table.xls'; // File name
  document.body.appendChild(downloadLink);
  downloadLink.click();
  document.body.removeChild(downloadLink);
});

// This is for the return table to show the SKU column based on the dropdown selection (vertical or product)
const dropdown = document.getElementById("return-category-slicer");
const table = document.getElementById("return-consolidated-data-table");
dropdown.addEventListener("change", function () {
  const isVerticalLevel = dropdown.value === "return_vertical";

  // Get all rows including the header
  const rows = table.querySelectorAll("tr");

  rows.forEach(row => {
    const firstCell = row.children[0]; // First cell (SKU column)
    if (firstCell) {
      firstCell.style.display = isVerticalLevel ? "none" : ""; // Hide or show SKU column
    }
  });
});