var CLIENT_URL = "/admin/users/client/"
var ORDER_URL = "/admin/orders/order/"

// This function adds a `Create Order` button on Client's Requests Tab.
// When user clicks on this button - we are redirecting him to POS system.
function addCreateOrderButton() {
  function createButton(clientId, requestId) {
    var url = '/admin/pos/?client_id=' + clientId + '&request_id=' + requestId
    var button = (
      "<a href='" + url + "' target='_blank'><input type='button' value='CREATE ORDER'></a>"
    )

    return button
  }

  var ALL_REQUEST_SELECTOR = '#request_list-group fieldset.module td.original.empty'
  var allRows = document.querySelectorAll(ALL_REQUEST_SELECTOR)

  function callback(item, index) {
    var inputList = item.querySelectorAll('input')
    var parent = item.parentElement

    var requestElement = inputList[0]
    var clientElement = inputList[1]

    var requestId = Number(requestElement.value)
    var clientId = Number(clientElement.value)

    var newTdRow = document.createElement('td')
    var createOrderButton = createButton(clientId, requestId)
    newTdRow.className = 'create-order'
    newTdRow.innerHTML = createOrderButton

    parent.appendChild(newTdRow)
  }

  allRows.forEach(callback)
}


function fillOrderPaymentWithColor() {
  var ALL_ORDER_SELECTOR = '#result_list > tbody > tr'
  var allRows = document.querySelectorAll(ALL_ORDER_SELECTOR)

  function callback(row, index) {
    var paymentField = row.querySelector('td.field-payment')
    var isPaid = paymentField.innerHTML === "Paid"
    var rowColor = "red"

    if (isPaid) {
      rowColor = "green"
    }

    row.style.backgroundColor = rowColor
  }

  allRows.forEach(callback)
}


if (window.location.pathname.search(CLIENT_URL) !== -1) {
  // We are waiting 1s while HTML is loading
  setTimeout(addCreateOrderButton, 1000)
}

if (window.location.pathname === ORDER_URL) {
  // We are waiting 1s while HTML is loading
  setTimeout(fillOrderPaymentWithColor, 1000)
}

