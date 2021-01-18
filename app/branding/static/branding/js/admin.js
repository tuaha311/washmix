var CLIENT_URL = "/admin/users/client/"
var ORDER_URL = "/admin/orders/order/"


/*
POS page
*/

// creates button `Create Order`
function createButton(clientId, requestId) {
  var newTdRow = document.createElement('td')

  var url = '/admin/pos/?client_id=' + clientId + '&request_id=' + requestId
  var button = (
    "<a href='" + url + "' target='_blank'><input type='button' value='CREATE ORDER'></a>"
  )

  newTdRow.className = 'create-order'
  newTdRow.innerHTML = button

  return newTdRow
}


// creates link that point on order
function createLink(orderId) {
  var newTdRow = document.createElement('td')

  var url = '/admin/orders/order/' + orderId + '/change/'
  var value = 'Order #' + orderId
  var link = (
    "<a href='" + url + "' target='_blank'>" + value +"</a>"
  )

  newTdRow.className = 'link'
  newTdRow.innerHTML = link

  return newTdRow
}



// handles button or link creation on Client's page
function handleOrderIsAlreadyFormed(clientId, requestId, parent) {
  jQuery.get(
    "/api/pos/orders/already_formed/",
    {
      "client": clientId,
      "request": requestId
    },
    function (jsonResponse) {
      var newElement;
      var formed = jsonResponse.formed
      var order = jsonResponse.order

      if (formed === true) {
        newElement = createLink(order)
      } else {
        newElement = createButton(clientId, requestId)
      }

      parent.appendChild(newElement)
    }
  )
}


// This function adds a `Create Order` button on Client's Requests Tab.
// If order is not formed - we are adding `Create Button`. When user clicks on this button
// - we are redirecting him to POS system.
// If formed - we are adding a link to the order.
function addCreateOrderButton() {
  var ALL_REQUEST_SELECTOR = '#request_list-group fieldset.module td.original.empty'
  var allRows = document.querySelectorAll(ALL_REQUEST_SELECTOR)

  function callback(item, index) {
    var inputList = item.querySelectorAll('input')
    var parent = item.parentElement

    var requestElement = inputList[0]
    var clientElement = inputList[1]

    var requestId = Number(requestElement.value)
    var clientId = Number(clientElement.value)

    handleOrderIsAlreadyFormed(clientId, requestId, parent)
  }

  allRows.forEach(callback)
}

/*
Orders page
*/

// This function works at Orders list page - /admin/orders/order/.
// We are filling paid orders with green color and with red if order is unpaid.
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


// simple router
if (window.location.pathname.search(CLIENT_URL) !== -1) {
  // We are waiting 1s while HTML is loading
  setTimeout(addCreateOrderButton, 1000)
}

if (window.location.pathname === ORDER_URL) {
  // We are waiting 1s while HTML is loading
  setTimeout(fillOrderPaymentWithColor, 1000)
}

