// Masonry for the card stream. Each card spans as many 1px grid rows as it
// is tall, so it tucks under the shortest card above it while the reading
// order stays left to right. It runs inline right after the grid, before
// first paint, and a ResizeObserver re-spans cards when fonts land or the
// column width changes. Browsers with native masonry skip all of this.
(() => {
  const grid = document.querySelector(".stream");
  if (!grid || CSS.supports("display", "grid-lanes")) return;
  const cards = [...grid.children];
  const place = () => {
    const gap = parseFloat(getComputedStyle(grid).getPropertyValue("--gap"));
    for (const card of cards) {
      card.style.gridRowEnd = `span ${Math.ceil(card.offsetHeight + gap)}`;
    }
  };
  grid.classList.add("is-masonry");
  place();
  const watch = new ResizeObserver(place);
  for (const card of cards) watch.observe(card);
})();
