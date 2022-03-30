function observeAndPreviewField(formElement) {
  // Listen to changes in field and generate preview
  let timeoutID;
  // let formElementId = 'id_summary';
  formElement.addEventListener('input', function(e) {
    clearTimeout(timeoutID);
    timeoutID = setTimeout(function() {
      fetchMarkdownPreview(formElement.id);
    }, 1000);
  });
}

function fetchMarkdownPreview(formElementId) {
  let data = {markdown: document.getElementById(formElementId).value};
  ajax.jsonRequest('POST', '/api/markdown-preview', data).then((r) => {
    let div = document.getElementById('markdown-preview-container');
    div.innerHTML = r.html;
  });
}

function initPreview(fieldId) {
  formElement = document.getElementById(fieldId);
  if (!formElement) return;
  observeAndPreviewField(formElement);
}

let formElement = null;
const possibleFieldIds = ['id_summary', 'id_text', 'id_description', 'id_content'];
possibleFieldIds.forEach(initPreview);
