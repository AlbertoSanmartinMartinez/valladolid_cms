
/*
Modal Functionalitiy
*/

function openCustomModal(url) {
  $('#custom-modal').load(url, function() {
    $(this).modal('show');
  });
  return false;
}

function closeCustomModal() {
  $('#custom-modal').modal('hide');
  return false;

}

/*
Schedule Form & Period Schedule Formset JS
*/

function walkTheDOM(node, func) {
  func(node);
  node = node.firstChild;
  while (node) {
    walkTheDOM(node, func);
    node = node.nextSibling;
  }
}

function updateFormSet(node) {
  console.log("update period schedule form");

  function updateForm(currentNode) {

    var current_node_id = String(currentNode.id)

    var index_forms = Number(document.getElementById("index-forms").value);

    if (current_node_id.startsWith('period-schedule-form-')) {
      console.log(index_forms)
      currentNode.id = 'period-schedule-form-' + index_forms;
      document.getElementById("index-forms").value = index_forms + 1;
    }
    if (current_node_id.startsWith('-dia', 9)) {
      currentNode.id = 'id_form-' + String(index_forms - 1) + '-dia';
      currentNode.name = "form-" + String(index_forms - 1) + "-dia";
    }
    if (current_node_id.startsWith('-inicio', 9)) {
      currentNode.id = 'id_form-' + String(index_forms - 1) + '-inicio';
      currentNode.name = "form-" + String(index_forms - 1) + "-inicio";
    }
    if (current_node_id.startsWith('-fin', 9)) {
      currentNode.id = 'id_form-' + String(index_forms - 1) + '-fin';
      currentNode.name = "form-" + String(index_forms - 1) + "-fin";
    }
  }

  walkTheDOM(node, updateForm);
}

$(document).on('click', '.delete-form', function() {
  console.log("delete period schedule form")

  if (Number(document.getElementById("id_form-TOTAL_FORMS").value) > 1) {

    var form_id = ($(this).attr("data-target"))
    var form = document.getElementById("period-schedule-form-" + form_id);
    var formset = document.getElementById("period-schedule-formset");

    formset.removeChild(form);
    updateFormSet(formset);

    document.getElementById("id_form-TOTAL_FORMS").value = Number(document.getElementById("index-forms").value);
    document.getElementById("index-forms").value = 0;
  }
});

$(document).on('click', '.add-form', function(e) {
  console.log("add period schedule form")

  e.preventDefault();

  var form = document.getElementById("period-schedule-form-0");
  var formset = document.getElementById("period-schedule-formset");
  var copy = form.cloneNode(true);

  formset.appendChild(copy);
  updateFormSet(formset);

  document.getElementById("id_form-TOTAL_FORMS").value = Number(document.getElementById("index-forms").value);
  document.getElementById("index-forms").value = 0;
});
