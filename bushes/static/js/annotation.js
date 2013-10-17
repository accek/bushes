function initAnnotation(username, tokens, parents, assignment_id, ready) {
    var parseview = new ParseView($('#parseview'));
    parseview.init(tokens);

    var ready_armed = false;

    console.log(localStorageGetList('ready_assignments'));

    var key = 'ass_' + assignment_id;

    if (parents && ready) {
        parseview.setParents(parents);
    } else {
        var set_parents = false;
        try {
            var saved_parents = localStorageGetList(key);
            if (saved_parents.length > 0) {
                parseview.setParents(saved_parents);
                set_parents = true;
            }
        } catch (e) {
            console.log("Error restoring parents: " + e);
        }
        if (!set_parents && parents) {
            try {
                parseview.setParents(parents);
            } catch (e) {
                console.log("Error restoring parents from server: " + e);
            }
        }
    }

    if (localStorageInList('ready_assignments', assignment_id)) {
        ready = true;
    }

    if (ready) {
        parseview.setMode('readonly');
    }

    function updateState() {
        $('#tool_split').toggleClass('active', parseview.mode == 'split');
        $('#tool_split').toggleClass('btn-warning', parseview.mode == 'split');
        $('#tool_undo').prop('disabled', !parseview.canUndo());
        $('#tool_redo').prop('disabled', !parseview.canRedo());
        $('#notready_actions').toggle(!ready);
        $('#ready_actions').toggle(ready);

        var jready = $('#tool_ready');
        if (ready_armed) {
            jready.addClass('btn-danger').removeClass('btn-success').text("Potwierdź");
        } else {
            jready.removeClass('btn-danger').addClass('btn-success').text("Gotowe!");
        }

        $('body').toggleClass('ready', ready);

        if (!ready) {
            localStorageSetList(key, parseview.getParents());
        }
    }

    $('#tool_split').click(function() {
        if (parseview.mode == 'join') {
            parseview.setMode('split');
        } else {
            parseview.setMode('join');
        }
    });

    $('#tool_undo').click(function() { parseview.undo(); });
    $('#tool_redo').click(function() { parseview.redo(); });

    $('#tool_next').click(function() {
        try {
            var assignments = JSON.parse(localStorage['assignments']);
            var ready_assignments = localStorageGetList('ready_assignments');
            for (var assignment in assignments) {
                assignment = parseInt(assignment);
                if (ready_assignments.indexOf(assignment) == -1) {
                    window.location.href = assignment;
                    return;
                }
            }
        } catch (e) {
        }
        window.location.href = '/';
    });

    $(document).click(function() {
        if (ready_armed) {
            ready_armed = false;
            updateState();
        }
    });

    $('#tool_ready').click(function(e) {
        e.stopPropagation();
        if (ready_armed) {
            ready = true;
            parseview.setMode('readonly');
            localStorageAddToList('ready_assignments', assignment_id);
        } else {
            ready_armed = true;
        }
        updateState();
    });

    parseview.registerUpdateHandler(updateState);
    updateState();
}
