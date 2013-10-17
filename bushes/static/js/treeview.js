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

function TreeView(jcontainer) {
    this.jcontainer = jcontainer;
    this.tokens = [];
    this.parents = [];
    this.blocks = [];
}

TreeView.prototype._generateHtml = function() {
    this.jcontainer.addClass('treeview');

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
    html += '<div class="tree">';
    html += '<div class="root node-container"></div>';
    html += '</div>';
    this.jcontainer.html(html);
}

TreeView.prototype._jtoken = function(index) {
    return $('.token[data-id=' + index + ']', this.jcontainer);
}

TreeView.prototype._jnode = function(tree, index) {
    return $('.node[data-tree=' + tree + '][data-id=' + index + ']', this.jcontainer);
}

TreeView.prototype._generateBlocks = function() {
    this.blocks = []
    for (var index = 0; index < this.tokens.length; index++) {
        var token = this.tokens[index];
        var block = {
            num: index,
            token: token,
            interp: token.interp,
            agreement: true,
            left_noninterp: null,
            right_noninterp: null,
        }
        this.blocks[index] = block;
    }

    if (this.parents.length > 0) {
        for (var index = 0; index < this.tokens.length; index++) {
            var block = this.blocks[index];
            var a_parent = this.parents[0][index];
            for (var t = 1; t < this.parents.length; t++) {
                if (this.parents[t][index] != a_parent) {
                    block.agreement = false;
                    this._jtoken(index).addClass('disagreement');
                    break;
                }
            }
        }
    }

    for (var index = 0; index < this.tokens.length; index++) {
        var block = this.blocks[index];
        for (var i = index; i >= 0; i--) {
            if (!this.blocks[i].interp) {
                block.left_noninterp = i;
            }
        }
        for (var i = index; i < this.blocks.length; i++) {
            if (!this.blocks[i].interp) {
                block.right_noninterp = i;
            }
        }
    }
}

TreeView.prototype.init = function(tokens, parents, tree_headers) {
    this.tokens = tokens;
    this.parents = parents;
    this.tree_headers = tree_headers;
    this._generateHtml();
    this._generateBlocks();
    this._updateChildren();
    this._updateTrees();
}

TreeView.prototype.__findSubtree = function(tree, index, array) {
    array.push(index);
    var block = this.blocks[index];
    var children = block.children[tree];
    for (var i = 0; i < children.length; i++) {
        var child_index = children[i];
        this.__findSubtree(tree, child_index, array);
    }
}

TreeView.prototype._findSubtree = function(tree, index) {
    var ret = [];
    this.__findSubtree(tree, index, ret);
    ret.sort(numericComparator);
    return ret;
}

TreeView.prototype._updateChildren = function() {
    for (var index = 0; index < this.blocks.length; index++) {
        var block = this.blocks[index];
        block.children = []
        block.hidden = []
    }
    for (var t = 0; t < this.parents.length; t++) {
        for (var index = 0; index < this.blocks.length; index++) {
            this.blocks[index].children[t] = [];
        }
    }

    for (var t = 0; t < this.parents.length; t++) {
        var parents = this.parents[t];
        for (var index = 0; index < this.blocks.length; index++) {
            var block = this.blocks[index];
            var parent = this.parents[t][index];
            if (parent != null) {
                this.blocks[parent].children[t].push(index);
            }
        }
        for (var index = 0; index < this.blocks.length; index++) {
            var block = this.blocks[index];
            block.hidden[t] = block.interp && parents[index] == null
                && !block.children[t].length;
        }
    }
}

TreeView.prototype._drawLine = function(div1, div2, thickness) {
    function getOffset( el ) { // return element top, left, width, height
        var _x = 0;
        var _y = 0;
        var _w = el.offsetWidth|0;
        var _h = el.offsetHeight|0;
        while( el && !$(el).hasClass('tree') && !isNaN( el.offsetLeft ) && !isNaN( el.offsetTop ) ) {
            console.log('el: ');
            console.log(el);
            _x += el.offsetLeft - el.scrollLeft;
            _y += el.offsetTop - el.scrollTop;
            el = el.offsetParent;
            console.log('parent: ' + el);
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

TreeView.prototype._drawTreeBranch = function(tree, index, parent_node, parent_container) {
    var self = this;
    function on_hover(event) {
        self._onHover(this, event);
    }
    function on_unhover(event) {
        self._onUnhover(this, event);
    }

    var block = this.blocks[index];
    var domcontainer = document.createElement('div');
    if (parent_node) {
        domcontainer.setAttribute('class', 'node-container has-parent');
    } else {
        domcontainer.setAttribute('class', 'node-container');
    }
    var domnode = document.createElement('div');
    var cls = 'node';
    if (!block.agreement) {
        cls += ' disagreement';
    }
    domnode.setAttribute('class', cls);
    domnode.setAttribute('data-id', index);
    domnode.setAttribute('data-tree', tree);
    $(domnode).hover(on_hover, on_unhover);
    var domtext = document.createTextNode(block.token.orth);
    domnode.appendChild(domtext);
    domcontainer.appendChild(domnode);
    domcontainer.appendChild(document.createElement('br'));
    parent_container.appendChild(domcontainer);

    this.tree_domnodes[tree][index] = domnode;

    var children = block.children[tree];
    for (var i = 0; i < children.length; i++) {
        var child_index = children[i];
        this._drawTreeBranch(tree, child_index, domnode, domcontainer);
    }

    return domcontainer;
}

TreeView.prototype._updateTrees = function() {
    var jtree = $('.tree', this.jcontainer);
    jtree.empty();
    this.tree_domnodes = [];
    for (var t = 0; t < this.parents.length; t++) {
        var jroot = $('<div class="root node-container"></div>');
        var domroot = jroot[0];
        var parents = this.parents[t];
        this.tree_domnodes[t] = []
        for (var index = 0; index < this.blocks.length; index++) {
            var block = this.blocks[index];
            var parent = parents[index];
            if (parent == null && !block.hidden[t]) {
                this._drawTreeBranch(t, index, null, domroot);
            }
        }
        var header = this.tree_headers[t];
        if (header) {
            jtree.append($('<div class="tree-header"></div>').html(header));
        }
        jtree.append(jroot);
        for (var index = 0; index < this.blocks.length; index++) {
            var block = this.blocks[index];
            var parent = parents[index];
            if (parent != null && this.tree_domnodes[t][index] !== undefined) {
                var domline = this._drawLine(
                        this.tree_domnodes[t][parent],
                        this.tree_domnodes[t][index],
                        3);
                domroot.appendChild(domline);
            }
        }
    }
}

TreeView.prototype._onHover = function(domnode, event) {
    var jnode = $(domnode);
    var index = parseInt(jnode.attr('data-id'));
    var tree = parseInt(jnode.attr('data-tree'));
    var block = this.blocks[index];
    var subtree = this._findSubtree(tree, index);
    for (var i = 0; i < subtree.length; i++) {
        this._jtoken(subtree[i]).addClass('hover-subtree');
    }
    this._jtoken(index).addClass('hover');
    var parent = this.parents[tree][index];
    if (parent != null) {
        this._jtoken(parent).addClass('hover-parent');
    }
}

TreeView.prototype._onUnhover = function(domnode, event) {
    $('.token.hover-subtree', this.jcontainer)
        .removeClass('hover-subtree hover');
    $('.token.hover-parent', this.jcontainer)
        .removeClass('hover-parent');
}
