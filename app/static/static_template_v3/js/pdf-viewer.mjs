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

/**
 * Collect necessary config for this script.
 */
function getConfig() {
  return {
    api: {
      endpoint: {
        base: document
          .querySelector("meta[name='api.endpoint.base']")
          .getAttribute("content"),
      },
    },
    doc: {
      uuid: dataset.docId,
    },
  };
}

/**
 * Create a document URL to be accessed.
 */
function makeDocumentURL(config = {}) {
  let currentUrl = new URL(window.location.href);

  if (currentUrl.searchParams.get("type") === "pptx") {
    return new URL(
      `${config.api.endpoint.base}/doc/pptx/${config.doc.uuid}/load`,
    );
  }

  return new URL(`${config.api.endpoint.base}/doc/${config.doc.uuid}/load`);
}

/**
 * The workerSrc property shall be specified.
 */
function loadPDFJSWorker() {
  let workerURL = "/js/pdfjs-dist/build/pdf.worker.mjs";
  pdfjsLib.GlobalWorkerOptions.workerSrc = workerURL;
}

let dataset = document.querySelector("[data-doc-id]").dataset;

let channel = new BroadcastChannel("viewer.single");

let config = getConfig();

let url = makeDocumentURL(config);
url.searchParams.append("per_page", 10);
url.searchParams.append("jump_to", Number(config.doc.uuid) || 0);

loadPDFJSWorker();

// Some PDFs need external cmaps.
//
const CMAP_URL = "/js/pdfjs-dist/cmaps/";
const CMAP_PACKED = true;

const ENABLE_XFA = true;

const SANDBOX_BUNDLE_SRC = `${window.location.origin}/js/pdfjs-dist/build/pdf.sandbox.mjs`;

const container = document.getElementById("viewerContainer");

const eventBus = new pdfjsViewer.EventBus();

// Loading document.
const loadingTask = pdfjsLib.getDocument({
  url: url.href,
  cMapUrl: CMAP_URL,
  cMapPacked: CMAP_PACKED,
  enableXfa: ENABLE_XFA,
});

const pdfDocument = await loadingTask.promise;

// (Optionally) enable hyperlinks within PDF files.
const pdfLinkService = new pdfjsViewer.PDFLinkService({
  eventBus,
});

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
      rect.right <= (window.innerWidth || document.documentElement.clientWidth);

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
  pdfViewer.currentScaleValue = "1";
});

eventBus.on("pagesloaded", async () => {
  let attacments = await pdfDocument.getAttachments();
  channel.postMessage({
    event: "pagesloaded",
    payload: attacments || [],
  });

  // Notify that pages are fully loaded
  channel.postMessage({
    event: "page.loaded",
    payload: true,
  });

  // Iterate over all pages to convert page into thumbnail then notify the
  // result
  for (let i = 1; i <= pdfViewer.pagesCount; i++) {
    let page = await pdfDocument.getPage(i);
    let viewport = page.getViewport({ scale: 0.5 });
    let canvas = document.createElement("canvas");
    let context = canvas.getContext("2d");

    canvas.height = viewport.height;
    canvas.width = viewport.width;

    let renderCtx = {
      canvasContext: context,
      viewport: viewport,
    };

    await page.render(renderCtx).promise;

    channel.postMessage({
      event: "thumbnail.sent",
      payload: canvas.toDataURL(),
    });
  }
});

eventBus.on("pagechanging", () => {
  let jumpToEl = document.querySelector("#jumpto_input");

  channel.postMessage({
    event: "pagechanging",
    payload: { page: pdfViewer.currentPageNumber },
  });

  // Update current page UI on navbar to show current displayed page number.
  if (jumpToEl) jumpToEl.value = pdfViewer.currentPageNumber;

  // -- DISABLE FOR PARTIAL RENDERING --
  // if (pdfViewer.pagesCount === pdfViewer.currentPageNumber) {
  //   channel.postMessage({ event: "last_page_reached" });
  // }
  // -- END --
});

eventBus.on("updatefindmatchescount", (data) => {
  channel.postMessage({
    event: "updatefindmatchescount",
    payload: data.matchesCount,
  });
});

eventBus.on("updatefindcontrolstate", (data) => {
  channel.postMessage({
    event: "updatefindcontrolstate",
    payload: { ...data.matchesCount, state: data.state },
  });
});

// Document loaded, specifying document for the viewer and
// the (optional) linkService.
pdfViewer.setDocument(pdfDocument);

pdfLinkService.setDocument(pdfDocument, null);

let jumptoInput = document.querySelector("#jumpto_input");
jumptoInput.addEventListener("keydown", async (event) => {
  if (event.keyCode === 13) {
    let page = +event.target.value < 1 ? 1 : +event.target.value;
    pdfViewer.currentPageNumber = page;

    // -- DISABLE FOR PARTIAL RENDERING --
    // let value = event.target.value;

    // if (url.searchParams.has("per_page")) {
    //   url.searchParams.set("per_page", 10);
    // } else {
    //   url.searchParams.append("per_page", 10);
    // }

    // if (url.searchParams.has("jump_to")) {
    //   url.searchParams.set("jump_to", Number(value) - 1);
    // } else {
    //   url.searchParams.append("jump_to", Number(value) - 1);
    // }

    // const loadingTask = pdfjsLib.getDocument({
    //   url: url.href,
    //   cMapUrl: CMAP_URL,
    //   cMapPacked: CMAP_PACKED,
    //   enableXfa: ENABLE_XFA,
    // });

    // let pdfDocument = await loadingTask.promise;

    // pdfViewer.setDocument(pdfDocument);
    // pdfLinkService.setDocument(pdfDocument, null);
    // -- END --
  }
});

window.app = { viewer: pdfViewer };
