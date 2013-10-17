function SyncController(progress) {
    this.progress = progress;
    this.oncomplete = null;
    this.onerror = null;
}

SyncController.prototype.start = function() {
    var ready_assignments = localStorageGetList('ready_assignments');
    var index = -1;
    var self = this;

    console.log("Assignments to send (" + ready_assignments.length + "): " + ready_assignments);

    function failed(message) {
        var text = "Błąd podczas przesyłania drzewa";
        if (message) {
            text += ": " + message
        }
        if (self.progress) {
            self.progress.failed(text);
        }
        if (self.onerror) {
            self.onerror();
        }
    }

    function next() {
        index++;
        if (index == ready_assignments.length) {
            if (self.progress) {
                self.progress.done();
            }
            if (self.oncomplete) {
                self.oncomplete();
            }
            return;
        }
        if (self.progress) {
            self.progress.setProgress(index, ready_assignments.length);
        }

        var id = ready_assignments[index];
        var key = 'ass_' + id;
        var parents = localStorageGetList(key);
        var data = { 'id': id, 'parents': parents };

        console.log("Uploading #" + id);
        
        $.ajax({
            url: '/upload',
            type: 'POST',
            contentType: 'application/json; charset=utf-8',
            data: JSON.stringify(data),
            dataType: 'text',
            success: function(result) {
                if (result == 'OK') {
                    console.log("Uploaded assignment #" + id);
                    localStorageRemoveFromList('ready_assignments', id);
                    delete localStorage[key];
                    $('#row_' + id).hide();
                    next();
                } else {
                    console.log(result);
                    failed();
                }
            },
            error: function(xhr, text_status, error) {
                console.log(error);
                failed(error);
            }
        });
    }

    next();
}
