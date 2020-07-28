/* global ajax:false */

window.asset = (function asset() {
  const baseModalId = 'file-modal';
  const zoomModalId = 'file-zoom-modal';

  document.addEventListener('DOMContentLoaded', () => {
    addFileClickEvent();
    initalizeAssetURL();
  });

  window.addEventListener('popstate', (event) => {


    const fileElementSelector = document.querySelector('[data-asset-id="' + event.state + '"]');

    $('#file-zoom-modal').modal('hide');
    if (event.state == "") {
      //The empty state occurs when the modal is closed, so it hides the modal.
      $('#file-modal').modal('hide');
    } else if (event.state == null) {
      //When pasting a new URL the state is lost which causes an error, which this handles by just using the URL.
      initalizeAssetURL();
      $('#file-modal').modal('show');
    } else {
      loadingSpinner(document.querySelector('#' + baseModalId));
      getModalHtml(fileElementSelector, baseModalId, event);
      $('#file-modal').modal('show');
    }
  });

  // Using Jquery due to BootStrap events only being available here.
  // TODO(Mike): When Bootstrap 5 is added, switch to regular JS.
  $(document).ready(function () {
    $('#file-modal').each(function (i) {
      // Remove modal content on hide
      $(this).on('hidden.bs.modal', event => {
        $(this).empty();
        if (this.classList.contains('modal-asset')) {
          // Add loading spinner pre-emtively
          loadingSpinner(this);
        }
      });

      // Give modal focus on open
      $(this).on('shown.bs.modal', function () {
        $(this).trigger('focus')
      })

      // Events for clicking close or ESC, cant use hiden.bs.modal as this is also triggered by going back in history.
      $(this).on('keydown.dismiss.bs.modal click.dismiss.bs.modal', () => {
        removeURLParam('asset');
      });

    })
    // Left-Right keyboard events
    $('#file-modal').keydown(function (event) {
      switch (event.key) {
        case "ArrowRight":
          $('#file-modal .modal-navigation.next').trigger('click');
          break;
        case "ArrowLeft":
          $('#file-modal .modal-navigation.previous').trigger('click');
          break;
      }
    });
  });

  function initalizeAssetURL() {
    const urlParams = new URLSearchParams(window.location.search);
    const assetParam = urlParams.get('asset');
    const assetElem = document.querySelector('[data-asset-id="' + assetParam + '"]')

    if (assetParam != null && assetElem != null) {
      assetElem.click();
    }
  }

  function addURLParam(param, value) {
    let url = new URL(window.location);
    const title = document.title;
    const state = value;
    const newparam = '?' + param + '=' + value;
    //When going back, it checks the state against the url before pushing it - otherwise the pop-stack gets over-ridden and you cant go forward in time.
    if (url.search != newparam) {
      url.searchParams.set(param, value);
      window.history.pushState(state, title, url);
    }
  }

  function removeURLParam(param) {
    let url = new URL(window.location);
    const title = document.title;
    const state = '';

    url.searchParams.delete(param);
    window.history.pushState(state, title, url);
  }

  function addFileClickEvent() {
    document.querySelectorAll(
      '.file a[data-toggle*="modal"], .grid a[data-toggle*="modal"]'
    ).forEach(element => {
      element.addEventListener('click', (event) => getModalHtml(element, baseModalId, event));
    });
  }

  function loadingSpinner(element) {
    const spinner = '<div class="spinner-border text-primary" role="status"><span class="sr-only">Loading...</span></div>';
    const close = '<button class="modal-navigation modal-close btn btn-ctrl d-none d-md-block" data-dismiss="modal"><i class="material-icons btn-material-icons">close</i></button>'
    element.innerHTML = spinner + close;
  }

  function getModalHtml(element, modalId, event) {
    if (element.classList.contains('modal-navigation')) {
      loadingSpinner(document.querySelector('#' + baseModalId))
    }

    fetch(element.dataset.url).then(response => {
      return response.text();
    }).then(html => {
      createModal(html, modalId, element.dataset.assetId, event);
    }).then(() => {
      // Create a new video player for the modal
      const player = new Plyr(document.querySelector('.video-player video'));
      document.querySelector('.modal').focus();

      // Trigger activation of comment event listeners
      activateComments();
      $('[data-toggle="tooltip"]').tooltip();

    }).catch(err => {
      console.warn('Something went wrong.', err);
    });
  }

  function createModal(html, modalId, assetId, event) {
    const template = document.createElement('template');
    template.innerHTML = html.trim();
    const modal = document.getElementById(modalId);
    if (modal.childElementCount === 0) {
      modal.appendChild(template.content);
    } else {
      modal.children[0].replaceWith(template.content);
    }

    if (modalId === baseModalId) {
      addButtonClickEvent();
      if (event.type != "popstate") {
        addURLParam('asset', assetId);
      }
    }
  }

  function addButtonClickEvent() {

    document.querySelectorAll(
      '.modal button.previous, .modal button.next'
    ).forEach(button => {
      button.addEventListener(
        'click', (event) => getModalHtml(button, baseModalId, event)
      );
    });

    document.querySelectorAll(
      '.modal a[data-toggle*="modal"]'
    ).forEach(element => {
      element.addEventListener(
        'click', (event) => getModalHtml(element, zoomModalId, event)
      );
    });

  }

  function activateComments() {
    const event = new CustomEvent('activateComments', { bubbles: true });
    document.querySelector('.modal').dispatchEvent(event);
  }
})();
