function AppCacheController(progress) {
    this.progress = progress;
    this.oncomplete = null;
    this.onerror = null;
}

AppCacheController.prototype._fire = function(handler, e) {
    if (handler) {
        handler(e);
    }
}

AppCacheController.prototype.init = function() {
    var self = this;
    var update_ready = false;

    this.progress.setUnknown();

    var appCache = window.applicationCache;
    if (!appCache) {
        console.log("AppCache not supported");
        this._fire(this.onerror, "notsupported");
        return;
    }

    if (appCache.status == appCache.UNCACHED) {
        console.log("Page not cached");
        this._fire(this.onerror, "notcached");
        return;
    }

    function onUpdateReady(e) {
        update_ready = true;
        location.reload();
    }

    function handleCacheEvent(e) {
        console.log(e);
    }

    function onError(e) {
        self.progress.failed("Błąd podczas pobierania zadań");
        self._fire(self.onerror, e);
    };

    function onObsolete(e) {
        console.log("Cache is obsolete");
        location.reload();
    };

    function onNoUpdate(e) {
        self.progress.done();
        self._fire(self.oncomplete, e);
    }

    function onProgress(e) {
        self.progress.setProgress(e.loaded, e.total);
    }

    function onCached(e) {
        onNoUpdate(e);
    }

    // Fired after the first cache of the manifest.
    appCache.addEventListener('cached', onCached, false);

    // Checking for an update. Always the first event fired in the sequence.
    appCache.addEventListener('checking', handleCacheEvent, false);

    // An update was found. The browser is fetching resources.
    appCache.addEventListener('downloading', handleCacheEvent, false);

    // The manifest returns 404 or 410, the download failed,
    // or the manifest changed while the download was in progress.
    appCache.addEventListener('error', onError, false);

    // Fired after the first download of the manifest.
    appCache.addEventListener('noupdate', onNoUpdate, false);

    // Fired if the manifest file returns a 404 or 410.
    // This results in the application cache being deleted.
    appCache.addEventListener('obsolete', onObsolete, false);

    // Fired for each resource listed in the manifest as it is being fetched.
    appCache.addEventListener('progress', onProgress, false);

    // Fired when the manifest resources have been newly redownloaded.
    appCache.addEventListener('updateready', onUpdateReady, false);
}

