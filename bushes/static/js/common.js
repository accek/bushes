function arrayToString(array) {
    var copy = array.slice(0);
    for (var i = 0; i < copy.length; i++) {
        if (copy[i] == null) {
            copy[i] = '';
        }
    }
    return copy.join(',');
}

function stringToArray(str) {
    if (str == null || str == undefined || str == '') {
        return [];
    }
    var array = str.split(',');
    for (var i = 0; i < array.length; i++) {
        if (array[i] == '') {
            array[i] = null;
        } else {
            array[i] = parseInt(array[i]);
        }
    }
    return array;
}

function localStorageGetList(key) {
    return stringToArray(localStorage[key]);
}

function localStorageSetList(key, list) {
    localStorage[key] = arrayToString(list);
}

function localStorageAddToList(key, element) {
    var list = localStorageGetList(key);
    if (list.indexOf(element) == -1) {
        list.push(element);
        localStorageSetList(key, list);
    }
}

function localStorageRemoveFromList(key, element) {
    var list = localStorageGetList(key);
    var index = list.indexOf(element);
    if (index != -1) {
        list.splice(index, 1);
        localStorageSetList(key, list);
    }
}

function localStorageInList(key, element) {
    var list = localStorageGetList(key);
    return list.indexOf(element) != -1;
}

function supports_html5_storage() {
  try {
    return 'localStorage' in window && window['localStorage'] !== null;
  } catch (e) {
    return false;
  }
}

function check_browser() {
  return supports_html5_storage();
}
