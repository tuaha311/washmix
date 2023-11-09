// urls
var CLIENT_URL = "/admin/users/client/"
var ORDER_URL = "/admin/orders/order/"
var DELIVERY_URL = "/admin/deliveries/delivery/"
var ARCHIEVED_DELIVERY_URL = "/admin/archived/archiveddelivery/"

// colors
var PAID_ORDER_COLOR = "green"
var UNPAID_ORDER_COLOR = "red"
var RUSH_DELIVERY_COLOR = "yellow"
var CLIENT_WITHOUT_CARD_COLOR = "red"
var DELIVERIES_DUE_TODAY = "orange"
var INSTORE_DELIVERIES = "#39b6ed"


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

// Hiding send sms Button from Admin panel (Drawer)
function hideSendSMSLink() {
  var sendSMSLink = document.querySelector('a[href="/admin/sms/sendsms/"]');
  var smsTemplateLink = document.querySelector('a[href="/admin/sms/smstemplate/"]');
  if (sendSMSLink) {
    sendSMSLink.parentElement.style.display = "none";
  }
  if (smsTemplateLink) {
    smsTemplateLink.innerHTML = "Outbound SMS";
  }
}

if (window.location.pathname.indexOf('/admin') !== -1) {
  setTimeout(hideSendSMSLink, 1000);
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
      }
      if (formed === false){
        newElement = createButton(clientId, requestId)
      }

      if (newElement) {
         parent.appendChild(newElement)
      }
    }
  )
}


/*
  Client's page
*/

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

// This function works at Deliveries list page - /admin/deliveries/delivery/.
// We are filling rush deliveries with yellow color
function fillClientWithoutCardWithColor() {
  var ALL_ORDER_SELECTOR = '#result_list > tbody > tr'
  var allRows = document.querySelectorAll(ALL_ORDER_SELECTOR)

  function callback(row, index) {
    var cardField = row.querySelector('td.field-has_card')
    var hasNotCard = cardField.innerHTML === "False"

    if (hasNotCard) {
      row.style.backgroundColor = CLIENT_WITHOUT_CARD_COLOR
    }

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
    var rowColor = UNPAID_ORDER_COLOR

    if (isPaid) {
      rowColor = PAID_ORDER_COLOR
    }

    row.style.backgroundColor = rowColor
  }

  allRows.forEach(callback)
}


/*
  Deliveries page
*/

// This function works at Deliveries list page - /admin/deliveries/delivery/.
// We are filling rush deliveries with yellow color
function fillRushDeliveryWithColor() {
  var ALL_ORDER_SELECTOR = '#result_list > tbody > tr'
  var allRows = document.querySelectorAll(ALL_ORDER_SELECTOR)
  var today = new Date();
  var dd = String(today.getDate()).padStart(2, '0');
  var mm = String(today.getMonth() + 1).padStart(2, '0');
  var yyyy = today.getFullYear();
  today = mm + '/' + dd + '/' + yyyy;

  function callback(row, index) {
    var rushField = row.querySelector('td.field-is_rush')
    var isRush = rushField.innerHTML === "True"

    var rowDate = row.querySelector(`#id_form-${index}-date`).value
    var isDateToday = today === rowDate

    if(isDateToday) {
      row.style.backgroundColor = DELIVERIES_DUE_TODAY
    }
    if (isRush) {
      row.style.backgroundColor = RUSH_DELIVERY_COLOR
    }

  }

  allRows.forEach(callback)
}

// simple router
if (window.location.pathname.search(CLIENT_URL) !== -1) {
  // We are waiting 1s while HTML is loading
  setTimeout(addCreateOrderButton, 1000)
  setTimeout(fillClientWithoutCardWithColor, 1000)
}

if (window.location.pathname === ORDER_URL) {
  // We are waiting 1s while HTML is loading
  setTimeout(fillOrderPaymentWithColor, 1000)
}

if (window.location.pathname === DELIVERY_URL) {
  // We are waiting 1s while HTML is loading
  setTimeout(fillRushDeliveryWithColor, 1000)
}


function fillInstoreDeliveryWithColor() {
  var ALL_ORDER_SELECTOR = '#result_list > tbody > tr'
  var allRows = document.querySelectorAll(ALL_ORDER_SELECTOR)

  function callback(row, index) {
    var commentField = row.querySelector('td.field-comment')
    var currentStatus = row.querySelector('td.field-status')
    var kindOfDelivery = row.querySelector('td.field-kind')
    var inStoreDelivery = commentField.innerText === "In store request"
    var pickupDelivery = kindOfDelivery.innerText === "Pickup"
    var dropoffDelivery = kindOfDelivery.innerText === "Dropoff"

    if (inStoreDelivery) {
      row.style.backgroundColor = INSTORE_DELIVERIES
      if (pickupDelivery) {
        // Hide the "No Show" option
        var selectElement = currentStatus.querySelector('select');
        if (selectElement) {
          var options = selectElement.querySelectorAll('option');
          options.forEach(function(option) {
            if (option.value === 'no_show') {
              selectElement.removeChild(option);
            }
            if (option.value === 'in_store_dropoff') {
              selectElement.removeChild(option);
            }
            if (option.value === 'cancelled') {
              selectElement.removeChild(option);
            }
          });
        }
      }
      if (dropoffDelivery) {
        // Hide the "No Show" option
        var selectElement = currentStatus.querySelector('select');
        if (selectElement) {
          var options = selectElement.querySelectorAll('option');
          options.forEach(function(option) {
            if (option.value === 'in_store_pickup') {
              selectElement.removeChild(option);
            }
          });
        }
      }
    }else{
      var selectElement = currentStatus.querySelector('select');
        if (selectElement) {
          var options = selectElement.querySelectorAll('option');
          options.forEach(function(option) {
            if (option.value === 'in_store_pickup') {
              selectElement.removeChild(option);
            }
            if (option.value === 'in_store_dropoff') {
              selectElement.removeChild(option);
            }
          });
        }
    }
  }

  allRows.forEach(callback)
}

if (window.location.pathname === DELIVERY_URL) {
  // We are waiting 1s while HTML is loading
  setTimeout(fillRushDeliveryWithColor, 1000)
  setTimeout(fillInstoreDeliveryWithColor, 1000)
}

if (window.location.pathname === ARCHIEVED_DELIVERY_URL) {
  // We are waiting 1s while HTML is loading
  setTimeout(fillInstoreDeliveryWithColor, 1000)
}
