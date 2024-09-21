// Mock API calls
async function getStatus() {
  // 发送网络请求并处理响应
  return fetch("/api/mailhelper/status")
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json(); // 解析JSON数据
    })
    .then((data) => {
      console.log(data);
      return data; // 返回真实数据
    })
    .catch((error) => {
      console.error("Fetch error:", error); // 错误处理
      // 如果网络请求失败，可以返回默认数据
      return {
        valid: true,
        auth_url: "",
        last_crawl: "2023/11/27",
        last_record: "2023/11/26",
      };
    });
}


async function getRecentBills() {
  return fetch("/api/mailhelper/recent_bills")
  .then((response) => {
    if (!response.ok) {
      throw new Error("Network response was not ok");
    }
    return response.json(); // 解析JSON数据
  })
  .then((data) => {
    console.log(data);
    return data['data']; // 返回真实数据
  })
  .catch((error) => {
    console.error("Fetch error:", error); // 错误处理
    // 如果网络请求失败，可以返回默认数据
    return [
      { detail: "Groceries", time: "10:00", amount: "150.00", category: "Food" },
      // Additional records...
    ];
  });
  
}

// Front-end rendering functions
async function renderTokenStatus() {
  const status = await getStatus();
  console.log('status: ' + JSON.stringify(status))
  var tokenStatus = document.getElementById("tokenStatus");

  tokenStatus.className = status.valid
    ? "status-indicator valid"
    : "status-indicator invalid";
  tokenStatus.textContent = status.valid
    ? "Token状态: 有效"
    : "Token状态: 无效";

  if (status.auth_url) {
    document.getElementById("authUrl").href = status.auth_url;
    console.log('href:' + status.auth_url)
  }

  if (status.last_record) {
    document.getElementById("lastRecord").textContent = status.last_record;
  }

  if (status.last_crawl) {
    document.getElementById("lastCrawl").textContent = status.last_crawl;
  }
}

async function renderRecentBills() {
  const bills = await getRecentBills();
  const tableBody = document.getElementById("billsTableBody");
  bills.forEach((bill) => {
    const row = tableBody.insertRow();
    row.innerHTML = `
        <td>${bill.标题}</td>
        <td>${bill.金额}</td>
        <td>${bill.时间}</td>
        <td>${bill.分类}</td>
      `;
  });
}

document.getElementById("do-crawl").addEventListener("click", function () {
  const startDate = document.getElementById("start-date").value;
  const endDate = document.getElementById("end-date").value;

  if (startDate && endDate) {
    fetch(`/api/mailhelper/crawl?start=${startDate}&end=${endDate}`)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json(); // 解析JSON数据
      })
      .then((data) => {
        console.log("API数据:", data); // 这里可以进一步处理数据，如更新DOM
      })
      .catch((error) => {
        console.error("API请求出错:", error);
      });
  } else {
    alert("请选择开始日期和结束日期！");
  }
});

// Initial render call
document.addEventListener("DOMContentLoaded", function () {
  renderTokenStatus(); 
  renderRecentBills();
});
