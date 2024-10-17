/* Copyright 2014 Mozilla Foundation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

if (!pdfjsLib.getDocument || !pdfjsViewer.PDFViewer) {
  // eslint-disable-next-line no-alert
  alert("Please build the pdfjs-dist library using\n  `gulp dist-install`");
}

let config = {
  apiBaseURL: document
    .querySelector("meta[name='api.endpoint.base']")
    .getAttribute("content"),
  staticBaseURL: document
    .querySelector("meta[name='asset.static.base']")
    .getAttribute("content"),
};

let apiURL = new URL(config.apiBaseURL);
let staticURL = new URL(config.staticBaseURL);
let currentURL = new URL(window.location);

let channel = new BroadcastChannel("viewer.compare");

let url = new URL(
  `${apiURL.origin}/api/doc/${currentURL.searchParams.get("left")}/load`,
);
url.searchParams.append("per_page", 10);
// url.searchParams.append("jump_to", bodyDataSet.jumpTo || 1);

// The workerSrc property shall be specified.
//
pdfjsLib.GlobalWorkerOptions.workerSrc = `${staticURL.href}/js/pdfjs-dist/build/pdf.worker.mjs`;

// Some PDFs need external cmaps.
//
const CMAP_URL = `${staticURL.href}/js/pdfjs-dist/cmaps/`;
const CMAP_PACKED = true;

const ENABLE_XFA = true;

const SANDBOX_BUNDLE_SRC = `${staticURL.href}/js/pdfjs-dist/build/pdf.sandbox.mjs`;

let container = {
  left: document.querySelector("#left_preview"),
  right: document.querySelector("#right_preview"),
};

let docURL = {
  left: currentURL.searchParams.get("left"),
  right: currentURL.searchParams.get("right"),
};

async function renderPreview(container, uuid, position) {
  let pattern =
    /^[0-9a-f]{8}-[0-9a-f]{4}-[4][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

  if (!pattern.test(uuid)) {
    return;
  }

  const eventBus = new pdfjsViewer.EventBus();

  // (Optionally) enable hyperlinks within PDF files.
  const pdfLinkService = new pdfjsViewer.PDFLinkService({ eventBus });

  // (Optionally) enable find controller.
  const pdfFindController = new pdfjsViewer.PDFFindController({
    eventBus,
    linkService: pdfLinkService,
  });

  // Override the default behaviour of PDF.js `scrollMatchIntoView` because it's
  // possibly bugs that lead cannot scroll to exact match word or phrase.
  let findController = pdfFindController.scrollMatchIntoView;
  pdfFindController.scrollMatchIntoView = function (...args) {
    findController.apply(this, args);
    setTimeout(() => {
      let match = document.querySelector(".selected");
      // Check if the selected match is outside the viewport
      let rect = match.getBoundingClientRect();
      let isInViewport =
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <=
          (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <=
          (window.innerWidth || document.documentElement.clientWidth);

      // Only scroll if the selected match is not in the viewport
      if (!isInViewport) {
        match.scrollIntoView({ behavior: "instant", block: "center" });
      }
    });
  };
  // (Optionally) enable scripting support.
  const pdfScriptingManager = new pdfjsViewer.PDFScriptingManager({
    eventBus,
    sandboxBundleSrc: SANDBOX_BUNDLE_SRC,
  });

  const pdfViewer = new pdfjsViewer.PDFViewer({
    container,
    eventBus,
    linkService: pdfLinkService,
    findController: pdfFindController,
    scriptingManager: pdfScriptingManager,
  });
  pdfLinkService.setViewer(pdfViewer);
  pdfScriptingManager.setViewer(pdfViewer);

  eventBus.on("pagesinit", function () {
    // We can use pdfViewer now, e.g. let's change default scale.
    pdfViewer.currentScaleValue = "page-width";
  });

  eventBus.on("pagesloaded", () => {
    channel.postMessage({
      event: "page.loaded",
      payload: { loaded: true, position },
    });
  });

  eventBus.on("pagechanging", () => {
    let jumpToEl = document.querySelector(`#jumpto_input_${position}`);

    channel.postMessage({
      event: "page_changing",
      payload: { page: pdfViewer.currentPageNumber },
    });

    // Update current page UI on navbar to show current displayed page number.
    if (jumpToEl) jumpToEl.value = pdfViewer.currentPageNumber;

    // -- DISABLE FOR PARTIAL RENDERING --
    // if (pdfViewer.pagesCount === pdfViewer.currentPageNumber) {
    //   channel.postMessage({
    //     event: "last_page_reached",
    //     payload: { position },
    //   });
    // }
    // -- END --
  });

  eventBus.on("updatefindmatchescount", (data) => {
    channel.postMessage({
      event: "updatefindmatchescount",
      payload: { ...data.matchesCount, position },
    });
  });

  eventBus.on("updatefindcontrolstate", (data) => {
    channel.postMessage({
      event: "updatefindcontrolstate",
      payload: { ...data.matchesCount, state: data.state, position },
    });
  });

  // Loading document.
  const loadingTask = pdfjsLib.getDocument({
    url: `${apiURL.origin}/api/doc/${uuid}/load?per_page=10`,
    cMapUrl: CMAP_URL,
    cMapPacked: CMAP_PACKED,
    enableXfa: ENABLE_XFA,
  });

  const pdfDocument = await loadingTask.promise;
  // Document loaded, specifying document for the viewer and
  // the (optional) linkService.
  pdfViewer.setDocument(pdfDocument);

  pdfLinkService.setDocument(pdfDocument, null);

  let jumptoInput = document.querySelector(`#jumpto_input_${position}`);

  if (jumptoInput) {
    jumptoInput.addEventListener("keydown", (event) => {
      let page = +event.target.value < 1 ? 1 : +event.target.value;
      pdfViewer.currentPageNumber = page;
    });
  }

  return pdfViewer;
}

let left = renderPreview(container.left, docURL.left, "left");
let right = renderPreview(container.right, docURL.right, "right");

window.app = { viewer: { left: await left, right: await right } };
