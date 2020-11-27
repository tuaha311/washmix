function main() {
  function createButton(clientId, requestId) {
    var url = '/admin/pos/?client_id=' + clientId + '&request_id=' + requestId
    var button = (
      "<a href='" + url + "' target='_blank'><input type='button' value='CREATE ORDER'></a>"
    )

    return button
  }

  var ORIGINAL_SELECTOR = 'fieldset.module td.original.empty'
  var tdList = document.querySelectorAll(ORIGINAL_SELECTOR)

  function callback(item, index) {
    var inputList = item.querySelectorAll('input')
    var parent = item.parentElement
    var deleteButton = parent.lastElementChild

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

  tdList.forEach(callback)
}

setTimeout(main, 1000)
