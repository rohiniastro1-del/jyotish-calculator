function decimalToDegreeMinutes(value) {
  const absolute = Math.abs(value);
  let degrees = Math.floor(absolute);
  let minutes = Math.round((absolute - degrees) * 60);

  if (minutes === 60) {
    degrees += 1;
    minutes = 0;
  }

  return { degrees, minutes };
}

const NORTH_CHART_LAYOUTS = {
  1: { sign: [286.0, 221.0], box: { x: 240.0, y: 99.0, width: 86.0, height: 74.0 } },
  2: { sign: [149.0, 108.0], box: { x: 106.0, y: 16.0, width: 86.0, height: 74.0 } },
  3: { sign: [117.0, 136.0], box: { x: 14.0, y: 99.0, width: 86.0, height: 74.0 } },
  4: { sign: [241.0, 266.0], box: { x: 93.0, y: 221.0, width: 86.0, height: 75.0 } },
  5: { sign: [117.0, 395.0], box: { x: 14.0, y: 357.0, width: 86.0, height: 74.0 } },
  6: { sign: [149.0, 423.0], box: { x: 101.0, y: 441.0, width: 86.0, height: 74.0 } },
  7: { sign: [286.0, 310.0], box: { x: 240.0, y: 366.0, width: 86.0, height: 74.0 } },
  8: { sign: [423.0, 423.0], box: { x: 383.0, y: 441.0, width: 87.0, height: 74.0 } },
  9: { sign: [455.0, 395.0], box: { x: 476.0, y: 366.0, width: 86.0, height: 74.0 } },
  10: { sign: [331.0, 266.0], box: { x: 371.0, y: 221.0, width: 86.0, height: 75.0 } },
  11: { sign: [455.0, 136.0], box: { x: 476.0, y: 99.0, width: 86.0, height: 74.0 } },
  12: { sign: [423.0, 108.0], box: { x: 383.0, y: 16.0, width: 87.0, height: 74.0 } },
};

const SOUTH_SIGN_LAYOUTS = {
  12: { box: { x: 14.9, y: 14.9, width: 135.5, height: 135.5 } },
  1: { box: { x: 150.5, y: 14.9, width: 135.5, height: 135.5 } },
  2: { box: { x: 286.0, y: 14.9, width: 135.5, height: 135.5 } },
  3: { box: { x: 421.5, y: 14.9, width: 135.5, height: 135.5 } },
  4: { box: { x: 421.5, y: 150.5, width: 135.5, height: 135.5 } },
  5: { box: { x: 421.5, y: 286.0, width: 135.5, height: 135.5 } },
  6: { box: { x: 421.5, y: 421.5, width: 135.5, height: 135.5 } },
  7: { box: { x: 286.0, y: 421.5, width: 135.5, height: 135.5 } },
  8: { box: { x: 150.5, y: 421.5, width: 135.5, height: 135.5 } },
  9: { box: { x: 14.9, y: 421.5, width: 135.5, height: 135.5 } },
  10: { box: { x: 14.9, y: 286.0, width: 135.5, height: 135.5 } },
  11: { box: { x: 14.9, y: 150.5, width: 135.5, height: 135.5 } },
};

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function groupChartItems(items) {
  const count = items.length;
  if (count === 0) {
    return [];
  }
  if (count === 1) {
    return [items];
  }
  if (count === 2 || count === 3 || count === 4) {
    return items.map((item) => [item]);
  }
  if (count === 5) {
    return [items.slice(0, 2), items.slice(2, 4), items.slice(4)];
  }

  const groups = [];
  for (let index = 0; index < count; index += 2) {
    groups.push(items.slice(index, index + 2));
  }
  return groups;
}

function chartLineYPositions(box, lineCount) {
  const centerY = box.y + box.height / 2;
  let lineGap;
  if (lineCount <= 3) {
    lineGap = 20.0;
  } else if (lineCount === 4) {
    lineGap = 18.0;
  } else {
    lineGap = 16.0;
  }
  const firstY = centerY - (((lineCount - 1) * lineGap) / 2);
  return Array.from({ length: lineCount }, (_, index) => firstY + index * lineGap);
}

function chartLineXPositions(box, itemCount) {
  const centerX = box.x + box.width / 2;
  if (itemCount === 1) {
    return [centerX];
  }

  const spread = Math.min(20.0, box.width * 0.22);
  return [centerX - spread, centerX + spread];
}

function chartItemPositions(displayHouse, items) {
  const box = NORTH_CHART_LAYOUTS[displayHouse].box;
  const groups = groupChartItems(items);
  const yPositions = chartLineYPositions(box, groups.length);
  const placed = [];

  groups.forEach((group, groupIndex) => {
    chartLineXPositions(box, group.length).forEach((xPos, itemIndex) => {
      placed.push([group[itemIndex], xPos, yPositions[groupIndex]]);
    });
  });

  return placed;
}

function southChartLineYPositions(box, lineCount) {
  const centerY = box.y + box.height / 2;
  let lineGap;
  if (lineCount <= 2) {
    lineGap = 24.0;
  } else if (lineCount <= 4) {
    lineGap = 22.0;
  } else {
    lineGap = 18.0;
  }
  const firstY = centerY - (((lineCount - 1) * lineGap) / 2);
  return Array.from({ length: lineCount }, (_, index) => firstY + index * lineGap);
}

function southChartLineXPositions(box, itemCount) {
  const centerX = box.x + box.width / 2;
  if (itemCount === 1) {
    return [centerX];
  }

  const spread = Math.min(26.0, box.width * 0.18);
  return [centerX - spread, centerX + spread];
}

function southChartItemPositions(signNumber, items) {
  const box = SOUTH_SIGN_LAYOUTS[signNumber].box;
  const groups = groupChartItems(items);
  const yPositions = southChartLineYPositions(box, groups.length);
  const placed = [];

  groups.forEach((group, groupIndex) => {
    southChartLineXPositions(box, group.length).forEach((xPos, itemIndex) => {
      placed.push([group[itemIndex], xPos, yPositions[groupIndex]]);
    });
  });

  return placed;
}

function chartTextClass(item, lineCount) {
  const classNames = ["chart-content"];
  if (item === "Ас") {
    classNames.push("chart-content--asc");
  } else if (item.includes("(")) {
    classNames.push("chart-content--retro");
  }
  if (lineCount >= 5) {
    classNames.push("chart-content--tight");
  }
  return classNames.join(" ");
}

function chartSignClass(signNumber) {
  return String(signNumber).length >= 2 ? "chart-sign-label chart-sign-label--double" : "chart-sign-label";
}

function rotateHouseToDisplayPosition(actualHouse, firstHouse) {
  return ((actualHouse - firstHouse + 12) % 12) + 1;
}

function renderNorthChartSvg(chartPayload, firstHouse, chartKey) {
  const title = escapeHtml(chartPayload.title);
  const ariaTitle = escapeHtml(chartPayload.aria_title || chartPayload.title);
  const chartId = `${chartKey}-${firstHouse}`;
  const bgId = `chartBg-${chartId}`;
  const centerId = `centerGlow-${chartId}`;
  const lineMaskId = `lineMask-${chartId}`;

  const signParts = [];
  const itemParts = [];
  const hitParts = [];

  chartPayload.houses.forEach((house) => {
    const displayHouse = rotateHouseToDisplayPosition(house.house, firstHouse);
    const [signX, signY] = NORTH_CHART_LAYOUTS[displayHouse].sign;
    const box = NORTH_CHART_LAYOUTS[displayHouse].box;

    signParts.push(
      `<text class="${chartSignClass(house.sign_number)}" x="${signX.toFixed(1)}" y="${signY.toFixed(1)}" text-anchor="middle" dominant-baseline="middle">${house.sign_number}</text>`,
    );

    const items = house.items || [];
    const lineCount = groupChartItems(items).length;
    chartItemPositions(displayHouse, items).forEach(([itemText, xPos, yPos]) => {
      itemParts.push(
        `<text class="${chartTextClass(itemText, lineCount)}" x="${xPos.toFixed(1)}" y="${yPos.toFixed(1)}" text-anchor="middle" dominant-baseline="middle">${escapeHtml(itemText)}</text>`,
      );
    });

    hitParts.push(
      `<rect class="chart-house-target" data-house-target="${house.house}" x="${box.x.toFixed(1)}" y="${box.y.toFixed(1)}" width="${box.width.toFixed(1)}" height="${box.height.toFixed(1)}" rx="12"></rect>`,
    );
  });

  return `
<svg class="north-chart-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 572 531" role="img" aria-label="${ariaTitle}">
  <defs>
    <linearGradient id="${bgId}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#fffef9" />
      <stop offset="100%" stop-color="#f4eedb" />
    </linearGradient>
    <linearGradient id="${centerId}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ddd2a5" />
      <stop offset="100%" stop-color="#c5b175" />
    </linearGradient>
    <mask id="${lineMaskId}">
      <rect width="572" height="531" fill="white" />
      <rect x="254" y="234" width="64" height="64" rx="16" fill="black" />
    </mask>
  </defs>
  <rect width="572" height="531" rx="18" fill="url(#${bgId})" />
  <g mask="url(#${lineMaskId})">
    <rect x="9" y="10" width="554" height="511" fill="none" stroke="#4e7b4a" stroke-width="2"/>
    <line x1="286" y1="10" x2="563" y2="265.5" stroke="#4e7b4a" stroke-width="2"/>
    <line x1="563" y1="265.5" x2="286" y2="521" stroke="#4e7b4a" stroke-width="2"/>
    <line x1="286" y1="521" x2="9" y2="265.5" stroke="#4e7b4a" stroke-width="2"/>
    <line x1="9" y1="265.5" x2="286" y2="10" stroke="#4e7b4a" stroke-width="2"/>
    <line x1="9" y1="10" x2="147.5" y2="137.75" stroke="#4e7b4a" stroke-width="2"/>
    <line x1="147.5" y1="137.75" x2="311" y2="291" stroke="#4e7b4a" stroke-width="2"/>
    <line x1="563" y1="10" x2="424.5" y2="137.75" stroke="#4e7b4a" stroke-width="2"/>
    <line x1="424.5" y1="137.75" x2="260" y2="291" stroke="#4e7b4a" stroke-width="2"/>
    <line x1="9" y1="521" x2="147.5" y2="393.25" stroke="#4e7b4a" stroke-width="2"/>
    <line x1="147.5" y1="393.25" x2="311" y2="240" stroke="#4e7b4a" stroke-width="2"/>
    <line x1="563" y1="521" x2="424.5" y2="393.25" stroke="#4e7b4a" stroke-width="2"/>
    <line x1="424.5" y1="393.25" x2="260" y2="240" stroke="#4e7b4a" stroke-width="2"/>
  </g>
  <rect x="260" y="240" width="51" height="51" rx="10" fill="url(#${centerId})" stroke="#4e7b4a" stroke-width="2"/>
  <text x="286" y="272" text-anchor="middle" class="chart-center-title">${title}</text>
  ${signParts.join("")}
  ${itemParts.join("")}
  ${hitParts.join("")}
</svg>`.trim();
}

function renderSouthChartSvg(chartPayload, chartKey) {
  const title = escapeHtml(chartPayload.title);
  const ariaTitle = escapeHtml(chartPayload.aria_title || chartPayload.title);
  const chartId = `${chartKey}-south`;
  const bgId = `southChartBg-${chartId}`;
  const centerId = `southCenterGlow-${chartId}`;

  const signItems = new Map();
  chartPayload.houses.forEach((house) => {
    signItems.set(Number(house.sign_number), house.items || []);
  });

  const itemParts = [];
  Object.keys(SOUTH_SIGN_LAYOUTS)
    .map((signNumber) => Number(signNumber))
    .sort((left, right) => left - right)
    .forEach((signNumber) => {
      const items = signItems.get(signNumber) || [];
      const lineCount = groupChartItems(items).length;
      southChartItemPositions(signNumber, items).forEach(([itemText, xPos, yPos]) => {
        itemParts.push(
          `<text class="${chartTextClass(itemText, lineCount)}" x="${xPos.toFixed(1)}" y="${yPos.toFixed(1)}" text-anchor="middle" dominant-baseline="middle">${escapeHtml(itemText)}</text>`,
        );
      });
    });

  return `
<svg class="south-chart-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 572 572" role="img" aria-label="${ariaTitle}">
  <defs>
    <linearGradient id="${bgId}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#fffef9" />
      <stop offset="100%" stop-color="#f4eedb" />
    </linearGradient>
    <linearGradient id="${centerId}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ddd2a5" />
      <stop offset="100%" stop-color="#c5b175" />
    </linearGradient>
  </defs>
  <rect width="572" height="572" fill="url(#${bgId})" />
  <rect x="14.9" y="14.9" width="542.2" height="542.2" fill="none" stroke="#4e7b4a" stroke-width="2.4" />
  <line x1="150.5" y1="14.9" x2="150.5" y2="557.1" stroke="#4e7b4a" stroke-width="2.4" />
  <line x1="421.5" y1="14.9" x2="421.5" y2="557.1" stroke="#4e7b4a" stroke-width="2.4" />
  <line x1="286.0" y1="14.9" x2="286.0" y2="150.5" stroke="#4e7b4a" stroke-width="2.4" />
  <line x1="286.0" y1="421.5" x2="286.0" y2="557.1" stroke="#4e7b4a" stroke-width="2.4" />
  <line x1="14.9" y1="150.5" x2="557.1" y2="150.5" stroke="#4e7b4a" stroke-width="2.4" />
  <line x1="14.9" y1="421.5" x2="557.1" y2="421.5" stroke="#4e7b4a" stroke-width="2.4" />
  <line x1="14.9" y1="286.0" x2="150.5" y2="286.0" stroke="#4e7b4a" stroke-width="2.4" />
  <line x1="421.5" y1="286.0" x2="557.1" y2="286.0" stroke="#4e7b4a" stroke-width="2.4" />
  <rect x="251.0" y="251.0" width="70.0" height="70.0" rx="13" fill="url(#${centerId})" stroke="#4e7b4a" stroke-width="2.4" />
  <text x="286" y="294" text-anchor="middle" class="chart-center-title">${title}</text>
  ${itemParts.join("")}
</svg>`.trim();
}

function bindCitySync(config) {
  const cityInput = document.getElementById(config.citySelectId);
  if (!cityInput) {
    return () => {};
  }

  const sync = () => {
    const selected = window.CITY_DATA.find((city) => city.name === cityInput.value.trim());
    if (!selected) {
      return;
    }

    const lat = decimalToDegreeMinutes(selected.lat);
    const lon = decimalToDegreeMinutes(selected.lon);

    document.getElementById(config.latitudeDegreesId).value = lat.degrees;
    document.getElementById(config.latitudeMinutesId).value = lat.minutes;
    document.getElementById(config.latitudeHemisphereId).value = selected.lat >= 0 ? "N" : "S";
    document.getElementById(config.longitudeDegreesId).value = lon.degrees;
    document.getElementById(config.longitudeMinutesId).value = lon.minutes;
    document.getElementById(config.longitudeHemisphereId).value = selected.lon >= 0 ? "E" : "W";
  };

  cityInput.addEventListener("change", sync);
  cityInput.addEventListener("blur", sync);
  return sync;
}

function bindTimezoneMode(selectId, containerId) {
  const modeSelect = document.getElementById(selectId);
  const manualFields = document.getElementById(containerId);
  if (!modeSelect || !manualFields) {
    return;
  }

  const sync = () => {
    manualFields.classList.toggle("is-hidden", modeSelect.value !== "manual");
  };

  modeSelect.addEventListener("change", sync);
  sync();
}

function bindChartLightbox() {
  const lightbox = document.getElementById("chartLightbox");
  const content = document.getElementById("chartLightboxContent");
  const title = document.getElementById("chartLightboxTitle");
  const closeButton = document.getElementById("chartLightboxClose");
  const zoomableFrames = document.querySelectorAll(".chart-frame--zoomable");

  if (!lightbox || !content || !title || !closeButton || !zoomableFrames.length) {
    return;
  }

  let lastActiveFrame = null;

  const close = () => {
    lightbox.classList.remove("is-open");
    lightbox.setAttribute("aria-hidden", "true");
    document.body.classList.remove("lightbox-open");
    content.innerHTML = "";

    if (lastActiveFrame) {
      lastActiveFrame.focus();
      lastActiveFrame = null;
    }
  };

  const open = (frame) => {
    const chartSvg = frame.querySelector(".north-chart-svg, .south-chart-svg");
    if (!chartSvg) {
      return;
    }

    lastActiveFrame = frame;
    title.textContent = frame.dataset.chartTitle || "Увеличена карта";
    content.innerHTML = chartSvg.outerHTML;
    lightbox.classList.add("is-open");
    lightbox.setAttribute("aria-hidden", "false");
    document.body.classList.add("lightbox-open");
    closeButton.focus();
  };

  zoomableFrames.forEach((frame) => {
    frame.addEventListener("click", () => {
      if (frame.classList.contains("is-selecting-house")) {
        return;
      }
      open(frame);
    });
    frame.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        open(frame);
      }
    });
  });

  lightbox.addEventListener("click", (event) => {
    if (event.target === lightbox || event.target.hasAttribute("data-close-lightbox")) {
      close();
    }
  });

  closeButton.addEventListener("click", close);

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && lightbox.classList.contains("is-open")) {
      close();
    }
  });
}

function bindChartRotation() {
  const chartCards = document.querySelectorAll(".chart-card");
  if (!chartCards.length) {
    return;
  }

  const groupStyles = {};
  const switchers = document.querySelectorAll(".chart-style-switch");
  switchers.forEach((switcher) => {
    groupStyles[switcher.dataset.chartStyleGroup] = switcher.dataset.defaultStyle || "north";
  });

  const controllers = [];

  chartCards.forEach((card, index) => {
    const frame = card.querySelector(".chart-frame--rotatable");
    const payloadNode = card.querySelector(".chart-payload");
    const toggleButton = card.querySelector(".chart-rotate-toggle");
    const resetButton = card.querySelector(".chart-rotate-reset");
    const tools = card.querySelector(".chart-tools");
    const styleGroup = card.dataset.chartStyleGroup || `chart-group-${index + 1}`;

    if (!frame || !payloadNode || !toggleButton || !resetButton) {
      return;
    }

    let chartPayload;
    try {
      chartPayload = JSON.parse(payloadNode.textContent);
    } catch (_error) {
      return;
    }

    const chartKey = `chart-${index + 1}`;
    let currentFirstHouse = 1;
    let selectingHouse = false;

    const updateControls = () => {
      const currentStyle = groupStyles[styleGroup] || "north";
      const isNorthStyle = currentStyle === "north";

      card.dataset.currentStyle = currentStyle;
      if (tools) {
        tools.classList.toggle("is-hidden", !isNorthStyle);
      }

      if (!isNorthStyle) {
        selectingHouse = false;
        toggleButton.classList.remove("is-active");
        resetButton.classList.add("is-hidden");
        frame.classList.remove("is-selecting-house");
        return;
      }

      toggleButton.textContent = selectingHouse ? "Избери дом..." : "Гледай от друг дом";
      toggleButton.classList.toggle("is-active", selectingHouse);
      resetButton.classList.toggle("is-hidden", currentFirstHouse === 1);
      frame.classList.toggle("is-selecting-house", selectingHouse);
    };

    const render = () => {
      const currentStyle = groupStyles[styleGroup] || "north";
      if (currentStyle === "south") {
        selectingHouse = false;
        frame.innerHTML = renderSouthChartSvg(chartPayload, chartKey);
      } else {
        frame.innerHTML = renderNorthChartSvg(chartPayload, currentFirstHouse, chartKey);
      }
      frame.dataset.currentFirstHouse = String(currentFirstHouse);
      updateControls();
    };

    toggleButton.addEventListener("click", () => {
      selectingHouse = !selectingHouse;
      updateControls();
    });

    resetButton.addEventListener("click", () => {
      currentFirstHouse = 1;
      selectingHouse = false;
      render();
    });

    frame.addEventListener("click", (event) => {
      if ((groupStyles[styleGroup] || "north") !== "north" || !selectingHouse) {
        return;
      }

      const target = event.target.closest("[data-house-target]");
      event.preventDefault();
      event.stopImmediatePropagation();
      event.stopPropagation();

      if (!target) {
        return;
      }

      currentFirstHouse = Number(target.getAttribute("data-house-target")) || 1;
      selectingHouse = false;
      render();
    }, true);

    controllers.push({ group: styleGroup, render });
  });

  switchers.forEach((switcher) => {
    const groupName = switcher.dataset.chartStyleGroup;
    const buttons = switcher.querySelectorAll(".chart-style-button");

    const syncButtons = () => {
      const currentStyle = groupStyles[groupName] || "north";
      buttons.forEach((button) => {
        const isActive = button.dataset.chartStyle === currentStyle;
        button.classList.toggle("is-active", isActive);
        button.setAttribute("aria-pressed", isActive ? "true" : "false");
      });
    };

    buttons.forEach((button) => {
      button.addEventListener("click", () => {
        groupStyles[groupName] = button.dataset.chartStyle || "north";
        syncButtons();
        controllers
          .filter((controller) => controller.group === groupName)
          .forEach((controller) => controller.render());
      });
    });

    syncButtons();
  });

  controllers.forEach((controller) => controller.render());
}

function bindTableScrollAssist() {
  const scrollAreas = document.querySelectorAll(".table-scroll");
  if (!scrollAreas.length) {
    return;
  }

  scrollAreas.forEach((scrollArea, index) => {
    const table = scrollArea.querySelector("table");
    if (!table || scrollArea.previousElementSibling?.classList.contains("table-scroll-assist")) {
      return;
    }

    const assist = document.createElement("div");
    assist.className = "table-scroll-assist";
    assist.hidden = true;
    assist.innerHTML = `
      <div class="table-scroll-assist__label">Плъзни таблицата наляво и надясно</div>
      <div class="table-scroll-assist__track" aria-hidden="true">
        <div class="table-scroll-assist__thumb"></div>
      </div>
    `.trim();

    scrollArea.parentNode.insertBefore(assist, scrollArea);

    const track = assist.querySelector(".table-scroll-assist__track");
    const thumb = assist.querySelector(".table-scroll-assist__thumb");
    const assistKey = `table-scroll-assist-${index + 1}`;
    let dragging = false;
    let startX = 0;
    let startScrollLeft = 0;
    let activePointerId = null;

    const update = () => {
      const maxScroll = scrollArea.scrollWidth - scrollArea.clientWidth;
      const isScrollable = maxScroll > 6;
      assist.hidden = !isScrollable;

      if (!isScrollable) {
        return;
      }

      const trackWidth = track.clientWidth;
      const thumbWidth = Math.max(trackWidth * (scrollArea.clientWidth / scrollArea.scrollWidth), 54);
      const maxThumbOffset = Math.max(trackWidth - thumbWidth, 0);
      const thumbOffset = maxScroll > 0 ? (scrollArea.scrollLeft / maxScroll) * maxThumbOffset : 0;

      assist.dataset.assistKey = assistKey;
      thumb.style.width = `${thumbWidth}px`;
      thumb.style.transform = `translateX(${thumbOffset}px)`;
    };

    const beginDrag = (event) => {
      dragging = true;
      activePointerId = event.pointerId;
      startX = event.clientX;
      startScrollLeft = scrollArea.scrollLeft;
      track.classList.add("is-dragging");
      if (track.setPointerCapture) {
        track.setPointerCapture(activePointerId);
      }
      event.preventDefault();
    };

    const endDrag = () => {
      dragging = false;
      track.classList.remove("is-dragging");
      if (activePointerId !== null && track.releasePointerCapture) {
        track.releasePointerCapture(activePointerId);
      }
      activePointerId = null;
    };

    track.addEventListener("pointerdown", (event) => {
      const rect = track.getBoundingClientRect();
      const thumbRect = thumb.getBoundingClientRect();
      const clickedThumb = event.clientX >= thumbRect.left && event.clientX <= thumbRect.right;

      if (!clickedThumb) {
        const trackWidth = rect.width;
        const thumbWidth = thumb.offsetWidth;
        const maxThumbOffset = Math.max(trackWidth - thumbWidth, 1);
        const targetOffset = Math.min(Math.max((event.clientX - rect.left) - (thumbWidth / 2), 0), maxThumbOffset);
        const maxScroll = Math.max(scrollArea.scrollWidth - scrollArea.clientWidth, 0);
        scrollArea.scrollLeft = (targetOffset / maxThumbOffset) * maxScroll;
        update();
      }

      beginDrag(event);
    });

    track.addEventListener("pointermove", (event) => {
      if (!dragging) {
        return;
      }

      const maxScroll = scrollArea.scrollWidth - scrollArea.clientWidth;
      const maxThumbOffset = Math.max(track.clientWidth - thumb.offsetWidth, 1);
      const deltaX = event.clientX - startX;
      const scrollDelta = (deltaX / maxThumbOffset) * maxScroll;

      scrollArea.scrollLeft = startScrollLeft + scrollDelta;
      update();
    });

    track.addEventListener("pointerup", endDrag);
    track.addEventListener("pointercancel", endDrag);
    track.addEventListener("lostpointercapture", endDrag);
    scrollArea.addEventListener("scroll", update, { passive: true });
    window.addEventListener("resize", update);

    if ("ResizeObserver" in window) {
      const observer = new ResizeObserver(update);
      observer.observe(scrollArea);
      observer.observe(table);
    }

    update();
  });
}

document.addEventListener("DOMContentLoaded", () => {
  const syncNatalCity = bindCitySync({
    citySelectId: "cityName",
    latitudeDegreesId: "latitudeDegrees",
    latitudeMinutesId: "latitudeMinutes",
    latitudeHemisphereId: "latitudeHemisphere",
    longitudeDegreesId: "longitudeDegrees",
    longitudeMinutesId: "longitudeMinutes",
    longitudeHemisphereId: "longitudeHemisphere",
  });

  const syncTransitCity = bindCitySync({
    citySelectId: "transitCityName",
    latitudeDegreesId: "transitLatitudeDegrees",
    latitudeMinutesId: "transitLatitudeMinutes",
    latitudeHemisphereId: "transitLatitudeHemisphere",
    longitudeDegreesId: "transitLongitudeDegrees",
    longitudeMinutesId: "transitLongitudeMinutes",
    longitudeHemisphereId: "transitLongitudeHemisphere",
  });

  const maybeSyncIfBlank = (fieldIds, syncFn) => {
    const shouldSync = fieldIds.some((fieldId) => {
      const field = document.getElementById(fieldId);
      return field && field.value.trim() === "";
    });

    if (shouldSync) {
      syncFn();
    }
  };

  maybeSyncIfBlank(
    [
      "latitudeDegrees",
      "latitudeMinutes",
      "latitudeHemisphere",
      "longitudeDegrees",
      "longitudeMinutes",
      "longitudeHemisphere",
    ],
    syncNatalCity,
  );

  maybeSyncIfBlank(
    [
      "transitLatitudeDegrees",
      "transitLatitudeMinutes",
      "transitLatitudeHemisphere",
      "transitLongitudeDegrees",
      "transitLongitudeMinutes",
      "transitLongitudeHemisphere",
    ],
    syncTransitCity,
  );

  bindTimezoneMode("timezoneMode", "manualTimezoneFields");
  bindTimezoneMode("transitTimezoneMode", "transitManualTimezoneFields");
  bindTableScrollAssist();
  bindChartRotation();
  bindChartLightbox();
});
