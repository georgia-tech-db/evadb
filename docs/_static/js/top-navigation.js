// Remove the black background from the announcement banner. We abuse the
// sphinx-book-theme announcement feature to place a navigation bar on top of the
// documentation. This javascript file replaces the announcement banner with the
// navigation bar.
// document
//   .getElementsByClassName("announcement")[0]
//   .classList.remove("header-item");

document
  .getElementsByClassName("announcement")[0]
  .classList.remove("announcement");

// Get the right relative URL for a given path
function getNavURL(url) {
  references = document.getElementsByClassName("reference internal");
  for (let i = 0; i < references.length; i++) {
    if (references[i].href.includes(url)) {
      return references[i].href;
    }
  }
}

is_get_started = window.location.href.endsWith(
  "source/overview/getting-started.html"
);
is_use_cases = window.location.href.includes("source/usecases/");
is_developer_guide = window.location.href.includes("source/dev-guide/");
is_documentation = !(is_get_started || is_use_cases || is_developer_guide);

lightEvaLogoSvg =
  "<svg width='2030' height='460' xmlns='http://www.w3.org/2000/svg' overflow='hidden' viewBox='0 0 2030 460' ><g transform='translate(-640 -675)'><text fill='#F56522' font-family='Work Sans,Work Sans_MSFontService,sans-serif' font-weight='700' font-size='477' transform='translate(1165.32 1083)'>Eva<tspan fill='#000' x='844.479' y='0'>DB</tspan></text><path d='m1188.46 679.327-107.01 36.524c-9.56-3.205-27.86-6.011-55.06 3.048-36.352 12.385-46.387 41.488-71.407 78.738-44.82-47.557-114.67-93.243-170.297-111.949-5.638-1.857-12.091.948-14.411 6.266-.875 2.004-1.065 4.178-.543 6.215 8.587 28.289 20.714 55.397 36.144 80.794 49.398 10.056 96.431 26.169 127.081 48.41a245.023 245.023 0 0 1-9.715 10.718c-58.552-41.34-187.137-64.482-268.628-55.134-6.081.723-10.643 5.838-10.191 11.424a9.257 9.257 0 0 0 2.397 5.494c35.376 37.242 122.271 90.888 194.89 113.647L716.363 1124.86c-1.602 3.05-.293 6.59 2.924 7.9 2.252.92 4.949.53 6.927-1 42.419-39.35 118.554-104.07 187.394-132.339 132.282-54.303 184.272-152.11 176.622-267.657l99.48-49.392c.86-.521 1.15-1.57.63-2.344-.39-.579-1.14-.858-1.88-.701Z' fill='#F46523' fill-rule='evenodd'/></g></svg>";

darkEvaLogoSvg =
  "<svg width='2030' height='460' xmlns='http://www.w3.org/2000/svg' overflow='hidden' viewBox='0 0 2030 460'><g transform='translate(-640 -675)'><text fill='#F56522' font-family='Work Sans,Work Sans_MSFontService,sans-serif' font-weight='700' font-size='477' transform='translate(1165.32 1083)'>Eva<tspan fill='#FFFFFF' x='844.479' y='0'>DB</tspan></text><path d='m1188.46 679.327-107.01 36.524c-9.56-3.205-27.86-6.011-55.06 3.048-36.352 12.385-46.387 41.488-71.407 78.738-44.82-47.557-114.67-93.243-170.297-111.949-5.638-1.857-12.091.948-14.411 6.266-.875 2.004-1.065 4.178-.543 6.215 8.587 28.289 20.714 55.397 36.144 80.794 49.398 10.056 96.431 26.169 127.081 48.41a245.023 245.023 0 0 1-9.715 10.718c-58.552-41.34-187.137-64.482-268.628-55.134-6.081.723-10.643 5.838-10.191 11.424a9.257 9.257 0 0 0 2.397 5.494c35.376 37.242 122.271 90.888 194.89 113.647L716.363 1124.86c-1.602 3.05-.293 6.59 2.924 7.9 2.252.92 4.949.53 6.927-1 42.419-39.35 118.554-104.07 187.394-132.339 132.282-54.303 184.272-152.11 176.622-267.657l99.48-49.392c.86-.521 1.15-1.57.63-2.344-.39-.579-1.14-.858-1.88-.701Z' fill='#F46523' fill-rule='evenodd'/></g></svg>";

topNavContent = document.createElement("div");
topNavContent.setAttribute("class", "top-nav-content");

// The left part that contains links and menus
topNavContentLeft = document.createElement("div");
topNavContentLeft.setAttribute("class", "left");

leftContents = [];

//-- The EvaDB link
lightLinkEvaDB = document.createElement("a");
lightLinkEvaDB.setAttribute("href", getNavURL("source/overview/getting-started.html").replace("source/overview/getting-started.html", "index.html"))
lightLinkEvaDB.setAttribute("class", "evadb-logo");
lightLinkEvaDB.classList.add("only-light");
lightLinkEvaDB.innerHTML += lightEvaLogoSvg;

darkLinkEvaDB = document.createElement("a");
darkLinkEvaDB.setAttribute("href", getNavURL("source/overview/getting-started.html").replace("source/overview/getting-started.html", "index.html"))
darkLinkEvaDB.setAttribute("class", "evadb-logo");
darkLinkEvaDB.classList.add("only-dark");
darkLinkEvaDB.innerHTML += darkEvaLogoSvg;

topNavContentLeft.append(lightLinkEvaDB);
topNavContentLeft.append(darkLinkEvaDB);

// leftContents.push(linkEvaDB)

//-- The Get started link
getStartedLink = document.createElement("a");
getStartedLink.innerText = "Get started";
getStartedLink.setAttribute(
  "href",
  getNavURL("source/overview/getting-started.html")
);
if (is_get_started) {
  getStartedLink.style.borderBottom = "2px solid var(--orange)";
}
leftContents.push(getStartedLink);

//-- The Use Cases link
useCasesLink = document.createElement("a");
useCasesLink.innerText = "Use cases";
useCasesLink.setAttribute(
  "href",
  getNavURL("source/usecases/image-classification.html")
);
if (is_use_cases) {
  useCasesLink.style.borderBottom = "2px solid var(--orange)";
}
leftContents.push(useCasesLink);

//-- The Documentation link
documentationLink = document.createElement("a");
documentationLink.innerText = "Docs";
documentationLink.setAttribute("href", getNavURL("source/overview/getting-started.html").replace("source/overview/getting-started.html", "index.html"))
if (is_documentation) {
  documentationLink.style.borderBottom = "2px solid var(--orange)";
}
leftContents.push(documentationLink);

//-- The Developer Guide
developerGuideLink = document.createElement("a");
developerGuideLink.innerText = "Developer Guide";
developerGuideLink.setAttribute(
  "href",
  getNavURL("source/dev-guide/contribute.html")
);
if (is_developer_guide) {
  developerGuideLink.style.borderBottom = "2px solid var(--orange)";
}

leftContents.push(developerGuideLink);

leftContents.forEach(function (content) {
  var lightContent = content.cloneNode(true);
  lightContent.classList.add("only-light");
  lightContent.style.color = "black";
  topNavContentLeft.append(lightContent);

  var darkContent = content.cloneNode(true);
  darkContent.classList.add("only-dark");
  darkContent.style.color = "white";
  topNavContentLeft.append(darkContent);
});

topNavContent.append(topNavContentLeft);



// RIGHT PART

topNavContentRight = document.createElement("div");
topNavContentRight.setAttribute("class", "image-header");
topNavContentRight.innerHTML = "<a class = 'only-dark:bg-gray-500' href='https://github.com/georgia-tech-db/evadb'><img class='icon-hover only-light' src='https://raw.githubusercontent.com/georgia-tech-db/evadb/master/docs/_static/icons/github.png' width='25px' height='25px'><img class='icon-hover only-dark' src='https://raw.githubusercontent.com/georgia-tech-db/evadb/master/docs/_static/icons/github-no-fill.png' width='25px' height='25px'></a> <a href='https://join.slack.com/t/eva-db/shared_invite/zt-1i10zyddy-PlJ4iawLdurDv~aIAq90Dg'><img class='icon-hover' src='https://raw.githubusercontent.com/georgia-tech-db/evadb/master/docs/_static/icons/slack.png' width='25px' height='25px'> </a><a href='https://twitter.com/evadb_ai'> <img class='icon-hover' src='https://raw.githubusercontent.com/georgia-tech-db/evadb/master/docs/_static/icons/twitter.png' width='25px' height='25px'> </a>"

topNavContent.append(topNavContentRight)



document.getElementsByClassName("topnav")[0].append(topNavContent);