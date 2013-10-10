function escapeHtml(unsafe) {
    return unsafe
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
}

function numericComparator(a, b) {
    return a - b;
}

function ParseView(jcontainer) {
    this.jcontainer = jcontainer;
    this.tokens = [];
    this.blocks = [];
    this.selected_index = null;
    this.setMode('join');
    this.undo_stack = [];
    this.redo_stack = [];
    this.on_update = null;
}

ParseView.prototype._generateHtml = function() {
    this.jcontainer.addClass('parseview');

    var html = '<div class="tokens">';
    for (var i = 0; i < this.tokens.length; i++) {
        var token = this.tokens[i];
        if (!token.no_space) {
            html += ' ';
        }
        html += '<span class="token" data-id="' + i + '">'
            + escapeHtml(token.orth) + '</span>';
    }
    html += '</div>';
    html += '<hr>';
    html += '<div class="blocks">';
    for (var i = 0; i < this.tokens.length; i++) {
        var token = this.tokens[i];
        html += '<div class="block" data-id="' + i + '">'
            + '<span class="left"></span>'
            + '<span class="middle">' + escapeHtml(token.orth) + '</span>'
            + '<span class="right"></span>'
            + '</div> ';
    }
    html += '</div>';
    html += '<hr>';
    html += '<div class="tree">';
    html += '</div>';
    this.jcontainer.html(html);
}

ParseView.prototype._jtoken = function(index) {
    return $('.token[data-id=' + index + ']', this.jcontainer);
}

ParseView.prototype._jblock = function(index) {
    return $('.block[data-id=' + index + ']', this.jcontainer);
}

ParseView.prototype._jnode = function(index) {
    return $('.node[data-id=' + index + ']', this.jcontainer);
}

ParseView.prototype._generateBlocks = function() {
    this.blocks = []
    for (var index = 0; index < this.tokens.length; index++) {
        var token = this.tokens[index];
        var block = {
            num: index,
            token: token,
            disabled: token.interp
        }
        this.blocks[index] = block;
        var self = this;
        function on_click(event) {
            self._onClick(this, event);
        }
        function on_hover(event) {
            self._onHover(this, event);
        }
        function on_unhover(event) {
            self._onUnhover(this, event);
        }
        this._jtoken(index).click(on_click).hover(on_hover, on_unhover);
        this._jblock(index).click(on_click).hover(on_hover, on_unhover);
    }
}

ParseView.prototype.init = function(tokens) {
    this.tokens = tokens;
    this._generateHtml();
    this._generateBlocks();
    this._updateBlocks();

    var self = this;
    $(document).keyup(function(e) { self._onKey(e); });
    $(document).click(function(e) { self._onBodyClick(e); });
}

ParseView.prototype._onClick = function(domnode, event) {
    event.preventDefault();
    event.stopPropagation();
    var jnode = $(domnode);
    var index = parseInt(jnode.attr('data-id'));
    var block = this.blocks[index];
    if (block.disabled) {
        return;
    }
    if (this.mode == 'join') {
        if (this.selected_index != null) {
            if (index == this.selected_index) {
                this._clearSelection();
            } else {
                this._setParent(index, this.selected_index);
            }
        } else {
            this.selected_index = index;
            this._updateSelection();
        }
    } else if (this.mode == 'split') {
        if (jnode.hasClass('token')) {
            var split_index = index;
            while (true) {
                var parent = this.blocks[split_index].parent;
                if (parent == null) {
                    break;
                }
                this._setParent(split_index, null);
                split_index = parent;
            }
            return;
        }
        if (block.children.length == 0) {
            return;
        }
        this._setParent(block.children[block.children.length - 1], null);
    }
}

ParseView.prototype._onKey = function(event) {
    if (event.keyCode == 27 && this.selected_index != null) {
        this._clearSelection();
    }
}

ParseView.prototype._onBodyClick = function(event) {
    if (this.selected_index != null) {
        this._clearSelection();
    }
}

ParseView.prototype.__findSubtree = function(index, array) {
    array.push(index);
    var block = this.blocks[index];
    for (var i = 0; i < block.children.length; i++) {
        var child_index = block.children[i];
        this.__findSubtree(child_index, array);
    }
    for (var i = 0; i < block.auto_children.length; i++) {
        var child_index = block.auto_children[i];
        this.__findSubtree(child_index, array);
    }
}

ParseView.prototype._findSubtree = function(index) {
    var ret = [];
    this.__findSubtree(index, ret);
    ret.sort(numericComparator);
    return ret;
}

ParseView.prototype._setParent = function(index, new_parent) {
    // Check for circular references.
    var subtree = this._findSubtree(index);
    if (subtree.indexOf(new_parent) != -1) {
        alert("Operacja stworzyłaby cykl. To jest bez sensu.");
        this._clearSelection();
        return;
    }

    var block = this.blocks[index];
    this.undo_stack.push([index, block.parent, new_parent]);
    this.redo_stack = [];
    block.parent = new_parent;
    this._updateBlocks();
    this._cleanRedo(index);
}

ParseView.prototype._cleanRedo = function(index) {
    for (var i = 0; i < this.redo_stack.length; i++) {
        if (this.redo_stack[i][0] == index) {
            this.redo_stack = this.redo_stack.slice(0, i);
        }
    }
}

ParseView.prototype.canUndo = function() {
    return this.undo_stack.length > 0;
}

ParseView.prototype.undo = function() {
    var undo = this.undo_stack.pop();
    var index = undo[0];
    var block = this.blocks[index];
    var old_parent = undo[1];
    var new_parent = undo[2];
    block.parent = old_parent;
    this.redo_stack.push(undo);
    this._updateBlocks();
}

ParseView.prototype.canRedo = function() {
    return this.redo_stack.length > 0;
}

ParseView.prototype.redo = function() {
    var redo = this.redo_stack.pop();
    var index = redo[0];
    var block = this.blocks[index];
    var old_parent = redo[1];
    var new_parent = redo[2];
    block.parent = new_parent;
    this.undo_stack.push(redo);
    this._updateBlocks();
}

ParseView.prototype.registerUpdateHandler = function(handler) {
    this.on_update = handler;
}

ParseView.prototype._updateTop = function(index) {
    var block = this.blocks[index];
    if (block.parent == null) {
        block.top = null;
        var subtree = this._findSubtree(index);
        for (var i = 0; i < subtree.length; i++) {
            var node_index = parseInt(subtree[i]);
            var node = this.blocks[node_index];
            node.top = index;
            var jtoken = this._jtoken(node_index);
            jtoken.attr('data-top', index);
        }
    }
}

ParseView.prototype._updateBlock = function(index) {
    var block = this.blocks[index];
    var jblock = this._jblock(index)
    if (block.parent == null) {
        jblock.removeClass('block-hidden');
        var jleft = $('.left', jblock);
        var jright = $('.right', jblock);
        var subtree = this._findSubtree(index);
        var left_orths = '';
        var right_orths = '';
        for (var i = 0; i < subtree.length; i++) {
            var node_index = parseInt(subtree[i]);
            var node = this.blocks[node_index];
            if (node_index < index) {
                if (!node.token.no_space) {
                    left_orths += ' ';
                }
                left_orths += escapeHtml(node.token.orth);
            } else if (node_index > index) {
                if (!node.token.no_space) {
                    right_orths += ' ';
                }
                right_orths += escapeHtml(node.token.orth);
            }
        }
        jleft.html(left_orths);
        jright.html(right_orths);
    } else {
        jblock.addClass('block-hidden');
    }
}

ParseView.prototype._updateBlocks = function() {
    for (var index = 0; index < this.blocks.length; index++) {
        var block = this.blocks[index];
        block.children = [];
        block.auto_children = [];
        block.top = null;
    }
    for (var index = 0; index < this.blocks.length; index++) {
        var block = this.blocks[index];
        if (block.parent != null && !block.disabled) {
            this.blocks[block.parent].children.push(index);
        }
    }
    for (var index = 0; index < this.blocks.length; index++) {
        this._updateTop(index);
    }

    // Hide interpunction.
    for (var index = 0; index < this.blocks.length; index++) {
        if (index == 0 || index == this.blocks.length - 1)
            continue;
        var block = this.blocks[index];
        if (!block.disabled)
            continue;
        var prev_block = this.blocks[index - 1];
        var next_block = this.blocks[index + 1];
        if (prev_block.top != null && prev_block.top == next_block.top) {
            block.parent = prev_block.top;
            this.blocks[block.parent].auto_children.push(index);
        } else {
            block.parent = null;
        }
    }

    for (var index = 0; index < this.blocks.length; index++) {
        this._updateBlock(index);
    }
    this._clearSelection();
    this._updateTree();
    if (this.on_update) {
        this.on_update(this);
    }
}

ParseView.prototype._updateSelection = function() {
    $('.blocks .block', this.jcontainer).removeClass('selected');
    $('.tokens .token', this.jcontainer)
        .removeClass('selected')
        .removeClass('selected_block');
    $('.tree .node', this.jcontainer).removeClass('selected');
    if (this.selected_index != null) {
        this._jblock(this.selected_index).addClass('selected');
        this._jtoken(this.selected_index).addClass('selected');
        this._jnode(this.selected_index).addClass('selected');
        $('.tokens .token[data-top="' + this.selected_index + '"]',
                this.jcontainer).addClass('selected_block');
    }
}

ParseView.prototype._clearSelection = function() {
    this.selected_index = null;
    this._updateSelection();
}

ParseView.prototype.__updateDepths = function(index, depth) {
    var block = this.blocks[index];
    block.depth = depth;
    var max = depth;
    for (var i = 0; i < block.children.length; i++) {
        var sub_depth = this.__updateDepths(block.children[i], depth + 1);
        if (sub_depth > max) {
            max = sub_depth;
        }
    }
    return max;
}

ParseView.prototype._updateDepths = function() {
    var max_depth = 0;
    for (var i = 0; i < this.blocks.length; i++) {
        if (this.blocks[i].parent == null) {
            var depth = this.__updateDepths(i, 0);
            if (depth > max_depth) {
                max_depth = depth;
            }
        }
    }
    for (var i = 0; i < this.blocks.length; i++) {
        var block = this.blocks[i];
        if (!block.disabled) {
            continue;
        }
        var prev_block = this.blocks[i - 1];
        var next_block = this.blocks[i + 1];
        var prev_depth = prev_block ? prev_block.depth : 0;
        var next_depth = next_block ? next_block.depth : 0;
        block.depth = Math.max(prev_depth, next_depth);
    }
    return max_depth;
}

ParseView.prototype._drawLine = function(div1, div2, thickness) {

    function getOffset( el ) { // return element top, left, width, height
        var _x = 0;
        var _y = 0;
        var _w = el.offsetWidth|0;
        var _h = el.offsetHeight|0;
        while( el && el.tagName != 'DIV' && !isNaN( el.offsetLeft ) && !isNaN( el.offsetTop ) ) {
            console.log(el);
            _x += el.offsetLeft - el.scrollLeft;
            _y += el.offsetTop - el.scrollTop;
            el = el.offsetParent;
        }
        return { top: _y, left: _x, width: _w, height: _h };
    }

    var off1 = getOffset(div1);
    console.log(off1);
    var off2 = getOffset(div2);
    console.log(off2);
    // bottom right
    var x1 = off1.left + off1.width / 2;
    var y1 = off1.top + off1.height;
    // top right
    var x2 = off2.left + off2.width / 2;
    var y2 = off2.top;
    // distance
    var length = Math.sqrt(((x2-x1) * (x2-x1)) + ((y2-y1) * (y2-y1)));
    // center
    var cx = ((x1 + x2) / 2) - (length / 2);
    var cy = ((y1 + y2) / 2) - (thickness / 2);
    // angle
    var angle = Math.atan2((y1-y2),(x1-x2))*(180/Math.PI);
    // make hr
    var line = document.createElement('div');
    line.setAttribute('class', 'line');
    line.setAttribute('style', "padding:0px; margin:0px; height:"
            + thickness + "px; line-height:1px; position:absolute; left:" + cx
            + "px; top:" + cy + "px; width:" + length
            + "px; -moz-transform:rotate(" + angle
            + "deg); -webkit-transform:rotate(" + angle
            + "deg); -o-transform:rotate(" + angle
            + "deg); -ms-transform:rotate(" + angle
            + "deg); transform:rotate(" + angle + "deg);");
    return line;
}

ParseView.prototype._updateTree = function() {
    var self = this;
    function on_click(event) {
        self._onClick(this, event);
    }
    function on_hover(event) {
        self._onHover(this, event);
    }
    function on_unhover(event) {
        self._onUnhover(this, event);
    }

    var max_depth = this._updateDepths();
    var table = document.createElement('table');
    var spans = [];
    for (var d = 0; d <= max_depth; d++) {
        var row = document.createElement('tr');
        for (var index = 0; index < this.blocks.length; index++) {
            var block = this.blocks[index];
            var td = document.createElement('td');
            if (block.depth == d) {
                var span = document.createElement('span');
                span.setAttribute('data-id', index);
                span.setAttribute('class', 'node');
                $(span).click(on_click).hover(on_hover, on_unhover);
                spans[index] = span;
                var text = document.createTextNode(block.token.orth);
                span.appendChild(text);
                td.appendChild(span);
            }
            row.appendChild(td);
        }
        table.appendChild(row);
    }

    var jtree = $('.tree', this.jcontainer);
    jtree.empty();
    jtree.append(table);
    console.log(table);

    var lines = [];
    for (var index = 0; index < this.blocks.length; index++) {
        var block = this.blocks[index];
        if (block.parent != null && !block.disabled) {
            var line = this._drawLine(spans[block.parent], spans[index], 3);
            lines.push(line);
        }
    }
    jtree.append(lines);
}

ParseView.prototype.setMode = function(mode) {
    this.mode = mode;
    this.jcontainer.removeClass('mode-join');
    this.jcontainer.removeClass('mode-split');
    this.jcontainer.addClass('mode-' + this.mode);
    this._clearSelection();
}

ParseView.prototype._onHover = function(domnode, event) {
    var jnode = $(domnode);
    var index = parseInt(jnode.attr('data-id'));
    var block = this.blocks[index];
    if (block.disabled) {
        return;
    }
    if (this.mode == 'split') {
        if (jnode.hasClass('token') && block.parent != null) {
            var split_index = index;
            while (split_index != null) {
                this._jblock(split_index).addClass('hover-split-preview');
                split_index = this.blocks[split_index].parent;
            }
        } else if (jnode.hasClass('block') && block.children.length > 0) {
            var split_index = block.children[block.children.length - 1];
            this._jblock(split_index).addClass('hover-split-preview');
        } /*else if (jnode.hasClass('node') && block.parent != null) {
            this._jblock(index).addClass('hover-split-preview');
        }*/

    }
    var subtree = this._findSubtree(index);
    for (var i = 0; i < subtree.length; i++) {
        this._jtoken(subtree[i]).addClass('hover-subtree');
    }
    this._jtoken(index).addClass('hover');
    if (block.parent != null) {
        this._jtoken(block.parent).addClass('hover-parent');
    }
}

ParseView.prototype._onUnhover = function(domnode, event) {
    $('.token.hover-subtree', this.jcontainer)
        .removeClass('hover-subtree hover');
    $('.token.hover-parent', this.jcontainer)
        .removeClass('hover-parent');
    $('.block.hover-split-preview', this.jcontainer)
        .removeClass('hover-split-preview');
}

