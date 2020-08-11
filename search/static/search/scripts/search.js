const search = instantsearch({
  indexName: "studio",
  searchClient: instantMeiliSearch(
    "http://0.0.0.0:7700",
    //  TODO(Nat): api key goes here
  )
});

function timeDifference(datetime) {

  //TODO(Mike): When Natka adds new date-time formatting, fix processing.
  // console.log(datetime);

  let now = new Date();

  const msPerMinute = 60 * 1000;
  const msPerHour = msPerMinute * 60;
  const msPerDay = msPerHour * 24;
  const msPerMonth = msPerDay * 30;
  const msPerYear = msPerDay * 365;

  let elapsed = now - datetime;

  if (elapsed < msPerMinute) {
       return Math.round(elapsed/1000) + ' seconds ago';
  }

  else if (elapsed < msPerHour) {
       return Math.round(elapsed/msPerMinute) + ' minutes ago';
  }

  else if (elapsed < msPerDay ) {
       return Math.round(elapsed/msPerHour ) + ' hours ago';
  }

  else if (elapsed < msPerMonth) {
      return  Math.round(elapsed/msPerDay) + ' days ago';
  }

  else if (elapsed < msPerYear) {
      return  Math.round(elapsed/msPerMonth) + ' months ago';
  }

  else {
      return Math.round(elapsed/msPerYear ) + ' years ago';
  }
}

// -------- INPUT -------- //

// Create a render function
const renderSearchBox = (renderOptions, isFirstRender) => {
  const {
    query,
    refine,
    clear,
    isSearchStalled,
    widgetParams
  } = renderOptions;

  if (isFirstRender) {
    const input = document.createElement('input');
    input.setAttribute('class', 'form-control');
    input.setAttribute('type', 'text')
    input.setAttribute('placeholder', 'Search tags and keywords')

    //const loadingIndicator = document.createElement('span');
    //loadingIndicator.textContent = 'Loading...';

    const button = document.createElement('button');
    button.setAttribute('class', 'btn btn-icon btn-input');
    const buttonIcon = document.createElement('i');
    buttonIcon.setAttribute('class', 'material-icons');
    buttonIcon.textContent = 'close';
    button.appendChild(buttonIcon);

    input.addEventListener('input', event => {
      refine(event.target.value);
    });

    button.addEventListener('click', () => {
      clear();
    });

    widgetParams.container.querySelector('.input-group-append').insertAdjacentElement('beforebegin', input);
    //widgetParams.container.appendChild(loadingIndicator);
    widgetParams.container.querySelector('.input-group-append').appendChild(button);
  }

  widgetParams.container.querySelector('input').value = query;
  //widgetParams.container.querySelector('span').hidden = !isSearchStalled;
};

// create custom widget
const customSearchBox = instantsearch.connectors.connectSearchBox(
  renderSearchBox
);


// -------- HITS -------- //

// Create the render function
const renderHits = (renderOptions, isFirstRender) => {
  const { hits, widgetParams } = renderOptions;
  widgetParams.container.innerHTML = `

      ${hits
      .map(
        item =>
          `
          <div class="col-12 col-sm-6 col-lg-4 card-grid-item">
            <div class="card card-dark card-hover card-media">
              <div class="card-header">
                <a class="card-header-link" href="/${ item.url }">
                  <img src="${ item.thumbnail_url }" class="card-image" loading=lazy>
                </a>
              </div>
              <a href="/${ item.url }" class="card-body">
                <div class="card-subtitle-group">
                  <p class="card-subtitle content-type">
                  ${ item.model }
                  </p>

                  <p class="card-subtitle">
                    <i class="material-icons icon-inline small">schedule</i>
                    ${ timeDifference(item.date_created) }
                  </p>

                </div>
                <h3 class="card-title">
                  ${instantsearch.highlight({ attribute: 'name', hit: item })}
                </h3>
                <p class="card-text">
                  ${instantsearch.highlight({ attribute: 'description', hit: item })}
                </p>
              </a>
            </div>
          </div>
            `
      )
      .join('')}

  `;
};


const customHits = instantsearch.connectors.connectHits(renderHits);


// -------- FILTERS -------- //

// 1. Create a render function
const renderMenuSelect = (renderOptions, isFirstRender) => {
  const { items, canRefine, refine, widgetParams } = renderOptions;

  if (isFirstRender) {
    const select = document.createElement('select');

    select.setAttribute('class', 'custom-select');
    select.addEventListener('change', event => {
      refine(event.target.value);
    });

    widgetParams.container.querySelector('.input-group-prepend').insertAdjacentElement('afterend', select);
    // widgetParams.container.appendChild(select);
  }

  const select = widgetParams.container.querySelector('select');

  select.disabled = !canRefine;

  select.innerHTML = `
    <option value="">All</option>
    ${items
      .map(
        item =>
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


// -------- RENDER -------- //

search.addWidgets([
  customSearchBox({
    container: document.querySelector('#search-container'),
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
  customMenuSelect({
    container: document.querySelector('#searchLicence'),
    attribute: 'license',
  }),
  customMenuSelect({
    container: document.querySelector('#searchMedia'),
    attribute: 'media_type',
  }),
]);

search.start();
