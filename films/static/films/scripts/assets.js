/* global ajax:false */

window.asset = (function asset() {
	document.addEventListener('DOMContentLoaded', () => {
		document.querySelectorAll(
			'.file a[data-toggle*="modal"], .grid a[data-toggle*="modal"]'
		).forEach(element => {
			element.addEventListener('click', () => getModalHtml(element));
		});
	});

	function getModalHtml(element) {
		fetch(element.dataset.url).then(response => {
			return response.text();
		}).then(html => {
			createModal(html, 'file-modal');
		}).catch(err => {
			console.warn('Something went wrong.', err);
		});
	}

	function getZoomModalHtml(element) {
		fetch(element.dataset.url).then(response => {
			return response.text();
		}).then(html => {
			createZoomModal(html, 'file-zoom-modal');
			// addButtonClickEvent();
		}).catch(err => {
			console.warn('Something went wrong.', err);
		});
	}

	function createModal(html, elementId) {
		const template = document.createElement('template');
		template.innerHTML = html.trim();

		const modal = document.getElementById(elementId);
		if (modal.childElementCount === 0) {
			modal.appendChild(template.content);
		} else {
			modal.children[0].replaceWith(template.content);
		}
		$(modal).on('hidden.bs.modal', event => {
			modal.innerHTML = "";
		});
		//TODO(Mike): When Bootstrap 5 is added, switch to regular JS.
		// modal.addEventListener('hidden.bs.modal', event =>{
		// 	modal.innerHTML="";
		// })
		addButtonClickEvent();
	}

	function createZoomModal(html, elementId) {
		const base_modal = document.getElementById('file-modal');
		$(base_modal).modal('hide');  // removes all the children :/

		const template = document.createElement('template');
		template.innerHTML = html.trim();

		const modal = document.getElementById('file-zoom-modal');
		if (modal.childElementCount === 0) {
			modal.appendChild(template.content);
		} else {
			modal.children[0].replaceWith(template.content);
		}
		$(modal).on('hidden.bs.modal', event => {
			modal.innerHTML = "";
			$(base_modal).modal('show');  // empty modal background, no children
		});
	}

	function addButtonClickEvent() {
		document.querySelectorAll(
			'.modal button.previous, .modal button.next'
		).forEach(button => {
			button.addEventListener('click', () => getModalHtml(button));
		});
		document.querySelectorAll(
			'.modal a[data-toggle*="modal"]'
		).forEach(element => {
			element.addEventListener('click', () => getZoomModalHtml(element));
		});
	}
})();
