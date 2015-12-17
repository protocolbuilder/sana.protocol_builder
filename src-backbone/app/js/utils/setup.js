var Config = require('utils/config');


module.exports = {

    load_config: function() {
        global.Config = Config;
        global.DEBUG = Config.DEBUG;
    },

    load_libs: function() {
        // Loads libraries into global namespace
        global.$ = global.jQuery = require('jquery');
        global._ = require('underscore');
        global.Backbone = require('backbone');
        global.Backbone.$ = $;
        global.Marionette = require('backbone.marionette');

        global.Handlebars = require("hbsfy/runtime");
        this._setup_i18n();
        global.HandlebarsIntl = require('handlebars-intl');
        HandlebarsIntl.registerWith(Handlebars);

        require('bootstrap');
    },

    _setup_i18n: function() {
        var is_locales_supported = require('intl-locales-supported');

        if (global.Intl) {
            // Determine if the built-in `Intl` has the locale data we need.
            if (!is_locales_supported(Config.LOCALES_SUPPORTED)) {
                // `Intl` exists, but it doesn't have the data we need, so load the
                // polyfill and replace the constructors with need with the polyfill's.
                require('intl');
                Intl.NumberFormat   = IntlPolyfill.NumberFormat;
                Intl.DateTimeFormat = IntlPolyfill.DateTimeFormat;
            }
        } else {
            // No `Intl`, so use and load the polyfill.
            global.Intl = require('intl');
        }
    },

};
