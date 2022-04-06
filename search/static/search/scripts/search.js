/* eslint-disable no-undef, no-unused-vars, no-nested-ternary */
const searchClientConfig = JSON.parse(document.getElementById('search-client-config').textContent);

const indexName = 'studio';
const search = instantsearch({
  indexName,
  searchClient: instantMeiliSearch(searchClientConfig.hostUrl, searchClientConfig.apiKey),
  routing: {
    stateMapping: {
      stateToRoute(uiState) {
        const indexUiState = uiState[indexName];
        return {
          query: indexUiState.query,
          type: indexUiState.menu && indexUiState.menu.model,
          media_type: indexUiState.menu && indexUiState.menu.media_type,
          // license: indexUiState.menu && indexUiState.menu.license,
          film_title: indexUiState.menu && indexUiState.menu.film_title,
          sortBy: indexUiState && indexUiState.sortBy,
        };
      },
      routeToState(routeState) {
        return {
          [indexName]: {
            query: routeState.query,
            sortBy: routeState.sortBy,
            menu: {
              model: routeState.type,
              categories: routeState.categories,
              media_type: routeState.media_type,
              // license: routeState.license,
              film_title: routeState.film_title,
            },
          },
        };
      },
    },
  },
});

// -------- INPUT -------- //

// Create a render function
const renderSearchBox = (renderOptions, isFirstRender) => {
  const { query, refine, clear, isSearchStalled, widgetParams } = renderOptions;

  if (isFirstRender) {
    const input = document.createElement('input');
    input.setAttribute('class', 'form-control');
    input.setAttribute('type', 'text');
    input.setAttribute('id', 'searchInput');
    input.setAttribute('placeholder', 'Search tags and keywords');

    // const loadingIndicator = document.createElement('span');
    // loadingIndicator.textContent = 'Loading...';

    const button = document.createElement('button');
    button.setAttribute('class', 'btn btn-icon btn-input');
    const buttonIcon = document.createElement('i');
    buttonIcon.setAttribute('class', 'material-icons');
    buttonIcon.textContent = 'close';
    button.appendChild(buttonIcon);

    input.addEventListener('input', (event) => {
      refine(event.target.value);
    });

    button.addEventListener('click', () => {
      clear();
    });

    const searchContainer = document.getElementById('search-container');

    searchContainer.insertAdjacentElement('beforeend', input);
    searchContainer.insertAdjacentElement('beforeend', button);
  }

  widgetParams.container.querySelector('input').value = query;
  // widgetParams.container.querySelector('span').hidden = !isSearchStalled;
};

// create custom widget
const customSearchBox = instantsearch.connectors.connectSearchBox(renderSearchBox);

// -------- SORTING -------- //

// Create the render function
const renderSortBy = (renderOptions, isFirstRender) => {
  const { options, currentRefinement, hasNoResults, refine, widgetParams } = renderOptions;

  if (isFirstRender) {
    const select = document.createElement('select');
    select.setAttribute('class', 'form-select');

    select.addEventListener('change', (event) => {
      refine(event.target.value);
    });

    widgetParams.container.insertAdjacentElement('beforeend', select);
  }

  const select = widgetParams.container.querySelector('select');

  select.disabled = hasNoResults;

  select.innerHTML = `
    ${options
      .map(
        (option) => `
          <option
            value="${option.value}"
            ${option.value === currentRefinement ? 'selected' : ''}
          >
            ${option.label}
          </option>
        `
      )
      .join('')}
  `;
};

// Create the custom widget
const customSortBy = instantsearch.connectors.connectSortBy(renderSortBy);

// -------- HITS -------- //

let lastRenderArgs;

// Create the render function
const renderHits = (renderOptions, isFirstRender) => {
  const { hits, showMore, widgetParams } = renderOptions;

  widgetParams.container.innerHTML = `
      ${hits
        .map(
          (item) =>
            `
<div class="card col-12 col-sm-6 col-lg-4 card-grid-item">
  <div class="card-header">
    <a class="card-header-link" href="${item.url}" aria-label="${item.name}">
      <img src="${item.thumbnail_url || fileIconURL}" class="${
              item.thumbnail_url ? 'card-img' : 'file-icon'
            }" loading=lazy aria-label="${item.name}">
    </a>
  </div>
  <a href="${item.url}" class="card-body">

    <h3 class="card-title">
      ${instantsearch.highlight({ attribute: 'name', hit: item })}
    </h3>
    <p class="card-text">
      ${instantsearch.highlight({ attribute: 'description', hit: item })}
    </p>
  </a>
  <a href="${item.url}" class="card-footer">
    <div class="card-subtitle-group">

      <p class="card-subtitle content-type">
        <i class="material-icons icon-inline small">category</i>&nbsp;
        ${item.model === 'section' ? item.training_name : item.model}
      </p>


      ${
        item.film_title
          ? `<p class="card-subtitle"><i class="material-icons icon-inline small">movie</i>&nbsp;${titleCase(
              item.film_title
            )}</p>`
          : ''
      }

      <p class="card-subtitle">
        <i class="material-icons icon-inline small">schedule</i>&nbsp;
        ${timeDifference(epochToDate(item.timestamp))}
      </p>

      ${
        item.is_free
          ? `
        <span class="badge badge-pill">Free</span>
      `
          : ''
      }
    </div>
  </a>
</div>
            `
        )
        .join('')}
  `;

  lastRenderArgs = renderOptions;

  if (isFirstRender) {
    const sentinel = document.createElement('div');
    widgetParams.container.insertAdjacentElement('afterend', sentinel);

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting && !lastRenderArgs.isLastPage) {
          showMore();
        }
      });
    });

    observer.observe(sentinel);
  }
};

const customHits = instantsearch.connectors.connectInfiniteHits(renderHits);

function valueNotEmpty(el) {
  if (el.value !== false || el.value !== null || el.value !== 0 || el.value !== '') {
    return el.value;
  }
  return null;
}

function filterEmpty(arr) {
  return arr.filter(valueNotEmpty);
}

// -------- FILTERS -------- //

// 1. Create a render function
const renderMenuSelect = (renderOptions, isFirstRender) => {
  const { items, canRefine, refine, widgetParams } = renderOptions;

  if (isFirstRender) {
    const select = document.createElement('select');

    select.setAttribute('class', 'form-select');
    select.addEventListener('change', (event) => {
      refine(event.target.value);
    });

    widgetParams.container.insertAdjacentElement('beforeend', select);
    // widgetParams.container.appendChild(select);
  }

  const select = widgetParams.container.querySelector('select');

  select.disabled = !canRefine;

  select.innerHTML = `
    <option value="">All</option>
    ${filterEmpty(items)
      .map(
        (item) =>
          `<option
            value="${item.value}"
            ${item.isRefined ? 'selected' : ''}
          >
            ${item.label}
          </option>`
      )
      .join('')}
  `;
};

// 2. Create the custom widget
const customMenuSelect = instantsearch.connectors.connectMenu(renderMenuSelect);

// -------- CONFIGURE -------- //

const renderConfigure = (renderOptions, isFirstRender) => {};

const customConfigure = instantsearch.connectors.connectConfigure(renderConfigure, () => {});

// -------- RENDER -------- //
let timerId;
search.addWidgets([
  customSearchBox({
    container: document.querySelector('#search-container'),
    queryHook(query, refine) {
      clearTimeout(timerId);
      // Throttle search requests to avoid search lagging in non-ideal network conditions.
      // (Or in case Studio is too slow to respond to a search request.)
      timerId = setTimeout(() => refine(query), 500);
    },
  }),
  customHits({
    container: document.querySelector('#hits'),
  }),
  // customMenu({
  //   container: document.querySelector('#filters'),
  //   attribute: 'categories',
  //   showMoreLimit: 20,
  // }),
  customMenuSelect({
    container: document.querySelector('#searchType'),
    attribute: 'model',
  }),
  // customMenuSelect({
  //   container: document.querySelector('#searchLicence'),
  //   attribute: 'license',
  // }),
  customMenuSelect({
    container: document.querySelector('#searchMedia'),
    attribute: 'media_type',
  }),
  customMenuSelect({
    container: document.querySelector('#searchFilm'),
    attribute: 'film_title',
    // There's no way to have no limit for menu items and showMore makes no sense for a dropdown
    // See https://www.algolia.com/doc/api-reference/widgets/menu/js/#widget-param-limit
    limit: 999,
  }),
  // customMenuSelect({
  //   container: document.querySelector('#searchFree'),
  //   attribute: 'free',
  // }),
  customSortBy({
    container: document.querySelector('#sorting'),
    items: [
      { label: 'Relevance', value: 'studio' },
      { label: 'Date (new first)', value: 'studio_date_desc' },
      { label: 'Date (old first)', value: 'studio_date_asc' },
    ],
  }),
  customSortBy({
    container: document.querySelector('#sorting-mobile'),
    items: [
      { label: 'Relevance', value: 'studio' },
      { label: 'Date (new first)', value: 'studio_date_asc' },
      { label: 'Date (old first)', value: 'studio_date_desc' },
    ],
  }),
  customConfigure({
    container: document.querySelector('#hits'),
    searchParameters: {
      hitsPerPage: 9,
    },
  }),
]);

search.start();

document.addEventListener('DOMContentLoaded', () => {
  document.querySelector('#searchInput').focus();
});
