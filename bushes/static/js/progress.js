function Progress(jcontainer, min, max) {
    this.jcontainer = jcontainer;
    this.min = min;
    this.max = max;
    this.init();
}

Progress.prototype.init = function() {
    var self = this;
    if (this.min == 0) {
        this.jcontainer.attr('timerid',
                setTimeout(function() { self.jcontainer.css('visibility', 'visible'); }, 1000));
    }
}

Progress.prototype._setWidth = function(progress, of) {
    var percent = ((this.max - this.min) * progress / of) + this.min;
    $('.progress-bar', this.jcontainer).width(percent + '%');
}

Progress.prototype.setUnknown = function() {
    this._setWidth(5, 100);
    $('.progress', this.jcontainer).addClass('actice progress-striped');
}

Progress.prototype.setProgress = function(progress, of) {
    var self = this;
    this._setWidth(progress, of);
    $('.progress', this.jcontainer).removeClass('actice progress-striped');
}

Progress.prototype.done = function() {
    var self = this;
    this.setProgress(1, 1);
    if (this.max == 100) {
        clearTimeout(this.jcontainer.attr('timerid'));
        setTimeout(function() { self.jcontainer.css('visibility', 'hidden'); }, 500);
    }
}

Progress.prototype.failed = function(message) {
    this.jcontainer.html('<div class="alert alert-danger">' + message + '</div>');
}
