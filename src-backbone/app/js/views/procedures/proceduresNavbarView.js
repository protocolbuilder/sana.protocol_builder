const EventKeys = require('utils/eventKeys');
const App = require('utils/sanaAppInstance');


module.exports = Marionette.LayoutView.extend({

    template: require('templates/procedures/proceduresNavbarView'),
    tagName: 'div',
    className: 'container-fluid spb-container',

    regions: {
        'languageSelector': 'div.navbar-right.language-selector',
        'rightNavbar': 'div.navbar-right.content',
    },

    behaviors: {
        RightNavbarBehavior: {},
    },

    onAttach: function() {
        const welcomeMessage = i18n.t('Hello username', {
            username: App().session.user.get('first_name')
        });

        // Do this after View is shown so that rootLayoutView can find
        // p.navbar-text inside this View
        this.triggerMethod(EventKeys.UPDATE_NAVBAR_TEXT, welcomeMessage);
    },

});
