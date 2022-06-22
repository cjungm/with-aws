
var loadingdiv = $('#loading');
var noresults = $('#noresults');
var resultdiv = $('#results');
var searchbox = $('input#search');
var timer = 0;
var ul = document.querySelector(".pop_rel_keywords");
var relContainer = document.querySelector(".rel_search");

// Executes the search function 250 milliseconds after user stops typing
searchbox.keyup(function () {
  clearTimeout(timer);
  timer = setTimeout(search, 250);
  relContainer.style.borderColor = "black";
});

async function search() {
  // Clear results before searching
  await noresults.hide();
  await loadingdiv.show();
  // Get the query from the user
  let query = searchbox.val();
  // Only run a query if the string contains at least three characters
  if (query.length > 2) {
    relContainer.classList.remove("hide");
    // Make the HTTP request with the query as a parameter and wait for the JSON results
    let response = await $.get(apigatewayendpoint, { q: query, size: 25, action: "auto-complete" }, 'json');
    // Get the part of the JSON response that we care about
    let results = response['hits']['hits'];
    if (results.length > 0) {
      loadingdiv.hide();
      relContainer.classList.remove("hide");
      while (ul.lastChild) {
        await ul.removeChild(ul.firstChild);
      }
      // Iterate through the results and write them to HTML
      // for (var item in results) {
      for (var idx = 0; idx < 10; idx++){
        if (results[idx] !== undefined) {
          let name = results[idx]._source.Name;
          // Construct the full HTML string that we want to append to the div
          const li = document.createElement("li");
          li.setAttribute("onclick", "autocomplete(this)");
          li.innerHTML = name;
          ul.appendChild(li);
        }
      }
    } else {
      await noresults.show();
      await resultdiv.empty();
    }
  } else {
    resultdiv.empty();
    // relContainer.classList.add("hide")
    if (!("hide" in relContainer.classList)) {
      relContainer.classList.add("hide");
    }
    while (ul.firstChild) {
      ul.removeChild(ul.firstChild);
    }
  }
  await loadingdiv.hide();
}

// Tiny function to catch images that fail to load and replace them
function imageError(image) {
  image.src = 'img/no-image.png';
}

function autocomplete(productname) {
  document.getElementById('search').value = productname.textContent;
  if (!("hide" in relContainer.classList)) {
    relContainer.classList.add("hide");
  }
  loadingdiv.hide();
  (async () => {
    await productlist()
  })()
}


async function productlist() {
  await resultdiv.empty();
  let productname = document.getElementById('search').value;
  const searchParams = new URLSearchParams(location.search).get('username');
  if (!("hide" in relContainer.classList)) {
    relContainer.classList.add("hide");
  }
  let response = await $.get(apigatewayendpoint, { q: productname + "/" + searchParams, size: 25, action: "search" }, 'json');
  let results = response['hits']['hits'];
  if (results.length > 0) {
    while (ul.lastChild) {
      await ul.removeChild(ul.firstChild);
    }
    // Iterate through the results and write them to HTML
    resultdiv.append('<p>Found ' + results.length + ' results.</p>');
    for (var item in results) {
      let url = 'https://shopping.interpark.com/product/productInfo.do?prdNo=' + results[item]._source.PrdNo;
      let image = results[item]._source.Img_url;
      let name = results[item]._source.Name;
      let price = results[item]._source.Price;
      resultdiv.append('<div class="result">' +
        '<a href="' + url + '"><img src="' + image + '" onerror="imageError(this)"></a>' +
        '<div><h3><a href="' + url + '">' + name + '</a></h3><p>' + price + '원</p></div></div>');
    }
  }
}

// 실시간 인기 검색어
setInterval(async function ranklist() {
  const searchParams = new URLSearchParams(location.search).get('username');
  let response = await $.get(apigatewayendpoint, { q: searchParams, size: 25, action: "rank-list" }, 'json');
  let results = response['product'];
  console.log(results)
  for (var idx = 0; idx < 10; idx++) {
    (function (idx) {
      if (results[idx] !== undefined) {
        const rank_li = document.getElementById('rank-list' + idx);
        let name = results[idx].Name;
        console.log(idx + " " + name)
        rank_li.innerHTML = name;
        rank_li.setAttribute("onclick", "autocomplete(this)");
      } else {
        console.log("None")
        document.getElementById('rank-list' + idx).innerHTML = "-";
      }
    }
    )(idx)
  }
}, 10000)

onscroll = function() {
  var nVScroll = document.documentElement.scrollTop || document.body.scrollTop;
  if(nVScroll > 40){
    $("#rank-list")
    .css("position", "fixed")
    .css("width", "20%")
    .css("float", "right")
    .css("right", "5%"); 
  } 
};

/* [html 최초 로드 및 이벤트 상시 대기 실시] */
window.onload = function() {
  // [이벤트 함수 호출]
  intentDefaultPage();
};

/* [이벤트 수행 함수] */
function intentDefaultPage(){
  const searchParams = new URLSearchParams(location.search).get('username');
  document.getElementById('username').innerHTML = searchParams.toUpperCase().substring(0, 1);
};